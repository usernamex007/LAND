import asyncio
import logging
import signal
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

# Logging setup
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Bot configuration
API_ID = 23120489  
API_HASH = "ccfc629708e2f8a05c31ebe7961b5f92"
BOT_TOKEN = "7984449177:AAEjwcdh-OlUhJ5E_L26jSZfmCPFDuNK7d4"

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = None

# Start command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Help", callback_data="help")]
    ])
    await message.reply("👋 Welcome! Use /addsession <session_string> to add a session.", reply_markup=buttons)

# Help command
@bot.on_callback_query(filters.regex("^help$"))
@bot.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = """
📌 *How to use this bot:*
1️⃣ Use `/addsession <session_string>` to add a session.
2️⃣ Use `/report @username` to report a user.
3️⃣ Use `/report <message_link>` to report a specific message.
4️⃣ Select a reason for reporting from the buttons.
5️⃣ Select the number of reports to send (10, 50, 100, 200).

✅ The bot will notify you when reports are successfully sent.
"""
    await message.reply(help_text)

# Add session command
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

# Report command (User chooses a reason)
@bot.on_message(filters.command("report"))
async def report_user(client, message):
    args = message.text.split()

    if len(args) < 2:
        return await message.reply("⚠️ Usage: `/report @username` or `/report <message_link>`")

    target = args[1]

    if "t.me/" in target:
        return await handle_message_link(message, target)

    buttons = [
        [InlineKeyboardButton("Spam", callback_data=f"report:{target}:spam")],
        [InlineKeyboardButton("Child abuse", callback_data=f"report:{target}:child_abuse")],
        [InlineKeyboardButton("Violence", callback_data=f"report:{target}:violence")],
        [InlineKeyboardButton("Illegal goods", callback_data=f"report:{target}:illegal_goods")],
        [InlineKeyboardButton("Adult content", callback_data=f"report:{target}:porn")],
        [InlineKeyboardButton("Personal data", callback_data=f"report:{target}:personal_data")],
        [InlineKeyboardButton("Terrorism", callback_data=f"report:{target}:fake")],
        [InlineKeyboardButton("Copyright", callback_data=f"report:{target}:copyright")],
        [InlineKeyboardButton("Other", callback_data=f"report:{target}:other")]
    ]

    await message.reply(
        f"⚠️ Select a reason to report {target}:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Message link handling
async def handle_message_link(message, link):
    global userbot

    if not userbot:
        return await message.reply("⚠️ No session added! Use /addsession first.")

    match = re.search(r"t.me/([^/]+)/(\d+)", link)
    if not match:
        return await message.reply("⚠️ Invalid message link format.")

    chat_username, message_id = match.groups()

    try:
        chat = await userbot.get_chat(chat_username)
        buttons = [
            [InlineKeyboardButton("Spam", callback_data=f"reportmsg:{chat.id}:{message_id}:spam")],
            [InlineKeyboardButton("Child abuse", callback_data=f"reportmsg:{chat.id}:{message_id}:child_abuse")],
            [InlineKeyboardButton("Violence", callback_data=f"reportmsg:{chat.id}:{message_id}:violence")]
        ]

        await message.reply(
            "⚠️ Select a reason to report this message:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logging.error(f"Error fetching message: {e}")
        await message.reply("⚠️ Failed to fetch message.")

# Bulk report handler
@bot.on_callback_query(filters.regex("^reportmsg:|^report:"))
async def send_bulk_reports(client, callback_query):
    global userbot

    if not userbot:
        return await callback_query.answer("⚠️ No session added! Use /addsession first.", show_alert=True)

    data = callback_query.data.split(":")
    
    if "reportmsg" in data[0]:
        chat_id, message_id, reason_code = data[1], int(data[2]), data[3]
    else:
        target, reason_code = data[1], data[2]

    reason_mapping = {
        "spam": "Spam",
        "violence": "Violence",
        "child_abuse": "Child Abuse",
        "porn": "Adult Content",
        "copyright": "Copyright",
        "fake": "Terrorism",
        "illegal_goods": "Illegal Goods",
        "personal_data": "Personal Data",
        "other": "Other"
    }

    reason = reason_mapping.get(reason_code, "Other")

    buttons = [
        [InlineKeyboardButton("10 Reports", callback_data=f"sendreport:{callback_query.data}:10")],
        [InlineKeyboardButton("50 Reports", callback_data=f"sendreport:{callback_query.data}:50")],
        [InlineKeyboardButton("100 Reports", callback_data=f"sendreport:{callback_query.data}:100")],
        [InlineKeyboardButton("200 Reports", callback_data=f"sendreport:{callback_query.data}:200")]
    ]

    await callback_query.message.edit_text(
        f"✅ Selected reason: {reason}\n\nSelect number of reports to send:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Ping command
@bot.on_message(filters.command("ping"))
async def ping(client, message):
    await message.reply("🏓 Pong! The bot is active.")

# Graceful shutdown function
async def main():
    try:
        await bot.start()
        logging.info("✅ Bot started successfully!")
        
        # Use a signal handler to gracefully shutdown
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(bot.stop()))

        # Keep the bot alive
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logging.info("🚫 Bot stopped by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
