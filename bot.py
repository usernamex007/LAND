import asyncio
import logging
import time
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

# 🔹 Enable Logging
logging.basicConfig(level=logging.INFO)

# 🔹 API Credentials
API_ID = 28795512  # अपना API ID डालें
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # अपना API Hash डालें
BOT_TOKEN = "7854222423:AAENyQ95hobcR_CFGKeDfhrwbH2MU"  # अपना Bot Token डालें
STRING_SESSION = "AQG3YngADVoLztHlgfxI4gMSX8n5-RbHEuke_OYA6Gtm4girJGg3ZwEBdzHSy2LX3sBMy5D88nTLf4Qv8srW5AFx0Rec5jUj4hpRmednZkKL7_gXLexaPS-hnSRVYE9gYZHpR68gYEj3TN3a_NStvmW2nLsufUscza6J2awVq2rrQFrUX9_oop5MuAcRYsgWapB0p0pm4Z_FGG3M377ivchaklTcOjqelr0a_SLvFCEFRUT2fd5bnLyyIOulK0nSU1Fo42i0Yej4iVCLZ03c2-pWvPU3WCW5AA5vuEVepGzcBZ7PvlFzQ6VHoLPA3bjtVLZ9i2E-tUdyfQJ_3tHrQ4guD7QObwAAAAGllg0RAA"  # अपना String Session डालें
OWNER_ID = 7073041681  # 🔹 अपना Telegram User ID डालें (Admin को Notification भेजने के लिए)

# 🔹 Initialize Clients
bot = Client("report_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

# 🔹 Report Reason Mapping
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

# ✅ Bot Response on /start
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("👋 Hello! Use `/report @username spam` to report a user.\nUse `/ping` to check bot status.")

# ✅ /report Command (Userbot will Report)
@bot.on_message(filters.command("report"))
async def report_user(client, message):
    try:
        args = message.text.split()
        if len(args) < 3:
            return await message.reply("⚠️ Usage: `/report @username spam`")

        username = args[1]
        reason_key = args[2].lower()

        if reason_key not in REPORT_REASONS:
            return await message.reply(f"⚠️ Invalid reason! Choose from: {', '.join(REPORT_REASONS.keys())}")

        reason = REPORT_REASONS[reason_key]

        # 🔹 Resolve user/channel
        async with userbot:
            entity = await userbot.get_users(username)
            peer = await userbot.resolve_peer(entity.id)

            # 🔹 Send Report from Userbot
            await userbot.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))
        
        await message.reply(f"✅ Successfully reported {username} for {reason_key}.")

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply("⚠️ Failed to report. Check username & reason.")

# ✅ Ping Command for Bot
@bot.on_message(filters.command("ping"))
async def ping_bot(client, message):
    start_time = time.time()
    reply = await message.reply("🏓 Pong...")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    await reply.edit(f"🏓 Pong! `{latency}ms`")

# ✅ Ping Command for Userbot
@userbot.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping_userbot(client, message):
    start_time = time.time()
    reply = await message.reply("🏓 Pong...")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    await reply.edit(f"🏓 Pong! `{latency}ms` (Userbot)")

# ✅ Bot Start Notification to Owner
async def send_start_notifications():
    try:
        async with bot:
            await bot.send_message(OWNER_ID, "✅ **Bot Started Successfully!**")
        async with userbot:
            await userbot.send_message(OWNER_ID, "✅ **Userbot Started Successfully!**")
    except Exception as e:
        logging.error(f"Error sending start notification: {e}")

# 🔹 Main Function to Run Both Clients
async def main():
    await asyncio.gather(bot.start(), userbot.start())
    print("✅ Bot & Userbot started successfully!")

    # ✅ Send Notification to Admin
    await send_start_notifications()

    # ✅ Keep the bot running using asyncio.Event
    await asyncio.Event().wait()

# 🔹 Run the Bot
if __name__ == "__main__":
    asyncio.run(main())
