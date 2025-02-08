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
config_collection = db['config']  # To store session added flag

# 🎯 Bot Client
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Session storage and flag to check if sessions are added
session_strings = []

# 🎯 Start Command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    welcome_text = "👋 स्वागत है! /make_config  का उपयोग करें ताकि आप session strings जोड़ सकें।"
    await message.reply(welcome_text)

# 🎯 Make Config Command
@bot.on_message(filters.command("make_config"))
async def make_config(client, message):
    # Check if sessions are already added
    config = config_collection.find_one({"bot_id": BOT_TOKEN})
    
    if config and config.get("is_session_added", False):
        return await message.reply("⚠️ सत्र पहले ही जोड़ दिए गए हैं! आप अब रिपोर्ट करना शुरू कर सकते हैं.")

    args = message.text.split()

    if len(args) < 2:
        return await message.reply("⚠️ उपयोग: `/make_config <number>` जहां <number> वह संख्या है जो आप जोड़ना चाहते हैं।")

    try:
        session_count = int(args[1])  # Number of session strings
    except ValueError:
        return await message.reply("⚠️ कृपया एक मान्य संख्या प्रदान करें।")

    await message.reply(f"⚙️ कृपया {session_count} session strings प्रदान करें (स्पेस से अलग करें):")

    # Store expected session count
    session_strings.clear()  # Clear previous session strings
    bot.expected_session_count = session_count

# 🎯 Collect Session Strings
@bot.on_message(filters.text)
async def collect_session_strings(client, message):
    if hasattr(bot, 'expected_session_count') and len(session_strings) < bot.expected_session_count:
        session_input = message.text.strip()

        # Split the input and check if the correct number of session strings were provided
        new_sessions = session_input.split()

        if len(new_sessions) == bot.expected_session_count:
            session_strings.extend(new_sessions)
            await message.reply(f"✅ {len(new_sessions)} session strings successfully added.")
            
            # Reset expected session count and mark sessions as added
            del bot.expected_session_count

            # Save sessions in MongoDB
            sessions_collection.insert_many([{"session_string": session} for session in new_sessions])

            # Save flag in MongoDB (Mark session as added)
            config_collection.update_one(
                {"bot_id": BOT_TOKEN},
                {"$set": {"is_session_added": True}},
                upsert=True
            )

            # Send confirmation
            await message.reply("✅ सभी session strings जोड़ दिए गए हैं! आप अब रिपोर्टिंग शुरू कर सकते हैं.")
        else:
            await message.reply(f"⚠️ आपको ठीक {bot.expected_session_count} session strings प्रदान करनी चाहिए। कृपया पुनः प्रयास करें।")
    else:
        await message.reply("⚠️ कृपया पहले /make_config <number> कमांड का उपयोग करके session strings जोड़ें।")

# 🎯 Report Command (User chooses a reason)
@bot.on_message(filters.command("report"))
async def report_user(client, message):
    # Check if session strings have been added
    config = config_collection.find_one({"bot_id": BOT_TOKEN})
    
    if not config or not config.get("is_session_added", False):
        # Allow user to send /make_config if session is not added
        return await message.reply("⚠️ कृपया पहले /make_config कमांड का उपयोग करके session strings जोड़ें।")

    buttons = [
        [InlineKeyboardButton("I don't like it", callback_data=f"report:other")],
        [InlineKeyboardButton("Child abuse", callback_data=f"report:child_abuse")],
        [InlineKeyboardButton("Violence", callback_data=f"report:violence")],
        [InlineKeyboardButton("Illegal goods", callback_data=f"report:illegal_goods")],
        [InlineKeyboardButton("Illegal adult content", callback_data=f"report:porn")],
        [InlineKeyboardButton("Personal data", callback_data=f"report:personal_data")],
        [InlineKeyboardButton("Terrorism", callback_data=f"report:fake")],
        [InlineKeyboardButton("Scam or spam", callback_data=f"report:spam")],
        [InlineKeyboardButton("Copyright", callback_data=f"report:copyright")],
        [InlineKeyboardButton("Other", callback_data=f"report:other")]
    ]
    
    await message.reply(
        f"⚠️ रिपोर्ट करने का कारण चुनें:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🎯 Report Handler (User clicks a reason)
@bot.on_callback_query(filters.regex("^report:"))
async def handle_report(client, callback_query):
    config = config_collection.find_one({"bot_id": BOT_TOKEN})

    if not config or not config.get("is_session_added", False):
        return await callback_query.answer("⚠️ कृपया पहले /make_config कमांड का उपयोग करके session strings जोड़ें।", show_alert=True)

    data = callback_query.data.split(":")
    
    if len(data) < 2:
        return

    reason_code = data[1]

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
        [InlineKeyboardButton("10 Reports", callback_data=f"sendreport:{reason_code}:10")],
        [InlineKeyboardButton("50 Reports", callback_data=f"sendreport:{reason_code}:50")],
        [InlineKeyboardButton("100 Reports", callback_data=f"sendreport:{reason_code}:100")],
        [InlineKeyboardButton("200 Reports", callback_data=f"sendreport:{reason_code}:200")]
    ]

    await callback_query.message.edit_text(
        f"✅ Selected reason: {reason_code.replace('_', ' ').title()}\n\nReports भेजने के लिए संख्या चुनें:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🎯 Bulk Report Handler
@bot.on_callback_query(filters.regex("^sendreport:"))
async def send_bulk_reports(client, callback_query):
    config = config_collection.find_one({"bot_id": BOT_TOKEN})

    if not config or not config.get("is_session_added", False):
        return await callback_query.answer("⚠️ कृपया पहले /make_config कमांड का उपयोग करके session strings जोड़ें।", show_alert=True)

    data = callback_query.data.split(":")
    
    if len(data) < 3:
        return

    reason_code = data[1]
    count = int(data[2])

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

            # Sending bulk reports
            for i in range(count):
                await userbot.invoke(ReportPeer(peer=session_string, reason=reason, message="Reported by bot"))
                await asyncio.sleep(0.5)

            await userbot.stop()

        await callback_query.message.edit_text(f"✅ {count} reports successfully sent for {reason_code.replace('_', ' ').title()}.")

    except Exception as e:
        logging.error(f"Error sending report: {e}")
        await callback_query.answer("⚠️ रिपोर्ट भेजने में समस्या हुई। कृपया पुनः प्रयास करें।", show_alert=True)

# Start the bot
bot.run()
