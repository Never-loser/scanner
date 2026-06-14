import telebot
from telebot import types
import re
import os
from dotenv import load_dotenv

from database import get_random_approved_ip, count_approved_ips_by_user, add_clean_ip, approve_ip, reject_ip, get_pending_ips
from ip_parser import replace_ip_in_config

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables! Please set it in .env file.")

if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set in environment variables! Please set it in .env file.")

try:
    ADMIN_ID = int(ADMIN_ID)
except ValueError:
    raise ValueError("ADMIN_ID must be a valid integer (your Telegram user ID).")

bot = telebot.TeleBot(BOT_TOKEN)

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📤 ارسال کانفیگ")
    markup.add("📥 ارسال آیپی تمیز")
    markup.add("📊 آمار من")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "سلام! به ربات آیپی تمیز خوش اومدی.\nیکی از گزینه‌ها رو انتخاب کن:",
        reply_markup=main_menu()
    )



@bot.message_handler(func=lambda m: m.text == "📤 ارسال کانفیگ")
def ask_for_config(message):
    msg = bot.send_message(message.chat.id, "کانفیگ vless/vmess/trojan خودت رو بفرست:")
    bot.register_next_step_handler(msg, process_config)

def process_config(message):
    original_config = message.text.strip()
    if not original_config.startswith(("vless://", "trojan://")):
        bot.send_message(message.chat.id, "❌ کانفیگ معتبر نیست.")
        return

    clean_ip = get_random_approved_ip()
    if not clean_ip:
        bot.send_message(message.chat.id, "❌ هیچ آیپی تأیید شده‌ای وجود نداره.")
        return

    new_config = replace_ip_in_config(original_config, clean_ip)
    bot.send_message(
        message.chat.id,
        f"✅ کانفیگ جدید:\n\n`{new_config}`",
        parse_mode="Markdown"
    )

# ===================== دکمه ارسال آیپی تمیز =====================
@bot.message_handler(func=lambda m: m.text == "📥 ارسال آیپی تمیز")
def ask_for_ip(message):
    msg = bot.send_message(
        message.chat.id,
        "آیپی تمیز کلودفلر رو بفرست (مثال: 104.21.10.5):"
    )
    bot.register_next_step_handler(msg, process_ip_submission)




def is_valid_ip(ip: str) -> bool:
    # IPv4
    ipv4 = r'^(\d{1,3}\.){3}\d{1,3}$'
    # IPv6
    ipv6 = r'^[0-9a-fA-F:]+$'

    if re.match(ipv4, ip):
        parts = ip.split('.')
        return all(0 <= int(p) <= 255 for p in parts)
    if re.match(ipv6, ip) and ':' in ip:
        return True
    return False


def process_ip_submission(message):

    print("[DEBUG] process_ip_submission called")
    print(f"[DEBUG] message.text = {message.text}")
    ip = message.text.strip()
    user_id = message.from_user.id
    username = message.from_user.username or "ناشناس"

    if not is_valid_ip(ip):
        bot.send_message(message.chat.id, "❌ آیپی معتبر نیست.\nمثال IPv4: 104.21.10.5\nمثال IPv6: 2606:4700::1111")
        return

    added = add_clean_ip(ip=ip, submitted_by=user_id)
    if not added:
        bot.send_message(message.chat.id, "⚠️ این آیپی قبلاً توسط کسی ثبت شده.")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تأیید", callback_data=f"approve|{ip}|{user_id}"),
        types.InlineKeyboardButton("❌ رد", callback_data=f"reject|{ip}|{user_id}")
    )
    try:
        bot.send_message(
            ADMIN_ID,
            f"🔔 آیپی جدید برای تأیید:\n{ip}\nاز کاربر: @{username} (ID: {user_id})",
            reply_markup=markup
        )
        bot.send_message(message.chat.id, "✅ آیپیت ارسال شد و منتظر تأیید ادمینه.")
    except Exception as e:
        print(f"[ERROR] {e}")
        bot.send_message(message.chat.id, f"❌ خطا در ارسال به ادمین: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("approve|") or call.data.startswith("reject|"))
def handle_admin_decision(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ دسترسی نداری!")
        return

    parts = call.data.split("|")  # ← | به جای _ برای جدا کردن
    action = parts[0]
    ip = parts[1]
    user_id = int(parts[2])

    if action == "approve":
        approve_ip(ip=ip, admin_id=ADMIN_ID)
        bot.edit_message_text(f"✅ آیپی {ip} تأیید شد.", call.message.chat.id, call.message.message_id)
        bot.send_message(user_id, f"🎉 آیپی {ip} توسط ادمین تأیید شد! ممنون از مشارکتت.")
    else:
        reject_ip(ip=ip)
        bot.edit_message_text(f"❌ آیپی {ip} رد شد.", call.message.chat.id, call.message.message_id)
        bot.send_message(user_id, f"❌ متأسفانه آیپی {ip} تأیید نشد.")

    bot.answer_callback_query(call.id)
# ===================== آمار =====================
@bot.message_handler(func=lambda m: m.text == "📊 آمار من")
def stats(message):
    count = count_approved_ips_by_user(message.from_user.id)
    bot.send_message(message.chat.id, f"📊 تعداد آیپی‌های تأیید شده توسط تو: {count}")

print("ربات در حال اجراست...")
bot.infinity_polling()