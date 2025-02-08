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

# 🔹 Session storage
session_strings = []

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
    global session_strings

    if hasattr(bot, 'expected_session_count') and len(session_strings) < bot.expected_session_count:
        session_input = message.text.strip()

        # Split the input and check if the correct number of session strings were provided
        new_sessions = session_input.split()

        if len(new_sessions) == bot.expected_session_count:
            session_strings.extend(new_sessions)
            await message.reply(f"✅ {len(new_sessions)} session strings added successfully.")
            
            # Reset expected session count
            del bot.expected_session_count

            # Send confirmation
            await message.reply("✅ All session strings have been added! Now, please provide the target username for reporting.")
        else:
            await message.reply(f"⚠️ You need to provide exactly {bot.expected_session_count} session strings. Please try again.")
    else:
        await message.reply("⚠️ Please start by using the /make_config <number> command to add session strings.")

# 🎯 Report Command (Target username and quantity)
@bot.on_message(filters.command("report"))
async def report_user(client, message):
    if not session_strings:
        return await message.reply("⚠️ No session added! Please use /make_config first.")

    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply("⚠️ Usage: `/report @username`")

    username = args[1]

    # Ask for report count
    await message.reply(f"⚠️ How many reports would you like to send against @{username}? Please reply with the number (e.g., 10, 50, 100).")

    # Store the username for next steps
    bot.target_username = username

# 🎯 Collect Report Quantity
@bot.on_message(filters.text)
async def collect_report_count(client, message):
    if hasattr(bot, 'target_username'):
        username = bot.target_username
        count = message.text.strip()

        try:
            count = int(count)
            if count not in [10, 50, 100, 200]:
                raise ValueError("Invalid count")

            await message.reply(f"⚠️ You selected {count} reports for @{username}. Now, please select a reason for reporting.")

            # Reset username and count after confirmation
            del bot.target_username
            bot.report_count = count

            # Proceed with the reason selection
            report_buttons = [
                [InlineKeyboardButton("Spam", callback_data=f"report:{username}:spam")],
                [InlineKeyboardButton("Violence", callback_data=f"report:{username}:violence")],
                [InlineKeyboardButton("Child abuse", callback_data=f"report:{username}:child_abuse")],
                [InlineKeyboardButton("Other", callback_data=f"report:{username}:other")]
            ]
            await message.reply(
                f"⚠️ Select a reason to report @{username}:",
                reply_markup=InlineKeyboardMarkup(report_buttons)
            )
        except ValueError:
            await message.reply("⚠️ Please enter a valid number of reports (10, 50, 100, 200).")

# 🎯 Report Handler (User clicks a reason)
@bot.on_callback_query(filters.regex("^report:"))
async def handle_report(client, callback_query):
    username = callback_query.data.split(":")[1]
    reason_code = callback_query.data.split(":")[2]

    # Use the stored count from previous step
    count = bot.report_count  # Set this in the earlier step where you handle report count

    # Map the reason to the correct report reason
    reason_mapping = {
        "spam": InputReportReasonSpam(),
        "violence": InputReportReasonViolence(),
        "child_abuse": InputReportReasonChildAbuse(),
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

        await callback_query.message.edit_text(f"✅ Successfully sent {count} reports against @{username} for {reason_code.replace('_', ' ').title()}!")

    except Exception as e:
        logging.error(f"Error reporting user: {e}")
        await callback_query.answer("⚠️ Failed to send reports.", show_alert=True)

bot.run()
