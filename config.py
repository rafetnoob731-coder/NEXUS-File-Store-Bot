# ─── CONFIGURATION ──────────────────────────────────────────────────────────
# CREDIT: VIP DARK GOD | NEXUS STORE
# Made with ❤️ by @VIP_DARK_GOD
# ─────────────────────────────────────────────────────────────────────────────

import os
from typing import List, Dict, Optional

class Config:
    """Bot configuration - NEXUS STORE"""
    
    # ─── BOT SETTINGS ─────────────────────────────────────────────────────
    BOT_TOKEN = "8659779077:AAHGw7R-Z61xu6eFGErf97OPJOv0REUQcXg"        # Get from @BotFather
    BOT_NAME  = "NEXUS Files Store"          # Your bot's display name
    BOT_USERNAME = "Nexus_files_store_bot"   # Your bot's username (without @)
    
    # ─── ADMIN SETTINGS ───────────────────────────────────────────────────
    # Add multiple admin IDs separated by commas
    ADMIN_IDS = [
        "7702588711",   # Admin 1
        "7892915425",   # Admin 2
        "8526073588",   # Admin 3
    ]
    
    # ─── OWNER CONTACT ────────────────────────────────────────────────────
    OWNER_USERNAME = "nexus_pro_dev"         # Without the @ symbol
    OWNER_NAME = "NEXUS Pro Dev"             # Display name for owner
    
    # ─── COIN SETTINGS ────────────────────────────────────────────────────
    REFERRAL_COINS     = 1   # Coins referrer earns per successful referral
    NEW_USER_REF_COINS = 2   # Bonus coins new user gets when joining via referral
    STARTING_COINS     = 0   # Default coins for new users
    
    # ─── FORCE SUBSCRIBE CHANNELS ─────────────────────────────────────────
    # Users must join ALL channels below before using the bot
    # Format: {"name": "Display Name", "username": "channel_username"}
    # For private channels, use invite link as username
    FORCE_CHANNELS = [
        {"name": "VIP DARK GOD",  "username": "vip_dark_god_prime"},
        {"name": "NEXUS",         "username": "Nexusvipgod"},
    ]
    
    # ─── FILE SETTINGS ────────────────────────────────────────────────────
    FILES_PER_PAGE = 5          # Number of files shown per page in buy menu
    MAX_FILE_NAME_LENGTH = 100  # Maximum length for file names
    MAX_FILE_CONTENT_LENGTH = 4096  # Maximum length for text content
    
    # ─── REDEEM CODE SETTINGS ────────────────────────────────────────────
    CODE_EXPIRY_DAYS = 30       # Default expiry days for redeem codes
    CODE_LENGTH = 8             # Length of generated redeem codes
    
    # ─── DATABASE SETTINGS ───────────────────────────────────────────────
    DB_PATH = "bot_database.db"  # Database file path
    
    # ─── LOGGING SETTINGS ────────────────────────────────────────────────
    LOG_LEVEL = "INFO"           # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ─── BROADCAST SETTINGS ──────────────────────────────────────────────
    BROADCAST_BATCH_SIZE = 30    # Number of messages to send before sleeping
    BROADCAST_SLEEP_SECONDS = 1  # Sleep time between batches
    
    # ─── SUBSCRIPTION CACHE SETTINGS ─────────────────────────────────────
    SUBSCRIPTION_CACHE_MINUTES = 10  # How long to cache subscription checks
    
    # ─── RATE LIMITING SETTINGS ──────────────────────────────────────────
    RATE_LIMIT_ENABLED = True    # Enable/disable rate limiting
    RATE_LIMIT_CALLS = 30        # Number of calls allowed per minute
    RATE_LIMIT_PERIOD = 60       # Time period in seconds
    
    # ─── PAYMENT SETTINGS (Optional) ────────────────────────────────────
    # Add payment gateway settings if needed in future
    PAYMENT_ENABLED = False
    PAYMENT_PROVIDER = None      # e.g., "stripe", "paypal"
    PAYMENT_API_KEY = None
    
    # ─── FEATURE FLAGS ────────────────────────────────────────────────────
    ENABLE_LEADERBOARD = True    # Show/hide leaderboard feature
    ENABLE_REFERRALS = True      # Enable/disable referral system
    ENABLE_REDEEM_CODES = True   # Enable/disable redeem codes
    ENABLE_FORCE_SUBSCRIBE = True # Enable/disable force subscribe
    ENABLE_BROADCAST = True      # Enable/disable broadcast feature
    
    # ─── MESSAGES ─────────────────────────────────────────────────────────
    # Customizable messages (supports HTML formatting)
    WELCOME_MESSAGE = """
╔══════════════════════╗
      ⚡ <b>NEXUS STORE</b> ⚡
╚══════════════════════╝

👋 Hey <b>{first_name}</b>, Welcome to Nexus!

🔥 The ultimate destination for
   premium digital content.

🪙 Balance  :  <b>{coins} Coins</b>
━━━━━━━━━━━━━━━━━━━━━━
📁 Buy Files  |  🔗 Refer & Earn
━━━━━━━━━━━━━━━━━━━━━━
"""
    
    PURCHASE_SUCCESS_MESSAGE = """
✅ <b>Purchase Successful!</b>

📦 File      : <b>{file_name}</b>
💸 Paid      : <b>{price} Coins</b>
🪙 Remaining : <b>{remaining} Coins</b>

⬇️ Your file is below:
"""
    
    NOT_ENOUGH_COINS_MESSAGE = """
❌ <b>Not enough coins!</b>

🪙 Your coins  : <b>{coins}</b>
💰 Required    : <b>{price}</b>
📉 Shortfall   : <b>{shortfall}</b>

💡 Share your 🔗 Referral Link or use a 🎁 Redeem Code to earn more!
"""
    
    # ─── HELP / ABOUT MESSAGE ─────────────────────────────────────────────
    HELP_MESSAGE = """
⚡ <b>NEXUS STORE</b> ⚡
━━━━━━━━━━━━━━━━━

📁 <b>Buy Files</b> – Purchase premium files using coins.
🪙 <b>My Coins</b> – Check your balance and stats.
🔗 <b>Referral Link</b> – Share and earn coins.
🏆 <b>Leaderboard</b> – See top users.
🎁 <b>Redeem Code</b> – Use promo codes for free coins.
📞 <b>Contact Owner</b> – Get support.

━━━━━━━━━━━━━━━━━
🤖 Bot by @VIP_DARK_GOD
✨ Version 2.0 | NEXUS
"""
    
    # ─── CLASS METHODS ─────────────────────────────────────────────────────
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if a user is an admin."""
        return str(user_id) in cls.ADMIN_IDS
    
    @classmethod
    def get_channel_usernames(cls) -> List[str]:
        """Get list of channel usernames for force subscribe."""
        return [ch["username"] for ch in cls.FORCE_CHANNELS]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        errors = []
        
        # Check required settings
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        if not cls.ADMIN_IDS:
            errors.append("ADMIN_IDS is required (at least one admin)")
        if not cls.OWNER_USERNAME:
            errors.append("OWNER_USERNAME is required")
            
        # Check numeric values
        if cls.REFERRAL_COINS < 0:
            errors.append("REFERRAL_COINS must be >= 0")
        if cls.NEW_USER_REF_COINS < 0:
            errors.append("NEW_USER_REF_COINS must be >= 0")
        if cls.FILES_PER_PAGE < 1:
            errors.append("FILES_PER_PAGE must be >= 1")
        if cls.CODE_LENGTH < 4:
            errors.append("CODE_LENGTH must be >= 4")
            
        # Check channels
        for ch in cls.FORCE_CHANNELS:
            if not ch.get("name") or not ch.get("username"):
                errors.append(f"Invalid channel configuration: {ch}")
        
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(errors))
        
        return True
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables (override)."""
        cls.BOT_TOKEN = os.getenv("BOT_TOKEN", cls.BOT_TOKEN)
        cls.BOT_NAME = os.getenv("BOT_NAME", cls.BOT_NAME)
        cls.BOT_USERNAME = os.getenv("BOT_USERNAME", cls.BOT_USERNAME)
        cls.OWNER_USERNAME = os.getenv("OWNER_USERNAME", cls.OWNER_USERNAME)
        cls.OWNER_NAME = os.getenv("OWNER_NAME", cls.OWNER_NAME)
        cls.DB_PATH = os.getenv("DB_PATH", cls.DB_PATH)
        cls.LOG_LEVEL = os.getenv("LOG_LEVEL", cls.LOG_LEVEL)
        
        # Parse admin IDs from environment
        admin_ids = os.getenv("ADMIN_IDS", "")
        if admin_ids:
            cls.ADMIN_IDS = [id.strip() for id in admin_ids.split(",") if id.strip()]
        
        # Parse numeric values
        try:
            cls.REFERRAL_COINS = int(os.getenv("REFERRAL_COINS", cls.REFERRAL_COINS))
            cls.NEW_USER_REF_COINS = int(os.getenv("NEW_USER_REF_COINS", cls.NEW_USER_REF_COINS))
            cls.STARTING_COINS = int(os.getenv("STARTING_COINS", cls.STARTING_COINS))
            cls.FILES_PER_PAGE = int(os.getenv("FILES_PER_PAGE", cls.FILES_PER_PAGE))
            cls.CODE_EXPIRY_DAYS = int(os.getenv("CODE_EXPIRY_DAYS", cls.CODE_EXPIRY_DAYS))
            cls.CODE_LENGTH = int(os.getenv("CODE_LENGTH", cls.CODE_LENGTH))
            cls.SUBSCRIPTION_CACHE_MINUTES = int(os.getenv("SUBSCRIPTION_CACHE_MINUTES", cls.SUBSCRIPTION_CACHE_MINUTES))
        except ValueError:
            pass
        
        # Parse boolean values
        cls.ENABLE_LEADERBOARD = os.getenv("ENABLE_LEADERBOARD", str(cls.ENABLE_LEADERBOARD)).lower() == "true"
        cls.ENABLE_REFERRALS = os.getenv("ENABLE_REFERRALS", str(cls.ENABLE_REFERRALS)).lower() == "true"
        cls.ENABLE_REDEEM_CODES = os.getenv("ENABLE_REDEEM_CODES", str(cls.ENABLE_REDEEM_CODES)).lower() == "true"
        cls.ENABLE_FORCE_SUBSCRIBE = os.getenv("ENABLE_FORCE_SUBSCRIBE", str(cls.ENABLE_FORCE_SUBSCRIBE)).lower() == "true"
        cls.ENABLE_BROADCAST = os.getenv("ENABLE_BROADCAST", str(cls.ENABLE_BROADCAST)).lower() == "true"
        cls.RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", str(cls.RATE_LIMIT_ENABLED)).lower() == "true"
        cls.PAYMENT_ENABLED = os.getenv("PAYMENT_ENABLED", str(cls.PAYMENT_ENABLED)).lower() == "true"
        
        # Parse force channels from environment
        channels_str = os.getenv("FORCE_CHANNELS", "")
        if channels_str:
            cls.FORCE_CHANNELS = []
            for ch in channels_str.split(","):
                if ":" in ch:
                    name, username = ch.split(":", 1)
                    cls.FORCE_CHANNELS.append({"name": name.strip(), "username": username.strip()})
        
        return cls

# ─── EXPORT ──────────────────────────────────────────────────────────────
__all__ = ["Config"]

# ─── CREDIT: VIP DARK GOD ───────────────────────────────────────────────
# ⚡ NEXUS STORE — Configuration
# 🔥 Made with ❤️ by @VIP_DARK_GOD
# Version 3.0.0
# ─────────────────────────────────────────────────────────────────────────