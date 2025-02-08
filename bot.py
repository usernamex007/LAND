import asyncio
import logging
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
API_ID = 28795512  
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7984449177:AAFq5h_10P6yLlqv5CsjB_WJ8dRLK7U_JIw"

# 🎯 Bot Client
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Userbot session storage
userbot = None

# 🎯 Start Command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("👋 Welcome! Use /addsession <session_string> to add a session.")

# 🎯 Help Command
@bot.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = """
📌 *How to use this bot:*
1️⃣ Use `/addsession <session_string>` to add a session.
2️⃣ Use `/report @username` to report a user.
3️⃣ Select a reason for reporting from the buttons.
4️⃣ Select the number of reports to send.

✅ You can send multiple reports like 10, 50, 100, or 200 at once!
"""
    await message.reply(help_text)

# 🎯 Add Session Command
@bot.on_message(filters.command("addsession"))
async def add_session(client, message):
    global userbot

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("⚠️ Usage: `/addsession <session_string>`")

    session_string = args[1]

    try:
        if userbot:
            await userbot.stop()

        userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
        await userbot.start()
        
        await message.reply("✅ Session added successfully! Now you can use /report.")
    
    except Exception as e:
        logging.error(f"Error adding session: {e}")
        await message.reply(f"⚠️ Failed to add session. Error: {e}")

# 🎯 Report Command (User chooses a reason)
@bot.on_message(filters.command("report"))
async def report_user(client, message):
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
@bot.on_callback_query()
async def handle_report(client, callback_query):
    global userbot

    if not userbot:
        return await callback_query.answer("⚠️ No session added! Use /addsession first.", show_alert=True)

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
@bot.on_callback_query()
async def send_bulk_reports(client, callback_query):
    global userbot

    if not userbot or not userbot.is_connected:
        return await callback_query.answer("⚠️ No session added! Use /addsession first.", show_alert=True)

    if not callback_query.data.startswith("sendreport:"):
        return

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
        entity = await userbot.get_users(username)
        peer = await userbot.resolve_peer(entity.id)

        for i in range(count):
            await userbot.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))
            await asyncio.sleep(1.5)  # Telegram API Limit Handling

        await callback_query.message.edit_text(f"✅ Successfully sent {count} reports against {username} for {reason_code.replace('_', ' ').title()}!")

    except Exception as e:
        logging.error(f"Error reporting user: {e}")
        await callback_query.answer("⚠️ Failed to send reports.", show_alert=True)

bot.run()
