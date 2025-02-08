import asyncio
import logging
from pyrogram.raw import functions
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

# 🎯 Bot Client
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Userbot session storage
userbot = None

# 🎯 Start Command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    welcome_text = "👋 Welcome! Use /addsession <session_string> to add a session."
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
1️⃣ Use `/addsession <session_string>` to add a session.
2️⃣ Use `/report @username`, `/report <user_id>`, or `/report <message_link>` to report a user or message.
3️⃣ Select a reason for reporting from the buttons.
4️⃣ Reports will be sent automatically.
"""
    if isinstance(update, filters.callback_query):
        await update.message.edit_text(help_text)
    else:
        await update.reply(help_text)

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

        # Creating a new userbot session
        userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
        
        # Starting the userbot session asynchronously
        await userbot.start()

        # Use invoke() to send Ping request
        await userbot.invoke(functions.Ping(ping_id=0))

        await message.reply("✅ Session added successfully! Now you can use /report.")
    
    except Exception as e:
        logging.error(f"Error adding session: {e}")
        await message.reply(f"⚠️ Failed to add session. Error: {e}")

# 🎯 Report Command (User chooses a reason)
@bot.on_message(filters.command("report"))
async def report_user(client, message):
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply("⚠️ Usage: `/report @username`, `/report <user_id>`, or `/report <message_link>`")

    input_data = args[1]
    
    # Check if input is a message link, username or user_id
    if "t.me" in input_data:  # This indicates it's a message link
        try:
            # Extracting message ID and chat_id from the message link
            link_parts = input_data.split("/")
            if len(link_parts) < 5:
                return await message.reply("⚠️ Invalid message link format.")
            
            chat_id = link_parts[3]  # Channel/Group username or ID
            message_id = int(link_parts[4])  # Message ID

            buttons = [
                [InlineKeyboardButton("I don't like it", callback_data=f"report:{chat_id}:{message_id}:other")],
                [InlineKeyboardButton("Child abuse", callback_data=f"report:{chat_id}:{message_id}:child_abuse")],
                [InlineKeyboardButton("Violence", callback_data=f"report:{chat_id}:{message_id}:violence")],
                [InlineKeyboardButton("Illegal goods", callback_data=f"report:{chat_id}:{message_id}:illegal_goods")],
                [InlineKeyboardButton("Illegal adult content", callback_data=f"report:{chat_id}:{message_id}:porn")],
                [InlineKeyboardButton("Personal data", callback_data=f"report:{chat_id}:{message_id}:personal_data")],
                [InlineKeyboardButton("Terrorism", callback_data=f"report:{chat_id}:{message_id}:fake")],
                [InlineKeyboardButton("Scam or spam", callback_data=f"report:{chat_id}:{message_id}:spam")],
                [InlineKeyboardButton("Copyright", callback_data=f"report:{chat_id}:{message_id}:copyright")],
                [InlineKeyboardButton("Other", callback_data=f"report:{chat_id}:{message_id}:other")]
            ]

            await message.reply(
                f"⚠️ Select a reason to report the message in {chat_id}:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            logging.error(f"Error processing the message link: {e}")
            await message.reply("⚠️ Failed to process the message link.")
    
    elif input_data.isdigit():  # This indicates it's a user_id
        user_id = int(input_data)

        buttons = [
            [InlineKeyboardButton("I don't like it", callback_data=f"report:{user_id}:other")],
            [InlineKeyboardButton("Child abuse", callback_data=f"report:{user_id}:child_abuse")],
            [InlineKeyboardButton("Violence", callback_data=f"report:{user_id}:violence")],
            [InlineKeyboardButton("Illegal goods", callback_data=f"report:{user_id}:illegal_goods")],
            [InlineKeyboardButton("Illegal adult content", callback_data=f"report:{user_id}:porn")],
            [InlineKeyboardButton("Personal data", callback_data=f"report:{user_id}:personal_data")],
            [InlineKeyboardButton("Terrorism", callback_data=f"report:{user_id}:fake")],
            [InlineKeyboardButton("Scam or spam", callback_data=f"report:{user_id}:spam")],
            [InlineKeyboardButton("Copyright", callback_data=f"report:{user_id}:copyright")],
            [InlineKeyboardButton("Other", callback_data=f"report:{user_id}:other")]
        ]
        
        await message.reply(
            f"⚠️ Select a reason to report user with ID {user_id}:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    else:  # This indicates it's a username
        username = input_data

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
    
    if len(data) < 4:
        return

    identifier = data[1]  # Either username, user_id, or chat_id
    message_id = int(data[2]) if len(data) > 2 else None
    reason_code = data[3]

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
        if message_id:  # Reporting a specific message
            # Resolving the peer (group/channel) and reporting the specific message
            peer = await userbot.resolve_peer(identifier)
            await userbot.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))
        
        else:  # Reporting a user
            entity = await userbot.get_users(identifier)
            peer = await userbot.resolve_peer(entity.id)
            await userbot.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))

        await callback_query.message.edit_text(f"✅ Successfully reported for {reason_code.replace('_', ' ').title()}!")

    except Exception as e:
        logging.error(f"Error reporting: {e}")
        await callback_query.answer("⚠️ Failed to report.", show_alert=True)

# 🎯 Ping Command
@bot.on_message(filters.command("ping"))
async def ping(client, message):
    await message.reply("🏓 Pong! The bot is active.")

bot.run()
