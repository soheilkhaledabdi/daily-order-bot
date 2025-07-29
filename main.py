import telebot
from telebot import types
import mysql.connector
from datetime import datetime, date

TOKEN = '8232453331:AAEzooH4tlP0g8skia46OOftpehdtm4xLeY'
ADMINS = [1734062356]
bot = telebot.TeleBot(TOKEN)

db_config = {
    'host': 'localhost',
    'user': '',
    'password': '',
    'database': ''
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    username VARCHAR(255),
    order_text TEXT,
    order_date DATE,
    status ENUM('pending', 'completed', 'paid') DEFAULT 'pending'
)
''')
conn.commit()

def is_admin(user_id):
    return user_id in ADMINS

def today():
    return date.today().isoformat()

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "سلام! برای ثبت سفارش از /order استفاده کن.")

@bot.message_handler(commands=['order'])
def handle_order(message):
    order_text = message.text.replace('/order', '').strip()
    if not order_text:
        bot.reply_to(message, "لطفاً بعد از /order سفارشت رو بنویس.")
        return

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    order_date = today()

    cursor.execute("""
        INSERT INTO orders (user_id, username, order_text, order_date, status)
        VALUES (%s, %s, %s, %s, 'pending')
        ON DUPLICATE KEY UPDATE order_text = VALUES(order_text), status = 'pending'
    """, (user_id, username, order_text, order_date))
    conn.commit()

    bot.reply_to(message, f"✅ سفارش شما برای {order_date} ثبت شد: {order_text}")

@bot.message_handler(commands=['myorder'])
def handle_myorder(message):
    user_id = message.from_user.id
    cursor.execute("SELECT order_text FROM orders WHERE user_id = %s AND order_date = %s", (user_id, today()))
    row = cursor.fetchone()
    if row:
        bot.reply_to(message, f"🍵 سفارش امروز شما: {row[0]}")
    else:
        bot.reply_to(message, "سفارشی برای امروز ثبت نکردید.")

@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    user_id = message.from_user.id
    cursor.execute("DELETE FROM orders WHERE user_id = %s AND order_date = %s", (user_id, today()))
    conn.commit()
    bot.reply_to(message, "❌ سفارش امروز شما حذف شد.")

@bot.message_handler(commands=['summary'])
def handle_summary(message):
    order_date = today()
    cursor.execute("SELECT username, order_text, status FROM orders WHERE order_date = %s", (order_date,))
    rows = cursor.fetchall()

    if not rows:
        bot.reply_to(message, "هیچ سفارشی برای امروز ثبت نشده.")
        return

    summary = f"📋 لیست سفارش‌های امروز ({order_date}):\n\n"
    statuses = set()

    for username, order, status in rows:
        summary += f"• @{username}: {order}\n"
        statuses.add(status)

    markup = types.InlineKeyboardMarkup()

    if statuses == {'pending'}:
        markup.add(types.InlineKeyboardButton("✔️ سفارش‌ها تکمیل شده", callback_data=f"status:{order_date}:completed"))
        markup.add(types.InlineKeyboardButton("💰 کامل پرداخت شده", callback_data=f"status:{order_date}:paid"))
    elif statuses == {'completed'}:
        markup.add(types.InlineKeyboardButton("💰 کامل پرداخت شده", callback_data=f"status:{order_date}:paid"))
    elif statuses == {'paid'}:
        markup = None

    bot.send_message(message.chat.id, summary, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('status:'))
def handle_status_change(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "⛔ فقط ادمین می‌تونه این کار رو انجام بده.")
        return

    _, date_str, new_status = call.data.split(':')
    if new_status not in ['pending', 'completed', 'paid']:
        bot.answer_callback_query(call.id, "وضعیت نامعتبر")
        return

    cursor.execute("UPDATE orders SET status = %s WHERE order_date = %s", (new_status, date_str))
    conn.commit()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, f"✅ وضعیت سفارش‌های {date_str} به '{new_status}' تغییر یافت.")

@bot.message_handler(commands=['history'])
def handle_history(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "⛔ فقط ادمین می‌تونه این دستور رو اجرا کنه.")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "فرمت درست: /history YYYY-MM-DD")
        return

    query_date = args[1]
    cursor.execute("SELECT username, order_text, status FROM orders WHERE order_date = %s", (query_date,))
    rows = cursor.fetchall()

    if not rows:
        bot.reply_to(message, f"سفارشی در تاریخ {query_date} یافت نشد.")
        return

    summary = f"📆 سفارش‌ها در تاریخ {query_date}:\n\n"
    for username, order, status in rows:
        summary += f"• @{username}: {order} ({status})\n"

    bot.reply_to(message, summary)

@bot.message_handler(commands=['setstatus'])
def handle_setstatus(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "⛔ فقط ادمین مجازه وضعیت رو تغییر بده.")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "فرمت درست: /setstatus YYYY-MM-DD status\nمثلاً: /setstatus 2025-07-28 completed")
        return

    query_date = args[1]
    new_status = args[2]
    if new_status not in ['pending', 'completed', 'paid']:
        bot.reply_to(message, "وضعیت باید یکی از موارد زیر باشد: pending | completed | paid")
        return

    cursor.execute("UPDATE orders SET status = %s WHERE order_date = %s", (new_status, query_date))
    conn.commit()
    bot.reply_to(message, f"✅ وضعیت سفارش‌های {query_date} به '{new_status}' تغییر یافت.")

print("🤖 Bot is running...")
bot.infinity_polling()
