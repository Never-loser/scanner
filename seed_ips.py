import sqlite3

DB_NAME = "clean_ips.db"

# لیست آیپی‌هایی که فرستادی (فقط IP ها)
raw_data = """
108.162.194.35
188.114.97.108
198.41.205.53
172.67.158.196
103.21.244.127
173.245.59.155
104.25.147.92
104.17.225.26
172.65.191.69
188.114.98.147
103.21.244.96
162.159.137.4
104.25.202.135
162.159.60.150
104.27.196.223
104.25.173.82
104.16.145.217
188.114.96.103
104.25.61.133
172.67.173.31
173.245.58.159
103.21.244.123
104.25.93.13
104.27.28.165
104.19.52.219
188.114.97.6
""".strip().splitlines()


def seed_initial_ips():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    inserted = 0
    skipped = 0

    for ip in raw_data:
        ip = ip.strip()
        if not ip:
            continue

        try:
            cursor.execute("""
                INSERT INTO clean_ips (ip, submitted_by, status, created_at)
                VALUES (?, ?, 'approved', datetime('now'))
            """, (ip, 0))  # submitted_by = 0 یعنی آیپی اولیه
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    conn.close()

    print(f"✅ {inserted} آیپی با موفقیت به عنوان approved اضافه شد.")
    print(f"⚠️  {skipped} آیپی تکراری بود و اضافه نشد.")


if __name__ == "__main__":
    seed_initial_ips()