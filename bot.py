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
API_ID = 28795512  # Replace with your API ID
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # Replace with your API Hash
BOT_TOKEN = "7854222423:AAENyTD0z0UQ95hobcR_CFGKeDfhrwbH2MU"  # Replace with your bot token (leave empty if using userbot)
STRING_SESSION = "1AZWarzsBuxcmT-FRpGtdfxSeKqkguVjCHH60My8SKxrHTrAUIY1gGvD4mG51N1a1f_Zrv_Y73RZD3ZaQy7cOyVXYlgZIKXSQ1GZfNsouA5stBHyPBvdMX11pTLuoMeAmjn9a0XOxiHOKA4Ye4LUE9OMIVdgtFgauJWqAcTYpnqALAJyjcotAINyOv00FpPPZyoGyY3aKcyz7YJccddQfowYx56nsDnJRttxjI7wj9a5lXDfOxOwhbh7acJIBVtK5EV0f9eJQ9-vLBrkbPrOxavc7okcTLzKcpRDFv-xO4L373WAfGUhouc4KYfPVbxzmdFKgX6U-3ajSZ9a9eauZDZxakWfKr9U="  # Replace with your string session (leave empty if using a bot)

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

# /start command
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply(
        "👋 **Welcome to the Reporting Bot!**\n\n"
        "Use `/report @username reason` to report users.\n"
        "Available reasons: spam, fake, violence, porn, child_abuse, copyright, drugs, personal_info.\n\n"
        "**Example:** `/report @example spam`"
    )

# Command to report a user
@app.on_message(filters.command("report") & filters.me if STRING_SESSION else filters.command("report"))
async def report_user(client, message):
    try:
        # Extract command parameters
        args = message.text.split()
        if len(args) < 3:
            return await message.reply("❌ **Usage:** `/report @username reason`\nExample: `/report @user spam`")

        username = args[1]
        reason_key = args[2].lower()

        # Validate reason
        if reason_key not in REPORT_REASONS:
            return await message.reply(f"⚠️ **Invalid reason.** Choose from: {', '.join(REPORT_REASONS.keys())}")

        reason = REPORT_REASONS[reason_key]

        # Resolve user/channel
        entity = await client.get_users(username)
        peer = await client.resolve_peer(entity.id)

        # Send report
        await client.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))
        await message.reply(f"✅ **Successfully reported {username} for {reason_key}.**")

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply("⚠️ **Failed to report.** Check the username and reason.")

# Run the bot
app.run()
