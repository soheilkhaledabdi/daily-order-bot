import telebot
from telebot import types
import mysql.connector
from datetime import datetime, date
from config import BOT_TOKEN, ADMIN_IDS, DATABASE_CONFIG, MESSAGES, ORDER_STATUSES

bot = telebot.TeleBot(BOT_TOKEN)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)       
        cursor = conn.cursor()
        return conn, cursor
    except mysql.connector.Error as e:
        print(f"خطا در اتصال به پایگاه داده: {e}")
        return None, None

conn, cursor = get_db_connection()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def today():
    return date.today().isoformat()

def get_persian_status(status):
    return ORDER_STATUSES.get(status, status)

def format_date_persian(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return f"{date_obj.day}/{date_obj.month}/{date_obj.year}"
    except:
        return date_str

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, MESSAGES['welcome'], parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, MESSAGES['help'], parse_mode='Markdown')

@bot.message_handler(commands=['order'])
def handle_order(message):
    if not conn or not cursor:
        bot.reply_to(message, "❌ خطا در اتصال به پایگاه داده. لطفاً دوباره تلاش کنید.")
        return

    order_text = message.text.replace('/order', '').strip()
    if not order_text:
        bot.reply_to(message, "📝 لطفاً بعد از دستور `/order` سفارش خود را بنویسید.\n\nمثال:\n`/order قهوه آمریکانو`")
        return

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    order_date = today()

    try:
        cursor.execute("SELECT id, status FROM orders WHERE user_id = %s AND order_date = %s", (user_id, order_date))
        existing_order = cursor.fetchone()
        
        if existing_order:
            order_id, order_status = existing_order
            
            # بررسی اینکه آیا سفارش قابل تغییر است
            if order_status in ['completed', 'paid']:
                status_persian = get_persian_status(order_status)
                bot.reply_to(message, f"❌ نمی‌توانید سفارش {status_persian} را تغییر دهید.\n\nسفارش‌های تکمیل شده یا پرداخت شده قابل تغییر نیستند.")
                return
            
            cursor.execute("""
                UPDATE orders SET order_text = %s, status = 'pending'
                WHERE user_id = %s AND order_date = %s
            """, (order_text, user_id, order_date))
            response = f"✅ سفارش شما برای امروز ({format_date_persian(order_date)}) به‌روزرسانی شد:\n\n📝 **{order_text}**"
        else:
            cursor.execute("""
                INSERT INTO orders (user_id, username, order_text, order_date, status)
                VALUES (%s, %s, %s, %s, 'pending')
            """, (user_id, username, order_text, order_date))
            response = f"✅ سفارش شما برای امروز ({format_date_persian(order_date)}) ثبت شد:\n\n📝 **{order_text}**"
        
        conn.commit()
        bot.reply_to(message, response, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در ثبت سفارش: {str(e)}")

@bot.message_handler(commands=['myorder'])
def handle_myorder(message):
    if not conn or not cursor:
        bot.reply_to(message, "❌ خطا در اتصال به پایگاه داده.")
        return

    user_id = message.from_user.id
    order_date = today()
    
    try:
        cursor.execute("""
            SELECT order_text, status FROM orders 
            WHERE user_id = %s AND order_date = %s
        """, (user_id, order_date))
        row = cursor.fetchone()
        
        if row:
            order_text, status = row
            status_persian = get_persian_status(status)
            response = f"🍵 **سفارش امروز شما:**\n\n📝 {order_text}\n\n📊 **وضعیت:** {status_persian}"
            bot.reply_to(message, response, parse_mode='Markdown')
        else:
            bot.reply_to(message, "📭 شما هنوز سفارشی برای امروز ثبت نکرده‌اید.\n\nبرای ثبت سفارش از دستور `/order` استفاده کنید.")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در دریافت سفارش: {str(e)}")

@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    if not conn or not cursor:
        bot.reply_to(message, "❌ خطا در اتصال به پایگاه داده.")
        return

    user_id = message.from_user.id
    order_date = today()
    
    try:
        # بررسی وضعیت سفارش قبل از حذف
        cursor.execute("""
            SELECT status FROM orders 
            WHERE user_id = %s AND order_date = %s
        """, (user_id, order_date))
        row = cursor.fetchone()
        
        if not row:
            bot.reply_to(message, "📭 شما سفارشی برای امروز ندارید که حذف شود.")
            return
        
        order_status = row[0]
        
        # بررسی اینکه آیا سفارش قابل لغو است
        if order_status in ['completed', 'paid']:
            status_persian = get_persian_status(order_status)
            bot.reply_to(message, f"❌ نمی‌توانید سفارش {status_persian} را لغو کنید.\n\nسفارش‌های تکمیل شده یا پرداخت شده قابل لغو نیستند.")
            return
        
        # حذف سفارش
        cursor.execute("DELETE FROM orders WHERE user_id = %s AND order_date = %s", (user_id, order_date))
        conn.commit()
        
        if cursor.rowcount > 0:
            bot.reply_to(message, "❌ سفارش امروز شما با موفقیت حذف شد.")
        else:
            bot.reply_to(message, "📭 شما سفارشی برای امروز ندارید که حذف شود.")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در حذف سفارش: {str(e)}")

@bot.message_handler(commands=['summary'])
def handle_summary(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ فقط ادمین‌ها می‌توانند خلاصه سفارش‌ها را مشاهده کنند.")
        return

    if not conn or not cursor:
        bot.reply_to(message, "❌ خطا در اتصال به پایگاه داده.")
        return

    order_date = today()
    
    try:
        cursor.execute("""
            SELECT username, order_text, status 
            FROM orders 
            WHERE order_date = %s 
            ORDER BY created_at ASC
        """, (order_date,))
        rows = cursor.fetchall()

        if not rows:
            bot.reply_to(message, "📭 هیچ سفارشی برای امروز ثبت نشده است.")
            return

        summary = f"📋 **لیست سفارش‌های امروز** ({format_date_persian(order_date)}):\n\n"
        statuses = set()
        total_orders = len(rows)

        for i, (username, order, status) in enumerate(rows, 1):
            status_persian = get_persian_status(status)
            summary += f"{i}. **@{username}:** {order}\n   📊 وضعیت: {status_persian}\n\n"
            statuses.add(status)

        summary += f"📊 **آمار:** {total_orders} سفارش"

        markup = types.InlineKeyboardMarkup()

        if statuses == {'pending'}:
            markup.add(types.InlineKeyboardButton("✅ تکمیل شده", callback_data=f"status:{order_date}:completed"))
            markup.add(types.InlineKeyboardButton("💰 پرداخت شده", callback_data=f"status:{order_date}:paid"))
        elif statuses == {'completed'}:
            markup.add(types.InlineKeyboardButton("💰 پرداخت شده", callback_data=f"status:{order_date}:paid"))
        elif statuses == {'paid'}:
            markup = None

        bot.send_message(message.chat.id, summary, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در دریافت خلاصه: {str(e)}")

@bot.message_handler(commands=['stats'])
def handle_stats(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ فقط ادمین‌ها می‌توانند آمار را مشاهده کنند.")
        return

    if not conn or not cursor:
        bot.reply_to(message, "❌ خطا در اتصال به پایگاه داده.")
        return

    try:
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders WHERE order_date = %s", (today(),))
        today_orders = cursor.fetchone()[0]

        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM orders 
            WHERE order_date = %s 
            GROUP BY status
        """, (today(),))
        status_counts = dict(cursor.fetchall())

        stats_text = f"""
📊 **آمار ربات**

📈 **کلی:**
• کل سفارش‌ها: {total_orders}
• سفارش‌های امروز: {today_orders}

📋 **وضعیت امروز:**
• در انتظار: {status_counts.get('pending', 0)}
• تکمیل شده: {status_counts.get('completed', 0)}
• پرداخت شده: {status_counts.get('paid', 0)}
        """
        bot.reply_to(message, stats_text, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در دریافت آمار: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('status:'))
def handle_status_change(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "⛔ فقط ادمین می‌تواند این کار را انجام دهد.")
        return

    if not conn or not cursor:
        bot.answer_callback_query(call.id, "❌ خطا در اتصال به پایگاه داده.")
        return

    try:
        _, date_str, new_status = call.data.split(':')
        if new_status not in ['pending', 'completed', 'paid']:
            bot.answer_callback_query(call.id, "وضعیت نامعتبر")
            return

        cursor.execute("UPDATE orders SET status = %s WHERE order_date = %s", (new_status, date_str))
        conn.commit()
        
        status_persian = get_persian_status(new_status)
        
        cursor.execute("""
            SELECT username, order_text, status 
            FROM orders 
            WHERE order_date = %s 
            ORDER BY created_at ASC
        """, (date_str,))
        rows = cursor.fetchall()
        
        if rows:
            summary = f"📋 **لیست سفارش‌های {format_date_persian(date_str)}** (وضعیت: {status_persian}):\n\n"
            total_orders = len(rows)
            
            for i, (username, order, status) in enumerate(rows, 1):
                status_persian_item = get_persian_status(status)
                summary += f"{i}. **@{username}:** {order}\n   📊 وضعیت: {status_persian_item}\n\n"
            
            summary += f"📊 **آمار:** {total_orders} سفارش"
            
            statuses = set(status for _, _, status in rows)
            markup = types.InlineKeyboardMarkup()
            
            if statuses == {'pending'}:
                markup.add(types.InlineKeyboardButton("✅ تکمیل شده", callback_data=f"status:{date_str}:completed"))
                markup.add(types.InlineKeyboardButton("💰 پرداخت شده", callback_data=f"status:{date_str}:paid"))
            elif statuses == {'completed'}:
                markup.add(types.InlineKeyboardButton("💰 پرداخت شده", callback_data=f"status:{date_str}:paid"))
            elif statuses == {'paid'}:
                markup = None
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=summary,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"📭 هیچ سفارشی برای {format_date_persian(date_str)} یافت نشد.",
                reply_markup=None
            )
        
        bot.answer_callback_query(call.id, f"✅ وضعیت به '{status_persian}' تغییر یافت")
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ خطا: {str(e)}")

@bot.message_handler(commands=['history'])
def handle_history(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "⛔ فقط ادمین‌ها می‌توانند تاریخچه را مشاهده کنند.")
        return

    if not conn or not cursor:
        bot.reply_to(message, "❌ خطا در اتصال به پایگاه داده.")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "📅 فرمت صحیح: `/history YYYY-MM-DD`\n\nمثال:\n`/history 2024-01-15`")
        return

    query_date = args[1]
    
    try:
        cursor.execute("""
            SELECT username, order_text, status 
            FROM orders 
            WHERE order_date = %s 
            ORDER BY created_at ASC
        """, (query_date,))
        rows = cursor.fetchall()

        if not rows:
            bot.reply_to(message, f"📭 سفارشی در تاریخ {format_date_persian(query_date)} یافت نشد.")
            return

        summary = f"📆 **سفارش‌ها در تاریخ {format_date_persian(query_date)}:**\n\n"
        for i, (username, order, status) in enumerate(rows, 1):
            status_persian = get_persian_status(status)
            summary += f"{i}. **@{username}:** {order}\n   📊 وضعیت: {status_persian}\n\n"

        summary += f"📊 **مجموع:** {len(rows)} سفارش"
        bot.reply_to(message, summary, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در دریافت تاریخچه: {str(e)}")

@bot.message_handler(commands=['setstatus'])
def handle_setstatus(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "⛔ فقط ادمین‌ها می‌توانند وضعیت را تغییر دهند.")
        return

    if not conn or not cursor:
        bot.reply_to(message, "❌ خطا در اتصال به پایگاه داده.")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "⚙️ فرمت صحیح: `/setstatus YYYY-MM-DD status`\n\nمثال:\n`/setstatus 2024-01-15 completed`\n\nوضعیت‌های مجاز: `pending`, `completed`, `paid`")
        return

    query_date = args[1]
    new_status = args[2]
    
    if new_status not in ['pending', 'completed', 'paid']:
        bot.reply_to(message, "❌ وضعیت باید یکی از موارد زیر باشد:\n• `pending` (در انتظار)\n• `completed` (تکمیل شده)\n• `paid` (پرداخت شده)")
        return

    try:
        cursor.execute("UPDATE orders SET status = %s WHERE order_date = %s", (new_status, query_date))
        conn.commit()
        
        status_persian = get_persian_status(new_status)
        bot.reply_to(message, f"✅ وضعیت سفارش‌های {format_date_persian(query_date)} به '{status_persian}' تغییر یافت.")
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در تغییر وضعیت: {str(e)}")




if __name__ == "__main__":
    print("🤖 در حال راه‌اندازی ربات سفارش روزانه...")
    print("✅ ربات آماده است!")
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print("\n🛑 ربات متوقف شد.")
    except Exception as e:
        print(f"❌ خطا در اجرای ربات: {e}")
    finally:
        if conn:
            conn.close()
