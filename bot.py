import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import InputReportReasonSpam

# 📌 Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🛠 Configuration
API_ID = 28795512  
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7984449177:AAHC4MjJ541UAPnA9MYLqEcXaIrbd7e2I4A"
USERBOT_SESSION = "AQG3YngADVoLztHlgfxI4gMSX8n5-RbHEuke_OYA6Gtm4girJGg3ZwEBdzHSy2LX3sBMy5D88nTLf4Qv8srW5AFx0Rec5jUj4hpRmednZkKL7_gXLexaPS-hnSRVYE9gYZHpR68gYEj3TN3a_NStvmW2nLsufUscza6J2awVq2rrQFrUX9_oop5MuAcRYsgWapB0p0pm4Z_FGG3M377ivchaklTcOjqelr0a_SLvFCEFRUT2fd5bnLyyIOulK0nSU1Fo42i0Yej4iVCLZ03c2-pWvPU3WCW5AA5vuEVepGzcBZ7PvlFzQ6VHoLPA3bjtVLZ9i2E-tUdyfQJ_3tHrQ4guD7QObwAAAAGllg0RAA"

# 🎯 Bot & Userbot Clients
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=USERBOT_SESSION)

# 🎯 Report System
@bot.on_message(filters.command("report"))
@userbot.on_message(filters.command("report", prefixes="/") & filters.me)
async def report_user(client, message):
    try:
        args = message.text.split()
        if len(args) < 3:
            return await message.reply("⚠️ Usage: `/report @username reason` (e.g., `/report @user spam`)")

        username = args[1]
        reason = args[2].lower()

        # 🎯 Get user details
        try:
            entity = await userbot.get_users(username)
        except Exception:
            return await message.reply("❌ Invalid Username or User not found.")

        logging.info(f"✅ Entity Found: {entity}")

        # 🎯 Resolve Peer Safely
        try:
            peer = await userbot.resolve_peer(entity.id)
        except Exception:
            return await message.reply("❌ Could not resolve user. Make sure bot is in the group/channel.")

        logging.info(f"✅ Peer Resolved: {peer}")

        # 🎯 Report user
        await userbot.invoke(ReportPeer(peer=peer, reason=InputReportReasonSpam(), message="Reported by bot"))
        await message.reply(f"✅ Successfully reported {username} for {reason}.")
    
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply(f"⚠️ Failed to report. Error: {e}")

# 🎯 Start Bot & Userbot
async def main():
    await bot.start()
    await userbot.start()
    logging.info("✅ Bot & Userbot started successfully!")

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        logging.info("❌ Stopping Bot & Userbot...")
        await bot.stop()
        await userbot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("❌ Bot & Userbot Manually Stopped.")
