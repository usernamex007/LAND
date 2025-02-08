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

# ✅ Enable logging
logging.basicConfig(level=logging.INFO)

# ✅ Set up your API credentials
API_ID = 28795512  # Replace with your API ID
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"  # Replace with your API Hash
BOT_TOKEN = "7854222423:AAENyTD0z0UQ95hobcR_CFGKeDfhrwbH2MU"  # Replace with your bot token
STRING_SESSION = "AQG3YngADVoLztHlgfxI4gMSX8n5-RbHEuke_OYA6Gtm4girJGg3ZwEBdzHSy2LX3sBMy5D88nTLf4Qv8srW5AFx0Rec5jUj4hpRmednZkKL7_gXLexaPS-hnSRVYE9gYZHpR68gYEj3TN3a_NStvmW2nLsufUscza6J2awVq2rrQFrUX9_oop5MuAcRYsgWapB0p0pm4Z_FGG3M377ivchaklTcOjqelr0a_SLvFCEFRUT2fd5bnLyyIOulK0nSU1Fo42i0Yej4iVCLZ03c2-pWvPU3WCW5AA5vuEVepGzcBZ7PvlFzQ6VHoLPA3bjtVLZ9i2E-tUdyfQJ_3tHrQ4guD7QObwAAAAGllg0RAA"  # Replace with your string session

# ✅ Initialize Pyrogram clients
bot = Client("report_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

# ✅ Report reason mapping
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

# ✅ Start message
@bot.on_message(filters.command("start") & filters.private)
async def start_message(client, message):
    await message.reply("👋 **Welcome!**\nUse `/report @username reason` to report a user.")

# ✅ Report command
@bot.on_message(filters.command("report") & filters.private)
async def report_user(client, message):
    try:
        args = message.text.split()
        if len(args) < 3:
            return await message.reply("❌ **Usage:** `/report @username reason`")

        username = args[1]
        reason_key = args[2].lower()

        if reason_key not in REPORT_REASONS:
            return await message.reply(f"❌ **Invalid reason!**\nAvailable: {', '.join(REPORT_REASONS.keys())}")

        reason = REPORT_REASONS[reason_key]

        entity = await userbot.get_users(username)
        peer = await userbot.resolve_peer(entity.id)

        await userbot.invoke(ReportPeer(peer=peer, reason=reason, message="Reported by bot"))
        await message.reply(f"✅ **Successfully reported {username} for {reason_key}.**")

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply("⚠️ **Failed to report.** Check username and reason.")

# ✅ Run both clients properly
async def main():
    await bot.start()
    await userbot.start()
    print("✅ Both bot & userbot started!")
    await asyncio.Event().wait()  # Keeps the script running

if __name__ == "__main__":
    asyncio.run(main())
