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
API_ID = 28795512  # अपना API_ID डालें
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7854222423:AAENyTD0z0UQ95hobcR_CFGKeDfhrwbH2MU"

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

✅ Once a session is added, reports will be sent using the user session.
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
        # Existing userbot को पहले रोकें
        if userbot:
            await userbot.stop()

        # नया userbot शुरू करें
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

    # 🎯 Generate buttons for report reasons
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

# 🎯 Report Handler (User clicks a button)
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

    # 🎯 Mapping report reasons
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
        # 🎯 Get user details
        entity = await userbot.get_users(username)
        peer = await userbot.resolve_peer(entity.id)

        # 🎯 Report user
        await userbot.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))
        await callback_query.message.edit_text(f"✅ Successfully reported {username} for {reason_code.replace('_', ' ').title()}.")

    except Exception as e:
        logging.error(f"Error reporting user: {e}")
        await callback_query.answer("⚠️ Failed to report user.", show_alert=True)

# 🎯 Start Bot Properly Without asyncio.run()
async def main():
    await bot.start()
    logging.info("✅ Bot started successfully!")

    try:
        await asyncio.Event().wait()  # Keeps bot running
    except asyncio.CancelledError:
        logging.info("❌ Stopping Bot...")

    finally:
        if userbot:
            await userbot.stop()
        await bot.stop()
        logging.info("✅ Bot stopped successfully!")

# ✅ Properly Handle Event Loop
if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())  
    except KeyboardInterrupt:
        logging.info("❌ Bot manually stopped.")
        loop.run_until_complete(bot.stop())
        if userbot:
            loop.run_until_complete(userbot.stop())
