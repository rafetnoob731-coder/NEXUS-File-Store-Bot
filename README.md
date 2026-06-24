🗂️ NEXUS File Store Bot — Complete Setup Guide

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              ⚡ NEXUS FILE STORE BOT ⚡                       ║
║                                                              ║
║         Premium Digital Content Delivery System              ║
║                                                              ║
║              Made with ❤️ by @VIP_DARK_GOD                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

📋 Table of Contents

· Features
· Quick Setup
· Detailed Configuration
· Admin Panel Guide
· User Commands
· Database Schema
· Troubleshooting
· Advanced Features

---

✨ Features

🔹 User Features

Feature Description
📁 Buy Files Purchase premium files using coins (Text, Documents, Links)
🪙 Coin System Earn and spend coins within the bot
🔗 Referral System Earn coins for every user you refer
🏆 Leaderboard See top users by coin balance
🎁 Redeem Codes Use promo codes to get free coins
📞 Contact Owner Direct support contact
❓ Help/About Bot information and guide

🔹 Admin Features

Feature Description
➕ Add File Upload new files with name, price, and content
✏️ Edit File Modify existing file details
🗑️ Remove File Delete files from the store
🎫 Create Redeem Code Generate promo codes with coin rewards
💰 Give Coins Manually add coins to any user
📢 Broadcast Send messages to all users
📊 Bot Stats View comprehensive statistics
👥 All Users See complete user list with balances
🚫 Ban/Unban Control user access

---

🚀 Quick Setup

Step 1 — Install Requirements

```bash
pip install -r requirements.txt
```

Step 2 — Configure the Bot

Edit config.py with your details:

```python
# ─── BOT SETTINGS ─────────────────────────────────────────────────────
BOT_TOKEN = "8659779077:AAHGw7R-Z61xu6eFGErf97OPJOv0REUQcXg"  # From @BotFather
BOT_NAME  = "NEXUS Files Store"
BOT_USERNAME = "Nexus_files_store_bot"

# ─── ADMIN SETTINGS ───────────────────────────────────────────────────
ADMIN_IDS = [
    "7702588711",   # Your Telegram ID
    "7892915425",   # Additional admins
    "8526073588",
]

# ─── OWNER CONTACT ────────────────────────────────────────────────────
OWNER_USERNAME = "nexus_pro_dev"  # Your Telegram username
OWNER_NAME = "NEXUS Pro Dev"

# ─── COIN SETTINGS ────────────────────────────────────────────────────
REFERRAL_COINS     = 1   # Coins per referral
NEW_USER_REF_COINS = 2   # Bonus for new users

# ─── FORCE SUBSCRIBE CHANNELS ────────────────────────────────────────
FORCE_CHANNELS = [
    {"name": "VIP DARK GOD",  "username": "vip_dark_god_prime"},
    {"name": "NEXUS",         "username": "+zY5NXeQdHNo2OGM9"},
]
```

Step 3 — Run the Bot

```bash
python bot.py
```

---

📝 Detailed Configuration

Getting Your Telegram ID

1. Search for @userinfobot on Telegram
2. Start the bot
3. It will send your User ID instantly

Getting Bot Token

1. Search for @BotFather on Telegram
2. Send /newbot
3. Follow the instructions
4. Copy the token provided

Setting Up Force Subscribe

```python
# Public channels (use username without @)
FORCE_CHANNELS = [
    {"name": "My Channel", "username": "my_channel"},
]

# Private channels (use invite link hash)
FORCE_CHANNELS = [
    {"name": "Private Channel", "username": "+zY5NXeQdHNo2OGM9"},
]
```

---

👑 Admin Panel Guide

Accessing Admin Panel

· Admin buttons appear automatically when an admin uses the bot
· Regular users see the main menu

➕ Adding a File

```
1. Click "➕ Add File"
2. Enter file name
3. Enter price in coins
4. Send content:
   - Text: Type or paste it
   - Document: Upload directly
   - Link: Paste the URL
```

✏️ Editing a File

```
1. Click "✏️ Edit File"
2. Select the file to edit
3. Choose what to change:
   - 📝 Change Name
   - 💰 Change Price
   - 📄 Change Content
4. Enter new value
```

🗑️ Removing a File

```
1. Click "🗑️ Remove File"
2. Select the file to delete
3. Confirm removal
```

🎫 Creating Redeem Codes

```
1. Click "🎫 Create Redeem Code"
2. Enter coin amount (e.g., 10)
3. Enter max uses (e.g., 100)
4. Code is generated and displayed
```

💰 Giving Coins to Users

```
1. Click "💰 Give Coins"
2. Enter User ID or Username
3. Enter amount of coins
4. User receives coins instantly
```

📢 Broadcasting Messages

```
1. Click "📢 Broadcast"
2. Type your message
3. Bot sends to all registered users
4. Shows delivery statistics
```

---

👤 User Commands

Available Commands

Command Description
/start Start the bot and get welcome message
/help Show help information
/buy Open file store
/coins Check your balance
/referral Get your referral link
/leaderboard View top users
/redeem Use a promo code
/contact Contact the owner

Keyboard Navigation

```
┌─────────────────────────────┐
│  📁 Buy Files  🪙 My Coins   │
│  🔗 Referral  🏆 Leaderboard │
│  🎁 Redeem Code 📞 Contact   │
│  ❓ Help / About             │
└─────────────────────────────┘
```

---

🗄️ Database Schema

Tables Structure

Users Table

```sql
CREATE TABLE users (
    user_id     INTEGER PRIMARY KEY,
    username    TEXT,
    coins       INTEGER DEFAULT 0,
    joined_at   TEXT,
    referred_by INTEGER,
    is_banned   INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    last_active TEXT
);
```

Files Table

```sql
CREATE TABLE files (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    price       INTEGER NOT NULL,
    content     TEXT NOT NULL,
    created_at  TEXT,
    updated_at  TEXT,
    is_active   INTEGER DEFAULT 1,
    download_count INTEGER DEFAULT 0
);
```

Purchases Table

```sql
CREATE TABLE purchases (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    file_id     INTEGER,
    purchased_at TEXT,
    price_paid  INTEGER
);
```

Referrals Table

```sql
CREATE TABLE referrals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER,
    referred_id INTEGER UNIQUE,
    created_at  TEXT,
    rewarded    INTEGER DEFAULT 1
);
```

Redeem Codes Table

```sql
CREATE TABLE redeem_codes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT UNIQUE,
    coins       INTEGER,
    max_uses    INTEGER,
    used_count  INTEGER DEFAULT 0,
    created_at  TEXT,
    expires_at  TEXT,
    created_by  INTEGER,
    is_active   INTEGER DEFAULT 1
);
```

---

🔧 Troubleshooting

Common Issues & Solutions

❌ "Bot not starting"

```bash
# Check if token is correct
# Check internet connection
# Verify all dependencies installed
pip install --upgrade python-telegram-bot
```

❌ "Database errors"

```bash
# Delete database and restart
rm filestore.db
python bot.py
```

❌ "Admin commands not showing"

```python
# Verify your ID is in ADMIN_IDS
ADMIN_IDS = ["7702588711"]  # Your ID must match exactly
```

❌ "Force subscribe not working"

```python
# Check channel usernames are correct
# For private channels, use invite link hash
FORCE_CHANNELS = [
    {"username": "+zY5NXeQdHNo2OGM9"},  # Private channel
]
```

---

🚀 Advanced Features

Environment Variables Support

Create a .env file:

```bash
BOT_TOKEN=your_token_here
ADMIN_IDS=7702588711,7892915425
REFERRAL_COINS=1
NEW_USER_REF_COINS=2
```

Custom Messages

Edit config.py to customize bot messages:

```python
WELCOME_MESSAGE = """
╔══════════════════════╗
      ⚡ NEXUS STORE ⚡
╚══════════════════════╝
👋 Welcome {first_name}!
...
"""
```

Rate Limiting

```python
RATE_LIMIT_ENABLED = True
RATE_LIMIT_CALLS = 30   # Calls per minute
RATE_LIMIT_PERIOD = 60  # Seconds
```

Broadcast Performance

```python
BROADCAST_BATCH_SIZE = 30    # Messages per batch
BROADCAST_SLEEP_SECONDS = 1  # Sleep between batches
```

---

📚 Requirements

Create requirements.txt:

```txt
python-telegram-bot==20.7
```

---

🎯 Quick Reference

Admin Checklist

· Bot token configured
· Admin IDs added
· Owner username set
· Channels configured
· Coin values set
· Bot tested

User Flow

1. User starts bot → Joins required channels
2. Uses referral link (optional)
3. Earns coins via referrals/redeem
4. Buys files from store
5. Downloads purchased files

---

💬 Support

Contact

· Bot Developer: @VIP_DARK_GOD
· Channel: @vip_dark_god_prime
· Support: @nexus_pro_dev

Report Issues

```python
# Include in your bug report:
1. Bot version
2. Error message
3. Steps to reproduce
4. Logs (if available)
```

---

📜 License

```
MIT License

Copyright (c) 2024 VIP DARK GOD | NEXUS

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

---

🎉 Success!

Your NEXUS File Store Bot is now ready to use!

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎉 Congratulations! Your bot is now live and working!     ║
║                                                              ║
║   📢 Share your bot with users and start selling files!     ║
║                                                              ║
║   Made with ❤️ by @VIP_DARK_GOD | NEXUS Store               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

🚀 Happy Botting!

This guide is maintained by @VIP_DARK_GOD for the NEXUS File Store Bot.