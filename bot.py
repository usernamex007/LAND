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
import pymongo

# 📌 Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🛠 Configuration
API_ID = 23120489
API_HASH = "ccfc629708e2f8a05c31ebe7961b5f92"
BOT_TOKEN = "7782975743:AAGuVZ4Ip9mk8DwUtYYLb8nYD1T4PHugkDU"

# MongoDB Configuration
client_mongo = pymongo.MongoClient("mongodb+srv://sanatanixtech:sachin@sachin.9guym.mongodb.net/?retryWrites=true&w=majority&appName=Sachin")
db = client_mongo['report_bot_db']
sessions_collection = db['sessions']
reports_collection = db['reports']

# 🎯 Bot Client
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Session storage and flag to check if sessions are added
session_strings = []
is_session_added = False  # Flag to track if sessions are added

# 🎯 Start Command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    welcome_text = "👋 स्वागत है! /make_config <number> का उपयोग करें ताकि आप session strings जोड़ सकें।"
    await message.reply(welcome_text)

# 🎯 Make Config Command
@bot.on_message(filters.command("make_config"))
async def make_config(client, message):
    global is_session_added  # Use global variable to track session status

    # Check if sessions are already added
    if is_session_added:
        return await message.reply("⚠️ सत्र पहले ही जोड़ दिए गए हैं! आप अब रिपोर्ट करना शुरू कर सकते हैं।")

    args = message.text.split()

    if len(args) < 2:
        return await message.reply("⚠️ उपयोग: `/make_config <number>` जहाँ <number> वह संख्या है जो आप जोड़ना चाहते हैं।")

    try:
        session_count = int(args[1])  # Number of session strings
    except ValueError:
        return await message.reply("⚠️ कृपया सही संख्या प्रदान करें।")

    await message.reply(f"⚙️ कृपया {session_count} session strings निम्नलिखित प्रारूप में प्रदान करें (स्पेस से अलग करें):\n\n<session_string_1> <session_string_2> ...")

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
            await message.reply(f"✅ {len(new_sessions)} session strings सफलतापूर्वक जोड़ी गईं।")
            
            # Reset expected session count and mark sessions as added
            del bot.expected_session_count
            is_session_added = True  # Set flag to True

            # Save sessions in MongoDB
            sessions_collection.insert_many([{"session_string": session} for session in new_sessions])

            # Send confirmation
            await message.reply("✅ सभी session strings जोड़ दी गईं! अब आप रिपोर्ट करना शुरू कर सकते हैं।")
        else:
            await message.reply(f"⚠️ आपको ठीक {bot.expected_session_count} session strings प्रदान करनी चाहिए। कृपया फिर से प्रयास करें।")
    else:
        await message.reply("⚠️ कृपया पहले /make_config <number> का उपयोग करके session strings जोड़ें।")

# 🎯 Report Command (User chooses a reason)
@bot.on_message(filters.command("report"))
async def report_user(client, message):
    global is_session_added

    # Check if session strings are added before reporting
    if not is_session_added:
        return await message.reply("⚠️ सत्र जोड़ा नहीं गया! कृपया पहले /make_config का उपयोग करें।")

    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply("⚠️ उपयोग: `/report @username`")

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
        f"⚠️ {username} को रिपोर्ट करने का कारण चुनें:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🎯 Report Handler (User clicks a reason)
@bot.on_callback_query()
async def report_handler(client, callback_query):
    data = callback_query.data.split(":")
    username = data[1]
    reason = data[2]

    # Store report in MongoDB
    reports_collection.insert_one({"username": username, "reason": reason, "reported_by": callback_query.from_user.id})

    await callback_query.answer(f"{username} has been reported for {reason}. Thank you for your report!")
    await callback_query.message.edit("✅ Report has been successfully submitted.")

# 🎯 Run the bot
bot.run()
