# ─── CREDIT: VIP DARK GOD ───────────────────────────────────────────────
# Telegram File Store Bot – Advanced Edition
# Brand: NEXUS
# Made with ❤️ by @VIP_DARK_GOD
# Version 3.0.0
# ─────────────────────────────────────────────────────────────────────────

import os
import sys
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from functools import wraps

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ChatMember
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
    ConversationHandler, Defaults
)

# ─── IMPORT FROM MODULES ────────────────────────────────────────────────
from config import Config
Config.from_env()  # Load environment variables from env/overrides

from database import Database

# ─── BOT SETUP ──────────────────────────────────────────────────────────
logging.basicConfig(
    format=Config.LOG_FORMAT,
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
)
logger = logging.getLogger(__name__)

# ─── SUBSCRIPTION CACHE ────────────────────────────────────────────────
_sub_cache: Dict[int, tuple] = {}

async def check_subscription(user_id: int, bot) -> List[Dict]:
    """Returns list of channels the user has NOT joined, with caching."""
    now = datetime.now()
    if user_id in _sub_cache:
        cache_time, cached = _sub_cache[user_id]
        if (now - cache_time) < timedelta(minutes=10):
            return cached
    not_joined = []
    for ch in config.FORCE_CHANNELS:
        try:
            member = await bot.get_chat_member(
                chat_id=f"@{ch['username']}", user_id=user_id
            )
            if member.status in (ChatMember.LEFT, ChatMember.BANNED, "kicked", "left"):
                not_joined.append(ch)
        except Exception:
            not_joined.append(ch)
    _sub_cache[user_id] = (now, not_joined)
    return not_joined

# ─── DECORATORS ─────────────────────────────────────────────────────────
def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not config.is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ You are not an admin.")
            return ConversationHandler.END
        return await func(update, context, *args, **kwargs)
    return wrapper

def require_subscription(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        not_joined = await check_subscription(user.id, context.bot)
        if not_joined:
            await send_join_prompt(update, context.bot, not_joined)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# ─── KEYBOARDS ──────────────────────────────────────────────────────────
def main_keyboard():
    return ReplyKeyboardMarkup([
        ["📁 Buy Files",    "🪙 My Coins"],
        ["🔗 Referral Link", "🏆 Leaderboard"],
        ["🎁 Redeem Code",   "📞 Contact Owner"],
        ["❓ Help / About"]
    ], resize_keyboard=True)

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["➕ Add File",          "🗑️ Remove File"],
        ["✏️ Edit File",         "🎫 Create Redeem Code"],
        ["💰 Give Coins",        "📢 Broadcast"],
        ["📊 Bot Stats",         "👥 All Users"],
        ["🔙 Back to Main"]
    ], resize_keyboard=True)

def subscription_keyboard(not_joined: list, ref_arg: str = ""):
    buttons = []
    for ch in not_joined:
        buttons.append([InlineKeyboardButton(
            f"➕ Join @{ch['username']}",
            url=f"https://t.me/{ch['username']}"
        )])
    cb = f"verify_{ref_arg}" if ref_arg else "verify_"
    buttons.append([InlineKeyboardButton("✅ I Joined — Verify", callback_data=cb)])
    return InlineKeyboardMarkup(buttons)

def file_list_keyboard(files, offset, total):
    """Build inline keyboard with pagination for files."""
    kb = []
    for f in files:
        kb.append([InlineKeyboardButton(
            f"📄 {f['name']}  ·  🪙 {f['price']} Coins",
            callback_data=f"buy_{f['id']}"
        )])
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"files_{offset-5}"))
    if offset + 5 < total:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"files_{offset+5}"))
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(kb)

# ─── SUBSCRIPTION PROMPT ──────────────────────────────────────────────
async def send_join_prompt(update_or_query, bot, not_joined: list, ref_arg: str = ""):
    text = (
        "🔒 <b>Access Restricted!</b>\n\n"
        "You must join all our channels before using this bot.\n\n"
        + "\n".join(f"📢 @{ch['username']}" for ch in not_joined)
        + "\n\n✅ After joining, tap <b>Verify</b> below."
    )
    kb = subscription_keyboard(not_joined, ref_arg)
    if hasattr(update_or_query, 'message') and update_or_query.message:
        await update_or_query.message.reply_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await update_or_query.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)

# ─── /start ─────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ref_arg = context.args[0] if context.args else ""

    not_joined = await check_subscription(user.id, context.bot)
    if not_joined:
        await send_join_prompt(update, context.bot, not_joined, ref_arg)
        return

    is_new = db.add_user(user.id, user.username or user.first_name)

    if is_new and ref_arg and ref_arg.isdigit():
        ref_uid = int(ref_arg)
        if ref_uid != user.id and db.user_exists(ref_uid):
            db.add_coins(ref_uid, config.REFERRAL_COINS)
            db.record_referral(ref_uid, user.id)
            db.add_coins(user.id, config.NEW_USER_REF_COINS)
            try:
                await context.bot.send_message(
                    ref_uid,
                    f"🎉 <b>New Referral!</b>\n\n"
                    f"✅ Someone joined via your link!\n"
                    f"🪙 You earned <b>{config.REFERRAL_COINS} Coins</b>!"
                )
            except Exception as e:
                logger.warning(f"Could not notify referrer: {e}")

    coins = db.get_coins(user.id)
    
    # ─── NEXUS BRANDED WELCOME ──────────────────────────────────────────
    welcome = (
        f"╔══════════════════════╗\n"
        f"      ⚡ <b>NEXUS STORE</b> ⚡\n"
        f"╚══════════════════════╝\n\n"
        f"👋 Hey <b>{user.first_name}</b>, Welcome to Nexus!\n\n"
        f"🔥 The ultimate destination for\n"
        f"   premium digital content.\n\n"
        f"🪙 Balance  :  <b>{coins} Coins</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📁 Buy Files  |  🔗 Refer & Earn\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    kb = admin_keyboard() if config.is_admin(user.id) else main_keyboard()
    await update.message.reply_text(welcome, reply_markup=kb, parse_mode=ParseMode.HTML)

# ─── VERIFY CALLBACK ────────────────────────────────────────────────────
async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    ref_arg = query.data.replace("verify_", "")

    not_joined = await check_subscription(user.id, context.bot)
    if not_joined:
        await send_join_prompt(query, context.bot, not_joined, ref_arg)
        return

    is_new = db.add_user(user.id, user.username or user.first_name)
    if is_new and ref_arg and ref_arg.isdigit():
        ref_uid = int(ref_arg)
        if ref_uid != user.id and db.user_exists(ref_uid):
            db.add_coins(ref_uid, config.REFERRAL_COINS)
            db.record_referral(ref_uid, user.id)
            db.add_coins(user.id, config.NEW_USER_REF_COINS)
            try:
                await context.bot.send_message(
                    ref_uid,
                    f"🎉 <b>New Referral!</b>\n\n"
                    f"✅ Someone joined via your link!\n"
                    f"🪙 You earned <b>{config.REFERRAL_COINS} Coins</b>!"
                )
            except Exception as e:
                logger.warning(f"Could not notify referrer: {e}")

    coins = db.get_coins(user.id)
    
    # ─── NEXUS BRANDED WELCOME ──────────────────────────────────────────
    welcome = (
        f"╔══════════════════════╗\n"
        f"      ⚡ <b>NEXUS STORE</b> ⚡\n"
        f"╚══════════════════════╝\n\n"
        f"👋 Hey <b>{user.first_name}</b>, Welcome to Nexus!\n\n"
        f"🔥 The ultimate destination for\n"
        f"   premium digital content.\n\n"
        f"🪙 Balance  :  <b>{coins} Coins</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📁 Buy Files  |  🔗 Refer & Earn\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    kb = admin_keyboard() if config.is_admin(user.id) else main_keyboard()
    await query.message.edit_text(welcome, parse_mode=ParseMode.HTML)
    await context.bot.send_message(user.id, "👇 Use the menu below:", reply_markup=kb)

# ─── BUY FILES ──────────────────────────────────────────────────────────
@require_subscription
async def buy_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = db.count_files()
    if total == 0:
        await update.message.reply_text("😕 No files available right now. Check back later!")
        return
    offset = 0
    files = db.get_files_paginated(offset=offset, limit=5)
    kb = file_list_keyboard(files, offset, total)
    await update.message.reply_text(
        "📁 <b>Select a file to buy:</b>\n\n"
        "Tap a file to purchase it with your coins.",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )

async def files_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    offset = int(query.data.replace("files_", ""))
    if offset < 0:
        offset = 0
    total = db.count_files()
    if offset >= total:
        offset = total - 5
        if offset < 0:
            offset = 0
    files = db.get_files_paginated(offset=offset, limit=5)
    kb = file_list_keyboard(files, offset, total)
    await query.message.edit_text(
        "📁 <b>Select a file to buy:</b>\n\n"
        "Tap a file to purchase it with your coins.",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )

async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "cancel":
        await query.message.edit_text("❌ Cancelled.")
        return

    file_id = int(query.data.replace("buy_", ""))
    file = db.get_file(file_id)
    if not file:
        await query.message.edit_text("❌ File not found.")
        return

    # Check subscription again
    not_joined = await check_subscription(user_id, context.bot)
    if not_joined:
        await send_join_prompt(query, context.bot, not_joined)
        return

    user_coins = db.get_coins(user_id)

    if db.already_purchased(user_id, file['id']):
        await query.message.edit_text(
            f"✅ You already own <b>{file['name']}</b>!\n⬇️ Here is your file again:",
            parse_mode=ParseMode.HTML
        )
        await send_file_to_user(query, context, file)
        return

    if user_coins < file['price']:
        await query.message.edit_text(
            f"❌ <b>Not enough coins!</b>\n\n"
            f"🪙 Your coins  : <b>{user_coins}</b>\n"
            f"💰 Required    : <b>{file['price']}</b>\n"
            f"📉 Shortfall   : <b>{file['price'] - user_coins}</b>\n\n"
            f"💡 Share your 🔗 Referral Link or use a 🎁 Redeem Code to earn more!",
            parse_mode=ParseMode.HTML
        )
        return

    db.deduct_coins(user_id, file['price'])
    db.record_purchase(user_id, file['id'], file['price'])
    remaining = db.get_coins(user_id)

    await query.message.edit_text(
        f"✅ <b>Purchase Successful!</b>\n\n"
        f"📦 File      : <b>{file['name']}</b>\n"
        f"💸 Paid      : <b>{file['price']} Coins</b>\n"
        f"🪙 Remaining : <b>{remaining} Coins</b>\n\n"
        f"⬇️ Your file is below:",
        parse_mode=ParseMode.HTML
    )
    await send_file_to_user(query, context, file)

async def send_file_to_user(query, context, file):
    chat_id = query.message.chat_id
    content = file['content']
    if content.startswith("FILE:"):
        await context.bot.send_document(
            chat_id=chat_id,
            document=content.replace("FILE:", ""),
            caption=f"📦 <b>{file['name']}</b>",
            parse_mode=ParseMode.HTML
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"📦 <b>{file['name']}</b>\n\n{content}",
            parse_mode=ParseMode.HTML
        )

# ─── MY COINS ────────────────────────────────────────────────────────────
@require_subscription
async def my_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    coins = db.get_coins(user_id)
    refs = db.get_referral_count(user_id)
    purchases = db.get_purchase_count(user_id)

    await update.message.reply_text(
        f"🪙 <b>Your Coins Dashboard</b>\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💰 Current Coins   : <b>{coins}</b>\n"
        f"👥 Total Referrals : <b>{refs}</b>\n"
        f"🛒 Total Purchases : <b>{purchases}</b>\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💡 Each referral gives you <b>{config.REFERRAL_COINS} Coins</b>!\n"
        f"🎁 New users you refer get <b>{config.NEW_USER_REF_COINS} Coins</b> too!",
        parse_mode=ParseMode.HTML
    )

# ─── REFERRAL ───────────────────────────────────────────────────────────
@require_subscription
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot_info = await context.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={user_id}"
    refs = db.get_referral_count(user_id)

    await update.message.reply_text(
        f"🔗 <b>Your Referral Link</b>\n"
        f"━━━━━━━━━━━━━━━━━\n\n"
        f"<code>{link}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Referrals    : <b>{refs}</b>\n"
        f"🪙 You earn per refer : <b>{config.REFERRAL_COINS} Coins</b>\n"
        f"🎁 New user gets      : <b>{config.NEW_USER_REF_COINS} Coins</b>\n\n"
        f"📢 Share your link and earn automatically!",
        parse_mode=ParseMode.HTML
    )

# ─── LEADERBOARD ────────────────────────────────────────────────────────
@require_subscription
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = db.get_leaderboard()
    if not top:
        await update.message.reply_text("😕 No data yet. Be the first on the leaderboard!")
        return

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    text = "🏆 <b>Top 10 Leaderboard</b> (Most Coins)\n━━━━━━━━━━━━━━━━━\n\n"
    for i, row in enumerate(top[:10]):
        text += f"{medals[i]}  <b>{row['username'] or 'User'}</b>  —  🪙 {row['coins']}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

# ─── REDEEM CODE ────────────────────────────────────────────────────────
@require_subscription
async def redeem_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎁 <b>Enter Redeem Code</b>\n\nType your code below 👇",
        parse_mode=ParseMode.HTML
    )
    return 1  # REDEEM_INPUT

async def redeem_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    user_id = update.effective_user.id
    result = db.use_redeem_code(code, user_id)
    kb = admin_keyboard() if config.is_admin(user_id) else main_keyboard()

    msgs = {
        "not_found": "❌ Invalid code! Please check and try again.",
        "already_used": "⚠️ You have already used this code!",
        "expired": "⌛ This code has expired or reached its usage limit.",
        "inactive": "❌ This code is no longer active.",
    }
    if isinstance(result, str) and result in msgs:
        await update.message.reply_text(msgs[result], reply_markup=kb)
    elif isinstance(result, int):
        await update.message.reply_text(
            f"✅ <b>Code Redeemed Successfully!</b>\n\n"
            f"🪙 <b>+{result} Coins</b> added to your account!",
            reply_markup=kb,
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(msgs["not_found"], reply_markup=kb)
    return ConversationHandler.END

# ─── CONTACT OWNER ──────────────────────────────────────────────────────
@require_subscription
async def contact_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not config.OWNER_USERNAME:
        await update.message.reply_text("😕 Owner contact is not available right now.")
        return
    await update.message.reply_text(
        f"📞 <b>Contact Owner</b>\n"
        f"━━━━━━━━━━━━━━━━━\n\n"
        f"👤 @{config.OWNER_USERNAME}\n\n"
        f"⏰ Expect a reply within 24 hours.",
        parse_mode=ParseMode.HTML
    )

# ─── HELP / ABOUT ───────────────────────────────────────────────────────
@require_subscription
async def help_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"⚡ <b>NEXUS STORE</b> ⚡\n"
        f"━━━━━━━━━━━━━━━━━\n\n"
        f"📁 <b>Buy Files</b> – Purchase premium files using coins.\n"
        f"🪙 <b>My Coins</b> – Check your balance and stats.\n"
        f"🔗 <b>Referral Link</b> – Share and earn coins.\n"
        f"🏆 <b>Leaderboard</b> – See top users.\n"
        f"🎁 <b>Redeem Code</b> – Use promo codes for free coins.\n"
        f"📞 <b>Contact Owner</b> – Get support.\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🤖 Bot by @VIP_DARK_GOD\n"
        f"✨ Version 2.0 | NEXUS",
        parse_mode=ParseMode.HTML
    )

# ─── ADMIN: ADD FILE ────────────────────────────────────────────────────
@admin_only
async def admin_add_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "➕ <b>Add New File — Step 1/3</b>\n\n📝 Enter the <b>file name</b>:",
        parse_mode=ParseMode.HTML
    )
    return 2  # ADD_FILE_NAME

async def add_file_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['file_name'] = update.message.text.strip()
    await update.message.reply_text(
        "➕ <b>Add New File — Step 2/3</b>\n\n💰 Enter the <b>price</b> in coins:",
        parse_mode=ParseMode.HTML
    )
    return 3  # ADD_FILE_PRICE

async def add_file_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['file_price'] = int(update.message.text.strip())
        await update.message.reply_text(
            "➕ <b>Add New File — Step 3/3</b>\n\n"
            "📤 Send the <b>file content</b>:\n\n"
            "• <b>Text / Link</b> → Type or paste it\n"
            "• <b>Document</b> → Upload it directly",
            parse_mode=ParseMode.HTML
        )
        return 4  # ADD_FILE_CONTENT
    except ValueError:
        await update.message.reply_text("❌ Invalid! Please enter a valid number.")
        return 3

async def add_file_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data['file_name']
    price = context.user_data['file_price']
    if update.message.document:
        content = f"FILE:{update.message.document.file_id}"
    else:
        content = update.message.text.strip()
    db.add_file(name, price, content)
    await update.message.reply_text(
        f"✅ <b>File Added!</b>\n\n📄 Name  : <b>{name}</b>\n🪙 Price : <b>{price} Coins</b>",
        reply_markup=admin_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# ─── ADMIN: REMOVE FILE ────────────────────────────────────────────────
@admin_only
async def admin_remove_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = db.get_all_files()
    if not files:
        await update.message.reply_text("😕 No files to remove.")
        return
    buttons = [[InlineKeyboardButton(
        f"🗑️ {f['name']}  ·  🪙 {f['price']}",
        callback_data=f"del_{f['id']}"
    )] for f in files]
    await update.message.reply_text(
        "🗑️ <b>Select a file to remove:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )

async def remove_file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    file_id = int(query.data.replace("del_", ""))
    file = db.get_file(file_id)
    db.remove_file(file_id)
    await query.message.edit_text(f"✅ <b>{file['name']}</b> removed successfully!", parse_mode=ParseMode.HTML)

# ─── ADMIN: EDIT FILE ──────────────────────────────────────────────────
EDIT_FILE_SELECT, EDIT_FILE_NAME, EDIT_FILE_PRICE, EDIT_FILE_CONTENT = range(10, 14)

@admin_only
async def admin_edit_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = db.get_all_files()
    if not files:
        await update.message.reply_text("😕 No files to edit.")
        return
    buttons = [[InlineKeyboardButton(
        f"✏️ {f['name']}  ·  🪙 {f['price']}",
        callback_data=f"edit_{f['id']}"
    )] for f in files]
    await update.message.reply_text(
        "✏️ <b>Select a file to edit:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )
    return EDIT_FILE_SELECT

async def edit_file_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    file_id = int(query.data.replace("edit_", ""))
    context.user_data['edit_file_id'] = file_id
    file = db.get_file(file_id)
    
    await query.message.edit_text(
        f"✏️ <b>Editing: {file['name']}</b>\n\n"
        f"Current Price: 🪙 {file['price']} Coins\n\n"
        f"<b>What would you like to change?</b>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Change Name", callback_data="edit_name")],
            [InlineKeyboardButton("💰 Change Price", callback_data="edit_price")],
            [InlineKeyboardButton("📄 Change Content", callback_data="edit_content")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")]
        ]),
        parse_mode=ParseMode.HTML
    )
    return EDIT_FILE_SELECT

async def edit_name_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text("📝 Enter the new file name:")
    return EDIT_FILE_NAME

async def edit_price_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text("💰 Enter the new price in coins:")
    return EDIT_FILE_PRICE

async def edit_content_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        "📄 Send the new file content:\n\n"
        "• <b>Text / Link</b> → Type or paste it\n"
        "• <b>Document</b> → Upload it directly",
        parse_mode=ParseMode.HTML
    )
    return EDIT_FILE_CONTENT

async def edit_name_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = context.user_data['edit_file_id']
    new_name = update.message.text.strip()
    db.update_file(file_id, name=new_name)
    await update.message.reply_text(
        f"✅ File name updated to <b>{new_name}</b>!",
        reply_markup=admin_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def edit_price_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file_id = context.user_data['edit_file_id']
        new_price = int(update.message.text.strip())
        db.update_file(file_id, price=new_price)
        await update.message.reply_text(
            f"✅ File price updated to 🪙 <b>{new_price} Coins</b>!",
            reply_markup=admin_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Invalid! Please enter a valid number.")
        return EDIT_FILE_PRICE

async def edit_content_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = context.user_data['edit_file_id']
    if update.message.document:
        content = f"FILE:{update.message.document.file_id}"
    else:
        content = update.message.text.strip()
    db.update_file(file_id, content=content)
    await update.message.reply_text(
        f"✅ File content updated successfully!",
        reply_markup=admin_keyboard(),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text("❌ Edit cancelled.")
    return ConversationHandler.END

# ─── ADMIN: CREATE REDEEM CODE ─────────────────────────────────────────
@admin_only
async def admin_create_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎫 <b>Create Code — Step 1/2</b>\n\n🪙 How many <b>coins</b> should this code give?",
        parse_mode=ParseMode.HTML
    )
    return 7  # CREATE_CODE_COINS

async def create_code_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['code_coins'] = int(update.message.text.strip())
        await update.message.reply_text(
            "🎫 <b>Create Code — Step 2/2</b>\n\n🔢 How many times can it be used? (max uses)",
            parse_mode=ParseMode.HTML
        )
        return 8  # CREATE_CODE_USES
    except ValueError:
        await update.message.reply_text("❌ Invalid! Enter a valid number.")
        return 7

async def create_code_uses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        max_uses = int(update.message.text.strip())
        coins = context.user_data['code_coins']
        code = db.create_redeem_code(coins, max_uses)
        await update.message.reply_text(
            f"✅ <b>Redeem Code Created!</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🎫 Code      : <code>{code}</code>\n"
            f"🪙 Coins     : <b>{coins}</b>\n"
            f"🔢 Max Uses  : <b>{max_uses}</b>",
            reply_markup=admin_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Invalid! Enter a valid number.")
        return 8

# ─── ADMIN: GIVE COINS ──────────────────────────────────────────────────
@admin_only
async def admin_give_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 <b>Give Coins — Step 1/2</b>\n\n👤 Enter user <b>ID or Username</b>:",
        parse_mode=ParseMode.HTML
    )
    return 9  # GIVE_COINS_USER

async def give_coins_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = db.find_user(update.message.text.strip().replace("@", ""))
    if not user:
        await update.message.reply_text("❌ User not found!")
        return ConversationHandler.END
    context.user_data['target_user'] = user
    await update.message.reply_text(
        f"✅ <b>User Found!</b>\n\n"
        f"👤 {user['username']}  |  🪙 {user['coins']} Coins\n\n"
        f"💰 <b>Step 2/2</b> — How many coins to give?",
        parse_mode=ParseMode.HTML
    )
    return 10  # GIVE_COINS_AMOUNT

async def give_coins_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text.strip())
        user = context.user_data['target_user']
        db.add_coins(user['user_id'], amount)
        new_bal = db.get_coins(user['user_id'])
        await update.message.reply_text(
            f"✅ <b>Done!</b>  🪙 {amount} Coins → <b>{user['username']}</b>\n"
            f"New balance: <b>{new_bal} Coins</b>",
            reply_markup=admin_keyboard(),
            parse_mode=ParseMode.HTML
        )
        try:
            await context.bot.send_message(
                user['user_id'],
                f"🎉 Admin added <b>{amount} Coins</b> to your account!\n"
                f"🪙 New balance: <b>{new_bal} Coins</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Invalid! Enter a valid number.")
        return 10

# ─── ADMIN: BROADCAST ──────────────────────────────────────────────────
@admin_only
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📢 Type the message to broadcast to all users:")
    return 11  # BROADCAST_MSG

async def do_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    users = db.get_all_users()
    success = fail = 0
    status = await update.message.reply_text("⏳ Sending broadcast...")
    for u in users:
        try:
            await context.bot.send_message(
                u['user_id'],
                f"📢 <b>NEXUS Announcement</b>\n\n{msg}",
                parse_mode=ParseMode.HTML
            )
            success += 1
        except Exception:
            fail += 1
        # Avoid rate limiting
        if (success + fail) % 30 == 0:
            await asyncio.sleep(1)
    await status.edit_text(
        f"✅ <b>Broadcast Complete!</b>\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✔️ Sent   : <b>{success}</b>\n"
        f"❌ Failed : <b>{fail}</b>\n"
        f"👥 Total  : <b>{len(users)}</b>",
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# ─── ADMIN: STATS & USERS ──────────────────────────────────────────────
@admin_only
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = db.get_stats()
    await update.message.reply_text(
        f"📊 <b>NEXUS Bot Statistics</b>\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users     : <b>{s['users']}</b>\n"
        f"📁 Total Files     : <b>{s['files']}</b>\n"
        f"🛒 Total Purchases : <b>{s['purchases']}</b>\n"
        f"🎫 Active Codes    : <b>{s['active_codes']}</b>",
        f"💰 Total Spent     : 🪙 {s['total_coins_spent']:,}",
        f"🔄 Total Referrals : <b>{s['total_referrals']}</b>",
        parse_mode=ParseMode.HTML
    )

@admin_only
async def admin_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_users()
    text = f"👥 <b>All Users ({len(users)} total)</b>\n━━━━━━━━━━━━━━━━━\n\n"
    for u in users[:50]:
        text += f"• <code>{u['user_id']}</code>  @{u['username']}  🪙{u['coins']}\n"
    if len(users) > 50:
        text += f"\n... and {len(users)-50} more."
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

# ─── CANCEL ─────────────────────────────────────────────────────────────
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    kb = admin_keyboard() if config.is_admin(user_id) else main_keyboard()
    await update.message.reply_text("❌ Action cancelled.", reply_markup=kb)
    return ConversationHandler.END

# ─── TEXT ROUTER ────────────────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text
    user_id = update.effective_user.id
    is_admin = config.is_admin(user_id)

    routes = {
        "📁 Buy Files": buy_files,
        "🪙 My Coins": my_coins,
        "🔗 Referral Link": referral,
        "🏆 Leaderboard": leaderboard,
        "📞 Contact Owner": contact_owner,
        "❓ Help / About": help_about,
    }
    if text in routes:
        await routes[text](update, context)
    elif text == "📊 Bot Stats" and is_admin:
        await admin_stats(update, context)
    elif text == "👥 All Users" and is_admin:
        await admin_all_users(update, context)
    elif text == "✏️ Edit File" and is_admin:
        await admin_edit_file(update, context)
    elif text == "🔙 Back to Main":
        await update.message.reply_text("🏠 Back to main menu!", reply_markup=main_keyboard())

# ─── MAIN ──────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(config.BOT_TOKEN).defaults(
        Defaults(parse_mode=ParseMode.HTML)
    ).build()

    # ── Commands ──
    app.add_handler(CommandHandler("start", start))

    # ── Callbacks ──
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify_"))
    app.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(files_page_callback, pattern="^files_"))
    app.add_handler(CallbackQueryHandler(remove_file_callback, pattern="^del_"))
    
    # Edit file callbacks
    app.add_handler(CallbackQueryHandler(edit_file_select_callback, pattern="^edit_"))
    app.add_handler(CallbackQueryHandler(edit_name_prompt, pattern="^edit_name$"))
    app.add_handler(CallbackQueryHandler(edit_price_prompt, pattern="^edit_price$"))
    app.add_handler(CallbackQueryHandler(edit_content_prompt, pattern="^edit_content$"))
    app.add_handler(CallbackQueryHandler(cancel_edit, pattern="^cancel_edit$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: u.answer(), pattern="^cancel$"))

    # ── Conversations ──
    # Redeem
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎁 Redeem Code$"), redeem_start)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, redeem_process)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # Add File
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Add File$"), admin_add_file)],
        states={
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_file_name)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_file_price)],
            4: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_file_content),
                MessageHandler(filters.Document.ALL, add_file_content)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # Edit File
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^✏️ Edit File$"), admin_edit_file)],
        states={
            EDIT_FILE_SELECT: [
                CallbackQueryHandler(edit_name_prompt, pattern="^edit_name$"),
                CallbackQueryHandler(edit_price_prompt, pattern="^edit_price$"),
                CallbackQueryHandler(edit_content_prompt, pattern="^edit_content$"),
                CallbackQueryHandler(cancel_edit, pattern="^cancel_edit$"),
            ],
            EDIT_FILE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_name_process)],
            EDIT_FILE_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_price_process)],
            EDIT_FILE_CONTENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_content_process),
                MessageHandler(filters.Document.ALL, edit_content_process)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # Create Code
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎫 Create Redeem Code$"), admin_create_code)],
        states={
            7: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_code_coins)],
            8: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_code_uses)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # Give Coins
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💰 Give Coins$"), admin_give_coins)],
        states={
            9: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_coins_user)],
            10: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_coins_amount)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # Broadcast
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📢 Broadcast$"), admin_broadcast)],
        states={11: [MessageHandler(filters.TEXT & ~filters.COMMAND, do_broadcast)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # Remove File
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🗑️ Remove File$"), admin_remove_file)],
        states={},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    # ── Text Handler ──
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("✅ NEXUS Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

# ─── CREDIT: VIP DARK GOD ───────────────────────────────────────────────
# ⚡ NEXUS STORE — Advanced File Store Bot
# 🔥 Made with ❤️ by @VIP_DARK_GOD
# 📌 Brand: NEXUS
# ─────────────────────────────────────────────────────────────────────────