import mysql.connector
from config import DATABASE_CONFIG

def create_database():
    db_config = DATABASE_CONFIG.copy()
    db_config.pop('database', None)
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("🔧 راه‌اندازی پایگاه داده...")
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ دیتابیس {DATABASE_CONFIG['database']} ایجاد شد")
        
        cursor.execute(f"USE {DATABASE_CONFIG['database']}")
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            username VARCHAR(255),
            order_text TEXT NOT NULL,
            order_date DATE NOT NULL,
            status ENUM('pending', 'completed', 'paid') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user_date (user_id, order_date),
            INDEX idx_date_status (order_date, status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ جدول orders ایجاد شد")
        

        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT,
            action VARCHAR(100),
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_action (user_id, action),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ جدول bot_logs ایجاد شد")
        
        conn.commit()
        print("✅ تمام جداول با موفقیت ایجاد شدند")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📊 جداول موجود: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ خطا در راه‌اندازی پایگاه داده: {e}")
        return False

def test_connection():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == 1:
            print("✅ اتصال به پایگاه داده موفق است")
            return True
        else:
            print("❌ اتصال به پایگاه داده ناموفق است")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست اتصال: {e}")
        return False

def main():
    print("🤖 راه‌اندازی پایگاه داده ربات سفارش روزانه")
    print("=" * 50)
    
    if not test_connection():
        print("💡 لطفاً تنظیمات پایگاه داده را در فایل config.py بررسی کنید")
        return
    
    if create_database():
        print("\n🎉 راه‌اندازی پایگاه داده با موفقیت انجام شد!")
        print("✅ ربات آماده اجرا است")
        print("\n💡 برای اجرای ربات دستور زیر را وارد کنید:")
        print("python run.py")
    else:
        print("\n❌ راه‌اندازی پایگاه داده ناموفق بود")
        print("💡 لطفاً خطاها را بررسی کنید")

if __name__ == "__main__":
    main() 