# 🤖 Daily Order Bot

Telegram bot for managing daily orders with the ability to learn new commands

## ✨ Features

### 🎯 Main Features
- 📝 Register daily orders
- 📋 View today's orders
- ❌ Cancel orders
- 📊 Summary of today's orders
- 📈 Complete bot statistics

### 👑 Admin Features
- 📅 View order history
- ⚙️ Change order status
- 📊 Overall bot statistics

### 🌟 New Features
- 📱 Beautiful Persian user interface
- 🛡️ Error management
- 💾 MySQL database storage

## 🚀 Installation and Setup

### Prerequisites
- Python 3.7+
- MySQL Server
- Bot Token from @BotFather

### Installation Steps

1. **Clone the project:**
```bash
git clone https://github.com/soheilkhaledabdi/daily-order-bot
cd daily-order-bot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup database:**
```sql
CREATE DATABASE order_bot;
CREATE USER 'bot_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON order_bot.* TO 'bot_user'@'localhost';
FLUSH PRIVILEGES;
```

4. **Configure main.py:**
- Place bot token in the `TOKEN` variable
- Add admin information to the `ADMINS` list
- Change database settings in `db_config`

5. **Run the bot:**
```bash
python main.py
```

## 📚 Bot Commands

### User Commands
- `/start` - Start bot and show guide
- `/help` - Complete guide
- `/order [order text]` - Register new order
- `/myorder` - View today's order
- `/cancel` - Cancel today's order

### Admin Commands

- `/summary` - Summary of today's orders
- `/history [YYYY-MM-DD]` - Order history
- `/setstatus [date] [status]` - Change status
- `/stats` - Overall bot statistics

### Order Statuses
- ⏳ **Pending** (pending)
- ✅ **Completed** (completed)
- 💰 **Paid** (paid)



## 🛠️ Project Structure

```
daily-order-bot/
├── main.py              # Main bot file
├── requirements.txt      # Dependencies
├── README.md           # Guide
├── LICENSE             # License

```

## 🔧 Configuration

### Important variables in main.py:
- `TOKEN`: Telegram bot token
- `ADMINS`: List of admin IDs
- `db_config`: Database settings

## 🐛 Troubleshooting

### Common errors:
1. **Database connection error:**
   - Check MySQL settings
   - Ensure database exists

2. **Bot execution error:**
   - Check dependency installation
   - Verify token validity

## 📝 License

This project is published under MIT license.

## 🤝 Contributing

To contribute to improving this project:
1. Fork the project
2. Create a new branch
3. Commit your changes
4. Send a Pull Request