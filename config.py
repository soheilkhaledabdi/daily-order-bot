BOT_TOKEN = ''
ADMIN_IDS = []

DATABASE_CONFIG = {
    'host': 'localhost',
    'user': '',
    'password': '',
    'database': '',
    'charset': 'utf8mb4',
    'autocommit': True
}

BOT_SETTINGS = {
    'timeout': 60,
    'long_polling_timeout': 60,
    'parse_mode': 'Markdown'
}

MESSAGES = {
    'welcome': """
🤖 **ربات سفارش کافیییی**

**دستورات اصلی:**
📝 `/order [متن سفارش]` - چی چی میخوای؟
📋 `/myorder` - امروز چی چی خریدم؟
❌ `/cancel` - سفارشمو نمیخوام
📚 `/help` - راهنمای کامل

**دستورات ادمین:**
📊 `/summary` - خلاصه سفارش‌های امروز
👑 `/history [تاریخ]` - تاریخچه سفارش‌ها
⚙️ `/setstatus [تاریخ] [وضعیت]` - تغییر وضعیت

برای شروع، سفارش خود را با دستور `/order` ثبت کنید!
    """,
    
    'help': """
📚 **راهنمای کامل ربات**

**دستورات کاربران:**
📝 `/order [متن سفارش]` - ثبت سفارش جدید برای امروز
📋 `/myorder` - مشاهده سفارش امروز خود
❌ `/cancel` - لغو سفارش امروز
📚 `/help` - نمایش این راهنما

**دستورات ادمین:**
📊 `/summary` - مشاهده خلاصه سفارش‌های امروز
👑 `/history [YYYY-MM-DD]` - مشاهده تاریخچه سفارش‌ها
⚙️ `/setstatus [تاریخ] [وضعیت]` - تغییر وضعیت سفارش‌ها
📈 `/stats` - آمار کلی ربات

**وضعیت‌های سفارش:**
⏳ در انتظار (pending)
✅ تکمیل شده (completed)
💰 پرداخت شده (paid)

**مثال‌ها:**
`/order قهوه آمریکانو`
`/history 2024-01-15`
    """,
}

ORDER_STATUSES = {
    'pending': 'در انتظار',
    'completed': 'تکمیل شده',
    'paid': 'پرداخت شده'
}