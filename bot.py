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
API_ID = 23120489
API_HASH = "ccfc629708e2f8a05c31ebe7961b5f92"
BOT_TOKEN = "7984449177:AAFq5h_10P6yLlqv5CsjB_WJ8dRLK7U_JIw"

# 🎯 Bot Client
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Userbot session storage
userbot = None

# 🎯 Start Command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    welcome_text = "👋 Welcome! Use /make_config to configure your session settings."
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
1️⃣ Use `/make_config <number>` to specify how many session strings you want to add.
2️⃣ Then, use `/addsession` to add those sessions.
3️⃣ Use `/report @username` to report a user.
4️⃣ Select a reason for reporting from the buttons.
5️⃣ Reports will be sent automatically.

✅ You can send multiple reports like 10, 50, 100, or 200 at once!
"""
    if isinstance(update, filters.callback_query):
        await update.message.edit_text(help_text)
    else:
        await update.reply(help_text)

# 🎯 Make Config Command
@bot.on_message(filters.command("make_config"))
async def make_config(client, message):
    # Asking user how many sessions they want to add
    await message.reply("⚙️ How many session strings do you want to add? (e.g., 1, 10, 100)")

# 🎯 Add Session Command
@bot.on_message(filters.command("addsession"))
async def add_session(client, message):
    # Taking input for how many session strings user wants to add
    user_input = message.text.split()

    if len(user_input) < 2:
        return await message.reply("⚠️ Usage: `/addsession <number_of_sessions>`")

    try:
        num_sessions = int(user_input[1])  # Number of sessions user wants to add
        await message.reply(f"✅ You want to add {num_sessions} session(s). Please send your session strings now.")
        
        # Now waiting for user to send session strings
        for i in range(num_sessions):
            session_message = await client.listen(message.chat.id)
            session_string = session_message.text
            try:
                # Add session string logic here
                if userbot:
                    await userbot.stop()
                userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
                await userbot.start()
                await message.reply(f"✅ Session {i+1} added successfully: {session_string}")
            except Exception as e:
                logging.error(f"Error adding session: {e}")
                await message.reply(f"⚠️ Failed to add session {i+1}. Error: {e}")

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply(f"⚠️ An error occurred while processing your request: {e}")

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
@bot.on_callback_query(filters.regex("^report:"))
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
@bot.on_callback_query(filters.regex("^sendreport:"))
async def send_bulk_reports(client, callback_query):
    global userbot

    if not userbot:
        return await callback_query.answer("⚠️ No session added! Use /addsession first.", show_alert=True)

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
            await asyncio.sleep(0.5)  

        await callback_query.message.edit_text(f"✅ Successfully sent {count} reports against {username} for {reason_code.replace('_', ' ').title()}!")

    except Exception as e:
        logging.error(f"Error reporting user: {e}")
        await callback_query.answer("⚠️ Failed to send reports.", show_alert=True)

bot.run()
