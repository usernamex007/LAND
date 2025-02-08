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

# API Credentials
API_ID = 28795512  # Replace with your API ID
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # Replace with your API Hash
BOT_TOKEN = "7854222423:AAENyQ95hobcR_CFGKeDfhrwbH2MU"  # Replace with your Bot Token
STRING_SESSION = "AQG3YngADVoLztHlgfxI4gMSX8n5-RbHEuke_OYA6Gtm4girJGg3ZwEBdzHSy2LX3sBMy5D88nTLf4Qv8srW5AFx0Rec5jUj4hpRmednZkKL7_gXLexaPS-hnSRVYE9gYZHpR68gYEj3TN3a_NStvmW2nLsufUscza6J2awVq2rrQFrUX9_oop5MuAcRYsgWapB0p0pm4Z_FGG3M377ivchaklTcOjqelr0a_SLvFCEFRUT2fd5bnLyyIOulK0nSU1Fo42i0Yej4iVCLZ03c2-pWvPU3WCW5AA5vuEVepGzcBZ7PvlFzQ6VHoLPA3bjtVLZ9i2E-tUdyfQJ_3tHrQ4guD7QObwAAAAGllg0RAA"  # Replace with your String Session

OWNER_ID = 7073041681  # Replace with your Telegram User ID (Only Numbers)

# Initialize Pyrogram Clients
bot = Client("report_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

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

# 🔹 Ping Command for Bot
@bot.on_message(filters.command("ping"))
async def ping_bot(client, message):
    await message.reply_text("✅ **Pong! Bot is Alive.**")

# 🔹 Ping Command for Userbot
@userbot.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping_userbot(client, message):
    await message.reply_text("✅ **Pong! Userbot is Alive.**")

# 🔹 Report Command (Userbot Reports, Not Bot)
@bot.on_message(filters.command("report"))
@userbot.on_message(filters.command("report", prefixes="/") & filters.me)
async def report_user(client, message):
    try:
        args = message.text.split()
        if len(args) < 3:
            return await message.reply("⚠️ Usage: `/report @username reason` (e.g., `/report @user spam`)")

        username = args[1]
        reason_key = args[2].lower()

        if reason_key not in REPORT_REASONS:
            return await message.reply(f"⚠️ Invalid reason. Choose from: {', '.join(REPORT_REASONS.keys())}")

        reason = REPORT_REASONS[reason_key]

        entity = await client.get_users(username)
        peer = await client.resolve_peer(entity.id)

        await userbot.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))
        await message.reply(f"✅ Successfully reported {username} for {reason_key}.")

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply("⚠️ Failed to report. Check the username and reason.")

# 🔹 Start Notification Function
async def send_start_notifications():
    try:
        async with bot:
            await bot.send_message(OWNER_ID, "✅ **Bot Started Successfully!**")
    except Exception as e:
        logging.error(f"❌ Bot Notification Error: {e}")

    try:
        async with userbot:
            await userbot.send_message(OWNER_ID, "✅ **Userbot Started Successfully!**")
    except Exception as e:
        logging.error(f"❌ Userbot Notification Error: {e}")

# 🔹 Main Function
async def main():
    await bot.start()
    await userbot.start()
    logging.info("✅ Bot & Userbot started successfully!")

    # Send Start Notification
    await send_start_notifications()

    # Keep Bot Running
    await asyncio.Event().wait()

# Run the Bot
asyncio.run(main())
