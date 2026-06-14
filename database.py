import sqlite3
from typing import List, Optional

DB_NAME = "clean_ips.db"


def create_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clean_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL UNIQUE,
            submitted_by INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            approved_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("جدول clean_ips ساخته شد (نسخه ساده بدون استان).")


# ===================== توابع =====================

def add_clean_ip(ip: str, submitted_by: int) -> bool:
    """اضافه کردن آیپی جدید"""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO clean_ips (ip, submitted_by, status)
            VALUES (?, ?, 'pending')
        """, (ip, submitted_by))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_pending_ips() -> List[dict]:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clean_ips WHERE status = 'pending' ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def approve_ip(ip: str, admin_id: int) -> bool:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clean_ips 
        SET status = 'approved', approved_by = ? 
        WHERE ip = ? AND status = 'pending'
    """, (admin_id, ip))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def reject_ip(ip: str) -> bool:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clean_ips 
        SET status = 'rejected' 
        WHERE ip = ? AND status = 'pending'
    """, (ip,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def get_random_approved_ip() -> Optional[str]:
    """انتخاب تصادفی یک آیپی تأیید شده (برای جایگزینی در کانفیگ)"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ip FROM clean_ips 
        WHERE status = 'approved' 
        ORDER BY RANDOM() 
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    return row['ip'] if row else None


def get_approved_ips(limit: int = 20) -> List[str]:
    """دریافت چند تا آیپی تأیید شده (برای ارسال چند کانفیگ)"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ip FROM clean_ips 
        WHERE status = 'approved' 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [row['ip'] for row in rows]


def get_submitter_of_ip(ip: str) -> Optional[int]:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT submitted_by FROM clean_ips WHERE ip = ?", (ip,))
    row = cursor.fetchone()
    conn.close()
    return row['submitted_by'] if row else None


def count_approved_ips_by_user(user_id: int) -> int:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as count FROM clean_ips 
        WHERE submitted_by = ? AND status = 'approved'
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row['count'] if row else 0


def get_all_approved_ips(limit: int = 50) -> List[dict]:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ip, status FROM clean_ips 
        WHERE status = 'approved'
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]