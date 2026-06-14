# 🛡️ CleanIP Bot

A Telegram bot for crowdsourcing and distributing clean Cloudflare IP addresses. Users submit clean IPs, admins verify them, and the bot replaces IPs inside Vless/Trojan proxy configs automatically.

## ✨ Features

- Submit clean Cloudflare IPs via Telegram
- Admin approval/rejection system with inline buttons
- Automatic IP replacement inside Vless & Trojan configs
- IPv4 and IPv6 support
- SQLite database for persistent storage
- User contribution stats

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))
- Your Telegram user ID (as admin)

### Installation

```bash
git clone https://github.com/Never-loser/scanner.git
cd scanner
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_user_id_here
```

### Run

```bash
python bot.py
```

## 📁 Project Structure

```
├── bot.py          # Telegram bot logic and handlers
├── database.py     # SQLite database operations
├── ip_parser.py    # Vless/Trojan config parser and IP replacer
├── seed_ips.py     # Script to seed initial IPs into the database
├── requirements.txt
└── .env            # Environment variables (not committed)
```

## 🤖 Bot Commands

| Action | Description |
|--------|-------------|
| `/start` | Show main menu |
| 📤 Send Config | Submit your Vless/Trojan config to get a clean IP injected |
| 📥 Send Clean IP | Submit a clean Cloudflare IP for admin review |
| 📊 My Stats | See how many IPs you've contributed |

## 🔒 How It Works

1. A user submits a clean Cloudflare IP
2. The bot forwards it to the admin with Approve/Reject buttons
3. If approved, the IP enters the pool
4. Any user can submit their proxy config and get a random approved IP injected into it

## 📦 Requirements

```
pyTelegramBotAPI
python-dotenv
```

## ⚠️ Notes

- Only Vless and Trojan protocols are supported
- The bot validates IP format but does not automatically verify Cloudflare ownership
- The `.env` file and database are excluded from version control

## 📄 License

MIT
