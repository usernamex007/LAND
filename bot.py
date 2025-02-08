import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import (
    InputReportReasonSpam,
    InputReportReasonFake,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonCopyright,
    InputReportReasonIllegalDrugs,
    InputReportReasonPersonalDetails
)

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set up your API credentials
API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = ""  # If using bot
STRING_SESSION = "your_string_session_here"  # If using userbot

# Initialize Pyrogram client
if BOT_TOKEN:
    app = Client("report_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
elif STRING_SESSION:
    app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
else:
    raise ValueError("Provide either a BOT_TOKEN or a STRING_SESSION.")

# Report reason mapping
REPORT_REASONS = {
    "spam": InputReportReasonSpam(),
    "fake": InputReportReasonFake(),
    "violence": InputReportReasonViolence(),
    "porn": InputReportReasonPornography(),
    "child_abuse": InputReportReasonChildAbuse(),
    "copyright": InputReportReasonCopyright(),
    "drugs": InputReportReasonIllegalDrugs(),
    "personal_info": InputReportReasonPersonalDetails(),
}

# Start Command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("✅ Report Bot is active!\nUse /report @username reason to report.")

# Command to report a user
@app.on_message(filters.command("report"))
async def report_user(client, message):
    try:
        args = message.text.split()
        if len(args) < 3:
            return await message.reply("❌ Usage: /report @username reason (e.g., /report @user spam)")

        username = args[1]
        reason_key = args[2].lower()

        if reason_key not in REPORT_REASONS:
            return await message.reply(f"❌ Invalid reason. Choose from: {', '.join(REPORT_REASONS.keys())}")

        reason = REPORT_REASONS[reason_key]
        entity = await client.get_users(username)
        peer = await client.resolve_peer(entity.id)

        await message.reply(f"🔄 Reporting {username} for {reason_key}...")
        
        await client.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))
        await message.reply(f"✅ Successfully reported {username} for {reason_key}.")
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply(f"⚠️ Failed to report: {str(e)}")

# Run the bot
app.run()
