import asyncio
import logging
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import (
    InputReportReasonOther, InputReportReasonSpam, InputReportReasonViolence,
    InputReportReasonChildAbuse, InputReportReasonPornography, InputReportReasonCopyright,
    InputReportReasonFake, InputReportReasonIllegalDrugs, InputReportReasonPersonalDetails
)

# 📌 Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🛠 Configuration
API_ID = 23120489
API_HASH = "ccfc629708e2f8a05c31ebe7961b5f92"
BOT_TOKEN = "7984449177:AAEjwcdh-OlUhJ5E_L26jSZfmCPFDuNK7d4"

# 📂 SQLite Database setup
conn = sqlite3.connect('bot_config.db')
cursor = conn.cursor()

# Create table to store user data (session strings and config)
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_configs (
    user_id INTEGER PRIMARY KEY,
    session_strings TEXT,
    config_made BOOLEAN
)
""")
conn.commit()

# 🎯 Bot Client
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Session storage and flag to check if sessions are added
session_strings = []
is_session_added = False  # Flag to track if sessions are added

# Function to check if a user has already made a config
def check_user_config(user_id):
    cursor.execute("SELECT * FROM user_configs WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    return user_data

# Function to update user config in the database
def update_user_config(user_id, session_strings, config_made):
    cursor.execute("""
    INSERT OR REPLACE INTO user_configs (user_id, session_strings, config_made)
    VALUES (?, ?, ?)
    """, (user_id, session_strings, config_made))
    conn.commit()

# 🎯 Start Command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    welcome_text = "👋 Welcome! Use /make_config <number> to add multiple session strings."
    buttons = [[InlineKeyboardButton("❓ Help", callback_data="show_help")]]
    
    await message.reply(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🎯 Help Command (Button Click or /help)
@bot.on_message(filters.command("help"))
@bot.on_callback_query(filters.regex("^show_help$"))
async def help_command(client, update):
    help_text = """
📌 *How to use this bot:*
1️⃣ Use `/make_config <number>` to add session strings (e.g., `/make_config 5`).
2️⃣ Use `/report @username` to report a user.
3️⃣ Select a reason for reporting from the buttons.
4️⃣ Choose the number of reports to send (e.g., 10, 50, 100, 200).

✅ You can send multiple reports like 10, 50, 100, or 200 at once!
"""
    if isinstance(update, filters.callback_query):
        await update.message.edit_text(help_text)
    else:
        await update.reply(help_text)

# 🎯 Make Config Command
@bot.on_message(filters.command("make_config"))
async def make_config(client, message):
    global is_session_added  # Use global variable to track session status

    # Check if sessions are already added
    user_id = message.from_user.id
    user_data = check_user_config(user_id)
    if user_data and user_data[2]:  # If config_made is True
        return await message.reply("⚠️ Sessions are already configured! You can now start reporting.")

    args = message.text.split()

    if len(args) < 2:
        return await message.reply("⚠️ Usage: `/make_config <number>` where <number> is the count of session strings you want to add.")

    try:
        session_count = int(args[1])  # Number of session strings
    except ValueError:
        return await message.reply("⚠️ Please provide a valid number.")

    await message.reply(f"⚙️ Please provide {session_count} session strings in the following format (separate by spaces):\n\n<session_string_1> <session_string_2> ...")

    # Store expected session count
    session_strings.clear()  # Clear previous session strings
    bot.expected_session_count = session_count

# 🎯 Collect Session Strings
@bot.on_message(filters.text)
async def collect_session_strings(client, message):
    global session_strings, is_session_added

    if hasattr(bot, 'expected_session_count') and len(session_strings) < bot.expected_session_count:
        session_input = message.text.strip()

        # Split the input and check if the correct number of session strings were provided
        new_sessions = session_input.split()

        if len(new_sessions) == bot.expected_session_count:
            session_strings.extend(new_sessions)
            await message.reply(f"✅ {len(new_sessions)} session strings added successfully.")
            
            # Save to database
            update_user_config(message.from_user.id, ' '.join(new_sessions), True)

            # Reset expected session count and mark sessions as added
            del bot.expected_session_count
            is_session_added = True  # Set flag to True

            # Send confirmation
            await message.reply("✅ All session strings have been added! You can now proceed with reporting.")
        else:
            await message.reply(f"⚠️ You need to provide exactly {bot.expected_session_count} session strings. Please try again.")
    else:
        await message.reply("⚠️ Please start by using the /make_config <number> command to add session strings.")

# 🎯 Report Command (User chooses a reason)
@bot.on_message(filters.command("report"))
async def report_user(client, message):
    if not session_strings:
        return await message.reply("⚠️ No session added! Please use /make_config first.")

    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply("⚠️ Usage: `/report @username`")

    username = args[1]

    buttons = [
        [InlineKeyboardButton("I don't like it", callback_data=f"report:{username}:other")],
        [InlineKeyboardButton("Child abuse", callback_data=f"report:{username}:child_abuse")],
        [InlineKeyboardButton("Violence", callback_data=f"report:{username}:violence")],
        [InlineKeyboardButton("Illegal goods", callback_data=f"report:{username}:illegal_goods")],
        [InlineKeyboardButton("Illegal adult content", callback_data=f"report:{username}:porn")],
        [InlineKeyboardButton("Personal data", callback_data=f"report:{username}:personal_data")],
        [InlineKeyboardButton("Terrorism", callback_data=f"report:{username}:fake")],
        [InlineKeyboardButton("Scam or spam", callback_data=f"report:{username}:spam")],
        [InlineKeyboardButton("Copyright", callback_data=f"report:{username}:copyright")],
        [InlineKeyboardButton("Other", callback_data=f"report:{username}:other")]
    ]
    
    await message.reply(
        f"⚠️ Select a reason to report {username}:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🎯 Report Handler (User clicks a reason)
@bot.on_callback_query(filters.regex("^report:"))
async def handle_report(client, callback_query):
    global session_strings

    if not session_strings:
        return await callback_query.answer("⚠️ No session added! Use /make_config first.", show_alert=True)

    data = callback_query.data.split(":")
    
    if len(data) < 3:
        return

    username = data[1]
    reason_code = data[2]

    reason_mapping = {
        "spam": InputReportReasonSpam(),
        "violence": InputReportReasonViolence(),
        "child_abuse": InputReportReasonChildAbuse(),
        "porn": InputReportReasonPornography(),
        "copyright": InputReportReasonCopyright(),
        "fake": InputReportReasonFake(),
        "illegal_goods": InputReportReasonIllegalDrugs(),
        "personal_data": InputReportReasonPersonalDetails(),
        "other": InputReportReasonOther()
    }

    reason = reason_mapping.get(reason_code, InputReportReasonOther())

    # 🎯 Choose number of reports
    buttons = [
        [InlineKeyboardButton("10 Reports", callback_data=f"sendreport:{username}:{reason_code}:10")],
        [InlineKeyboardButton("50 Reports", callback_data=f"sendreport:{username}:{reason_code}:50")],
        [InlineKeyboardButton("100 Reports", callback_data=f"sendreport:{username}:{reason_code}:100")],
        [InlineKeyboardButton("200 Reports", callback_data=f"sendreport:{username}:{reason_code}:200")]
    ]

    await callback_query.message.edit_text(
        f"✅ Selected reason: {reason_code.replace('_', ' ').title()}\n\nSelect number of reports to send:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🎯 Bulk Report Handler
@bot.on_callback_query(filters.regex("^sendreport:"))
async def send_bulk_reports(client, callback_query):
    global session_strings

    if not session_strings:
        return await callback_query.answer("⚠️ No session added! Use /make_config first.", show_alert=True)

    data = callback_query.data.split(":")
    
    if len(data) < 4:
        return

    username = data[1]
    reason_code = data[2]
    count = int(data[3])

    reason_mapping = {
        "spam": InputReportReasonSpam(),
        "violence": InputReportReasonViolence(),
        "child_abuse": InputReportReasonChildAbuse(),
        "porn": InputReportReasonPornography(),
        "copyright": InputReportReasonCopyright(),
        "fake": InputReportReasonFake(),
        "illegal_goods": InputReportReasonIllegalDrugs(),
        "personal_data": InputReportReasonPersonalDetails(),
        "other": InputReportReasonOther()
    }

    reason = reason_mapping.get(reason_code, InputReportReasonOther())

    try:
        for session_string in session_strings:
            userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
            await userbot.start()

            entity = await userbot.get_users(username)
            peer = await userbot.resolve_peer(entity.id)

            for i in range(count):
                await userbot.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))
                await asyncio.sleep(0.5)

            await userbot.stop()

        await callback_query.message.edit_text(f"✅ Successfully sent {count} reports against {username} for {reason_code.replace('_', ' ').title()}!")

    except Exception as e:
        logging.error(f"Error reporting user: {e}")
        await callback_query.answer("⚠️ Failed to send reports.", show_alert=True)

bot.run()
