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
logging.basicConfig(level=logging.INFO)

# Set up your API credentials
API_ID = 123456  # Replace with your API ID
API_HASH = "your_api_hash"  # Replace with your API Hash
BOT_TOKEN = "your_bot_token"  # Replace with your bot token (leave empty if using userbot)
STRING_SESSION = ""  # Replace with your string session (leave empty if using a bot)

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

# Command to report a user
@app.on_message(filters.command("report") & filters.me if STRING_SESSION else filters.command("report"))
async def report_user(client, message):
    try:
        # Extract command parameters
        args = message.text.split()
        if len(args) < 3:
            return await message.reply("Usage: /report @username reason (e.g., /report @user spam)")

        username = args[1]
        reason_key = args[2].lower()

        # Validate reason
        if reason_key not in REPORT_REASONS:
            return await message.reply(f"Invalid reason. Choose from: {', '.join(REPORT_REASONS.keys())}")

        reason = REPORT_REASONS[reason_key]

        # Resolve user/channel
        entity = await client.get_users(username)
        peer = await client.resolve_peer(entity.id)

        # Send report
        await client.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))
        await message.reply(f"✅ Successfully reported {username} for {reason_key}.")

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply("⚠️ Failed to report. Check the username and reason.")

# Run the bot
app.run()
