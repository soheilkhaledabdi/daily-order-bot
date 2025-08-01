import sys
import signal
from datetime import datetime

def check_dependencies():
    try:
        import telebot
        import mysql.connector
        print("✅ تمام وابستگی‌ها نصب شده‌اند")
        return True
    except ImportError as e:
        print(f"❌ وابستگی مورد نیاز نصب نشده: {e}")
        print("💡 برای نصب وابستگی‌ها دستور زیر را اجرا کنید:")
        print("pip install -r requirements.txt")
        return False

def check_database():
    try:
        from config import DATABASE_CONFIG
        import mysql.connector
        
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        print("✅ اتصال به پایگاه داده برقرار است")
        return True
    except Exception as e:
        print(f"❌ خطا در اتصال به پایگاه داده: {e}")
        print("💡 لطفاً تنظیمات پایگاه داده را در فایل config.py بررسی کنید")
        return False

def signal_handler(signum, frame):
    print(f"\n🛑 دریافت سیگنال {signum}، در حال خروج...")
    sys.exit(0)

def main():
    print("🤖 راه‌اندازی ربات سفارش روزانه...")
    print("=" * 50)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_database():
        print("⚠️  ادامه بدون بررسی پایگاه داده...")
    
    print("🚀 شروع ربات...")
    print("=" * 50)
    
    try:
        from main import bot
        
        print("✅ ربات آماده است!")
        print("📝 برای توقف ربات Ctrl+C را فشار دهید")
        print("=" * 50)
        
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
        
    except KeyboardInterrupt:
        print("\n🛑 ربات توسط کاربر متوقف شد")
    except Exception as e:
        print(f"❌ خطا در اجرای ربات: {e}")
        sys.exit(1)
    finally:
        print("👋 ربات متوقف شد")

if __name__ == "__main__":
    main() 