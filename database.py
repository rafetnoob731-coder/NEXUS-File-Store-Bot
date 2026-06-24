# ─── DATABASE ──────────────────────────────────────────────────────────────
# CREDIT: VIP DARK GOD | NEXUS STORE
# Made with ❤️ by @VIP_DARK_GOD
# ─────────────────────────────────────────────────────────────────────────────

import sqlite3
import random
import string
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

DB_PATH = "filestore.db"

class Database:
    """NEXUS STORE Database Handler - Advanced SQLite wrapper with full features."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        logger.info(f"✅ Database initialized: {db_path}")

    def _create_tables(self):
        """Create all necessary tables with proper schema."""
        c = self.conn.cursor()
        c.executescript("""
            -- Users table
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                coins       INTEGER DEFAULT 0,
                joined_at   TEXT,
                referred_by INTEGER,
                is_banned   INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                last_active TEXT
            );

            -- Files table
            CREATE TABLE IF NOT EXISTS files (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                price       INTEGER NOT NULL,
                content     TEXT NOT NULL,
                created_at  TEXT,
                updated_at  TEXT,
                is_active   INTEGER DEFAULT 1,
                download_count INTEGER DEFAULT 0
            );

            -- Purchases table
            CREATE TABLE IF NOT EXISTS purchases (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                file_id     INTEGER,
                purchased_at TEXT,
                price_paid  INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (file_id) REFERENCES files(id)
            );

            -- Referrals table
            CREATE TABLE IF NOT EXISTS referrals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER UNIQUE,
                created_at  TEXT,
                rewarded    INTEGER DEFAULT 1,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                FOREIGN KEY (referred_id) REFERENCES users(user_id)
            );

            -- Redeem codes table
            CREATE TABLE IF NOT EXISTS redeem_codes (
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

            -- Code usage table
            CREATE TABLE IF NOT EXISTS code_uses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                code_id     INTEGER,
                user_id     INTEGER,
                used_at     TEXT,
                UNIQUE(code_id, user_id),
                FOREIGN KEY (code_id) REFERENCES redeem_codes(id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            -- User activity log
            CREATE TABLE IF NOT EXISTS user_activity (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                action      TEXT,
                details     TEXT,
                created_at  TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)
        self.conn.commit()
        logger.debug("✅ All tables created/verified")

    # ─── HELPER METHODS ────────────────────────────────────────────────────
    def _now(self) -> str:
        """Get current timestamp as ISO format string."""
        return datetime.now().isoformat()

    def _execute(self, query: str, params: tuple = ()) -> Any:
        """Execute a query with error handling."""
        try:
            c = self.conn.cursor()
            c.execute(query, params)
            self.conn.commit()
            return c
        except sqlite3.Error as e:
            logger.error(f"Database error: {e} | Query: {query}")
            raise

    def _fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one row and return as dict."""
        c = self._execute(query, params)
        row = c.fetchone()
        return dict(row) if row else None

    def _fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows and return as list of dicts."""
        c = self._execute(query, params)
        return [dict(r) for r in c.fetchall()]

    # ─── USERS ──────────────────────────────────────────────────────────────
    def add_user(self, user_id: int, username: str, referred_by: int = None) -> bool:
        """
        Add a new user to the database.
        Returns True if new user was added, False if already exists.
        """
        c = self.conn.cursor()
        c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if c.fetchone():
            return False
        
        c.execute(
            """INSERT INTO users 
               (user_id, username, coins, joined_at, referred_by, last_active) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, username, 0, self._now(), referred_by, self._now())
        )
        self.conn.commit()
        
        # Log activity
        self.log_activity(user_id, "register", f"Referred by: {referred_by}")
        logger.info(f"✅ New user registered: {user_id} ({username})")
        return True

    def user_exists(self, user_id: int) -> bool:
        """Check if a user exists in the database."""
        c = self.conn.cursor()
        c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        return c.fetchone() is not None

    def find_user(self, identifier: Union[int, str]) -> Optional[Dict]:
        """Find a user by ID or username."""
        if str(identifier).isdigit():
            return self._fetch_one(
                "SELECT * FROM users WHERE user_id = ?", (int(identifier),)
            )
        return self._fetch_one(
            "SELECT * FROM users WHERE username LIKE ?", (f"%{identifier}%",)
        )

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get complete user data by ID."""
        return self._fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))

    def get_all_users(self, limit: int = None, offset: int = 0) -> List[Dict]:
        """Get all users with optional pagination."""
        query = "SELECT * FROM users ORDER BY user_id"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        return self._fetch_all(query)

    def count_users(self) -> int:
        """Get total number of users."""
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) as count FROM users")
        return c.fetchone()['count']

    def update_username(self, user_id: int, username: str):
        """Update user's username."""
        self._execute(
            "UPDATE users SET username = ? WHERE user_id = ?",
            (username, user_id)
        )
        self.log_activity(user_id, "update_username", f"New username: {username}")

    def update_last_active(self, user_id: int):
        """Update user's last active timestamp."""
        self._execute(
            "UPDATE users SET last_active = ? WHERE user_id = ?",
            (self._now(), user_id)
        )

    def ban_user(self, user_id: int):
        """Ban a user from using the bot."""
        self._execute(
            "UPDATE users SET is_banned = 1 WHERE user_id = ?",
            (user_id,)
        )
        self.log_activity(user_id, "ban", "User banned by admin")
        logger.warning(f"🚫 User banned: {user_id}")

    def unban_user(self, user_id: int):
        """Unban a user."""
        self._execute(
            "UPDATE users SET is_banned = 0 WHERE user_id = ?",
            (user_id,)
        )
        self.log_activity(user_id, "unban", "User unbanned by admin")
        logger.info(f"✅ User unbanned: {user_id}")

    def is_banned(self, user_id: int) -> bool:
        """Check if a user is banned."""
        c = self.conn.cursor()
        c.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return bool(row and row['is_banned'])

    # ─── COINS ──────────────────────────────────────────────────────────────
    def get_coins(self, user_id: int) -> int:
        """Get user's coin balance."""
        c = self.conn.cursor()
        c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return row['coins'] if row else 0

    def add_coins(self, user_id: int, amount: int) -> int:
        """
        Add coins to a user's balance.
        Returns the new balance.
        """
        if amount <= 0:
            return self.get_coins(user_id)
        
        self._execute(
            "UPDATE users SET coins = coins + ? WHERE user_id = ?",
            (amount, user_id)
        )
        new_balance = self.get_coins(user_id)
        self.log_activity(user_id, "add_coins", f"Added {amount} coins. New: {new_balance}")
        logger.debug(f"💰 Added {amount} coins to user {user_id}. New: {new_balance}")
        return new_balance

    def deduct_coins(self, user_id: int, amount: int) -> bool:
        """
        Deduct coins from a user's balance.
        Returns True if successful, False if insufficient balance.
        """
        if amount <= 0:
            return True
        
        current = self.get_coins(user_id)
        if current < amount:
            return False
        
        self._execute(
            "UPDATE users SET coins = coins - ? WHERE user_id = ?",
            (amount, user_id)
        )
        new_balance = current - amount
        self.log_activity(user_id, "deduct_coins", f"Deducted {amount} coins. New: {new_balance}")
        logger.debug(f"💰 Deducted {amount} coins from user {user_id}. New: {new_balance}")
        return True

    def set_coins(self, user_id: int, amount: int):
        """Set user's coins to exact amount."""
        if amount < 0:
            amount = 0
        self._execute(
            "UPDATE users SET coins = ? WHERE user_id = ?",
            (amount, user_id)
        )
        self.log_activity(user_id, "set_coins", f"Set to {amount} coins")

    def add_spent(self, user_id: int, amount: int):
        """Track total spent by user."""
        self._execute(
            "UPDATE users SET total_spent = total_spent + ? WHERE user_id = ?",
            (amount, user_id)
        )

    # ─── FILES ──────────────────────────────────────────────────────────────
    def add_file(self, name: str, price: int, content: str) -> int:
        """
        Add a new file to the store.
        Returns the file ID.
        """
        c = self._execute(
            """INSERT INTO files (name, price, content, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?)""",
            (name, price, content, self._now(), self._now())
        )
        file_id = c.lastrowid
        logger.info(f"📁 New file added: {name} (ID: {file_id})")
        return file_id

    def get_file(self, file_id: int) -> Optional[Dict]:
        """Get a file by ID."""
        return self._fetch_one(
            "SELECT * FROM files WHERE id = ? AND is_active = 1",
            (file_id,)
        )

    def get_all_files(self, active_only: bool = True) -> List[Dict]:
        """Get all files."""
        query = "SELECT * FROM files"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY id"
        return self._fetch_all(query)

    def get_files_paginated(self, offset: int = 0, limit: int = 5, active_only: bool = True) -> List[Dict]:
        """Get files with pagination."""
        query = "SELECT * FROM files"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY id LIMIT ? OFFSET ?"
        return self._fetch_all(query, (limit, offset))

    def count_files(self, active_only: bool = True) -> int:
        """Get total number of files."""
        query = "SELECT COUNT(*) as count FROM files"
        if active_only:
            query += " WHERE is_active = 1"
        c = self.conn.cursor()
        c.execute(query)
        return c.fetchone()['count']

    def update_file(self, file_id: int, name: str = None, price: int = None, content: str = None):
        """Update a file's details."""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if price is not None:
            updates.append("price = ?")
            params.append(price)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        
        if updates:
            updates.append("updated_at = ?")
            params.append(self._now())
            params.append(file_id)
            
            self._execute(
                f"UPDATE files SET {', '.join(updates)} WHERE id = ?",
                tuple(params)
            )
            logger.info(f"✏️ File updated: {file_id}")

    def remove_file(self, file_id: int, soft_delete: bool = True):
        """
        Remove a file. 
        If soft_delete=True, just deactivate it.
        If soft_delete=False, permanently delete it.
        """
        if soft_delete:
            self._execute(
                "UPDATE files SET is_active = 0 WHERE id = ?",
                (file_id,)
            )
            logger.info(f"🗑️ File deactivated: {file_id}")
        else:
            self._execute("DELETE FROM files WHERE id = ?", (file_id,))
            logger.info(f"🗑️ File permanently deleted: {file_id}")

    def increment_download(self, file_id: int):
        """Increment file download count."""
        self._execute(
            "UPDATE files SET download_count = download_count + 1 WHERE id = ?",
            (file_id,)
        )

    # ─── PURCHASES ──────────────────────────────────────────────────────────
    def record_purchase(self, user_id: int, file_id: int, price_paid: int):
        """Record a file purchase."""
        self._execute(
            """INSERT INTO purchases (user_id, file_id, purchased_at, price_paid) 
               VALUES (?, ?, ?, ?)""",
            (user_id, file_id, self._now(), price_paid)
        )
        self.add_spent(user_id, price_paid)
        self.increment_download(file_id)
        self.log_activity(user_id, "purchase", f"File ID: {file_id}, Price: {price_paid}")
        logger.info(f"🛒 User {user_id} purchased file {file_id} for {price_paid} coins")

    def already_purchased(self, user_id: int, file_id: int) -> bool:
        """Check if a user has already purchased a file."""
        c = self.conn.cursor()
        c.execute(
            "SELECT id FROM purchases WHERE user_id = ? AND file_id = ?",
            (user_id, file_id)
        )
        return c.fetchone() is not None

    def get_user_purchases(self, user_id: int) -> List[Dict]:
        """Get all purchases by a user."""
        return self._fetch_all(
            """SELECT p.*, f.name as file_name, f.price 
               FROM purchases p 
               JOIN files f ON p.file_id = f.id 
               WHERE p.user_id = ? 
               ORDER BY p.purchased_at DESC""",
            (user_id,)
        )

    def get_purchase_count(self, user_id: int) -> int:
        """Get total number of purchases by a user."""
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) as count FROM purchases WHERE user_id = ?", (user_id,))
        return c.fetchone()['count']

    def get_total_spent(self, user_id: int) -> int:
        """Get total coins spent by a user."""
        c = self.conn.cursor()
        c.execute("SELECT total_spent FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return row['total_spent'] if row else 0

    # ─── REFERRALS ──────────────────────────────────────────────────────────
    def record_referral(self, referrer_id: int, referred_id: int) -> bool:
        """
        Record a referral.
        Returns True if successful, False if already recorded.
        """
        try:
            self._execute(
                "INSERT INTO referrals (referrer_id, referred_id, created_at) VALUES (?, ?, ?)",
                (referrer_id, referred_id, self._now())
            )
            self.log_activity(referrer_id, "referral", f"Referred user: {referred_id}")
            logger.info(f"🔗 Referral recorded: {referrer_id} -> {referred_id}")
            return True
        except sqlite3.IntegrityError:
            return False

    def get_referral_count(self, user_id: int) -> int:
        """Get total referrals by a user."""
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) as count FROM referrals WHERE referrer_id = ?", (user_id,))
        return c.fetchone()['count']

    def get_referrals(self, user_id: int) -> List[Dict]:
        """Get all referrals by a user with details."""
        return self._fetch_all(
            """SELECT r.*, u.username as referred_username, u.joined_at 
               FROM referrals r 
               JOIN users u ON r.referred_id = u.user_id 
               WHERE r.referrer_id = ? 
               ORDER BY r.created_at DESC""",
            (user_id,)
        )

    def get_referred_by(self, user_id: int) -> Optional[Dict]:
        """Get who referred a user."""
        return self._fetch_one(
            """SELECT r.*, u.username as referrer_username 
               FROM referrals r 
               JOIN users u ON r.referrer_id = u.user_id 
               WHERE r.referred_id = ?""",
            (user_id,)
        )

    # ─── REDEEM CODES ───────────────────────────────────────────────────────
    def create_redeem_code(self, coins: int, max_uses: int, expires_days: int = 30, created_by: int = None) -> str:
        """
        Create a new redeem code.
        Returns the generated code.
        """
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
        
        self._execute(
            """INSERT INTO redeem_codes 
               (code, coins, max_uses, created_at, expires_at, created_by) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (code, coins, max_uses, self._now(), expires_at, created_by)
        )
        logger.info(f"🎫 Redeem code created: {code} ({coins} coins, {max_uses} uses)")
        return code

    def use_redeem_code(self, code: str, user_id: int) -> Union[int, str]:
        """
        Use a redeem code.
        Returns:
        - int: coins added (success)
        - 'not_found': code doesn't exist
        - 'expired': code expired or used up
        - 'already_used': user already used this code
        - 'inactive': code is inactive
        """
        c = self.conn.cursor()
        c.execute(
            """SELECT * FROM redeem_codes 
               WHERE code = ? AND is_active = 1""",
            (code,)
        )
        row = c.fetchone()
        
        if not row:
            return "not_found"
        
        row = dict(row)
        
        # Check expiry
        if row['expires_at'] and datetime.now() > datetime.fromisoformat(row['expires_at']):
            return "expired"
        
        # Check max uses
        if row['used_count'] >= row['max_uses']:
            return "expired"
        
        # Check if user already used
        c.execute(
            "SELECT id FROM code_uses WHERE code_id = ? AND user_id = ?",
            (row['id'], user_id)
        )
        if c.fetchone():
            return "already_used"
        
        # Apply the code
        self._execute(
            "UPDATE redeem_codes SET used_count = used_count + 1 WHERE id = ?",
            (row['id'],)
        )
        self._execute(
            "INSERT INTO code_uses (code_id, user_id, used_at) VALUES (?, ?, ?)",
            (row['id'], user_id, self._now())
        )
        
        # Add coins to user
        self.add_coins(user_id, row['coins'])
        self.log_activity(user_id, "redeem_code", f"Code: {code}, Coins: {row['coins']}")
        
        logger.info(f"✅ User {user_id} redeemed code {code} for {row['coins']} coins")
        return row['coins']

    def get_redeem_code(self, code: str) -> Optional[Dict]:
        """Get redeem code details."""
        return self._fetch_one(
            "SELECT * FROM redeem_codes WHERE code = ?",
            (code,)
        )

    def get_all_redeem_codes(self) -> List[Dict]:
        """Get all redeem codes."""
        return self._fetch_all("SELECT * FROM redeem_codes ORDER BY created_at DESC")

    def deactivate_redeem_code(self, code: str):
        """Deactivate a redeem code."""
        self._execute(
            "UPDATE redeem_codes SET is_active = 0 WHERE code = ?",
            (code,)
        )
        logger.info(f"🎫 Redeem code deactivated: {code}")

    # ─── LEADERBOARD ────────────────────────────────────────────────────────
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users by coins."""
        return self._fetch_all(
            """SELECT user_id, username, coins, total_spent, 
               (SELECT COUNT(*) FROM referrals WHERE referrer_id = users.user_id) as referrals_count
               FROM users 
               ORDER BY coins DESC LIMIT ?""",
            (limit,)
        )

    def get_leaderboard_by_purchases(self, limit: int = 10) -> List[Dict]:
        """Get top users by purchase count."""
        return self._fetch_all(
            """SELECT u.user_id, u.username, u.coins, 
               COUNT(p.id) as purchases_count, SUM(p.price_paid) as total_spent
               FROM users u
               LEFT JOIN purchases p ON u.user_id = p.user_id
               GROUP BY u.user_id
               ORDER BY purchases_count DESC LIMIT ?""",
            (limit,)
        )

    # ─── STATS ──────────────────────────────────────────────────────────────
    def get_stats(self) -> Dict:
        """Get comprehensive bot statistics."""
        c = self.conn.cursor()
        
        # Basic stats
        stats = {}
        
        c.execute("SELECT COUNT(*) as count FROM users")
        stats['users'] = c.fetchone()['count']
        
        c.execute("SELECT COUNT(*) as count FROM files WHERE is_active = 1")
        stats['files'] = c.fetchone()['count']
        
        c.execute("SELECT COUNT(*) as count FROM purchases")
        stats['purchases'] = c.fetchone()['count']
        
        c.execute(
            "SELECT COUNT(*) as count FROM redeem_codes WHERE is_active = 1 AND used_count < max_uses"
        )
        stats['active_codes'] = c.fetchone()['count']
        
        # Revenue stats
        c.execute("SELECT SUM(price_paid) as total FROM purchases")
        stats['total_coins_spent'] = c.fetchone()['total'] or 0
        
        c.execute("SELECT SUM(coins) as total FROM users")
        stats['total_coins_in_circulation'] = c.fetchone()['total'] or 0
        
        # Referral stats
        c.execute("SELECT COUNT(*) as count FROM referrals")
        stats['total_referrals'] = c.fetchone()['count']
        
        return stats

    # ─── ACTIVITY LOG ──────────────────────────────────────────────────────
    def log_activity(self, user_id: int, action: str, details: str = ""):
        """Log user activity."""
        try:
            self._execute(
                "INSERT INTO user_activity (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
                (user_id, action, details, self._now())
            )
        except Exception as e:
            logger.warning(f"Failed to log activity: {e}")

    def get_user_activity(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user activity log."""
        return self._fetch_all(
            "SELECT * FROM user_activity WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )

    def get_recent_activity(self, limit: int = 50) -> List[Dict]:
        """Get recent activity across all users."""
        return self._fetch_all(
            """SELECT a.*, u.username 
               FROM user_activity a
               JOIN users u ON a.user_id = u.user_id
               ORDER BY a.created_at DESC LIMIT ?""",
            (limit,)
        )

    # ─── MAINTENANCE ────────────────────────────────────────────────────────
    def cleanup_expired_codes(self):
        """Deactivate expired redeem codes."""
        self._execute(
            "UPDATE redeem_codes SET is_active = 0 WHERE expires_at < ?",
            (self._now(),)
        )
        logger.info("🧹 Cleaned up expired redeem codes")

    def backup_database(self, backup_path: str):
        """Create a backup of the database."""
        import shutil
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"💾 Database backed up to: {backup_path}")

    def optimize(self):
        """Optimize the database."""
        self._execute("VACUUM")
        logger.info("🧹 Database optimized")

    def close(self):
        """Close the database connection."""
        self.conn.close()
        logger.info("🔒 Database connection closed")

    def __del__(self):
        """Destructor to ensure connection is closed."""
        try:
            self.close()
        except:
            pass

# ─── EXPORT ──────────────────────────────────────────────────────────────
__all__ = ["Database", "DB_PATH"]

# ─── CREDIT: VIP DARK GOD ───────────────────────────────────────────────
# ⚡ NEXUS STORE — Database Module
# 🔥 Made with ❤️ by @VIP_DARK_GOD
# Version 3.0.0
# ─────────────────────────────────────────────────────────────────────────