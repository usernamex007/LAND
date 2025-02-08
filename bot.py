import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import InputReportReasonSpam

# 📌 Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🛠 Configuration
API_ID = 28795512  # अपना API_ID डालें
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7854222423:AAENyTD0z0UQ95hobcR_CFGKeDfhrwbH2MU"

# 🎯 Bot Client
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Userbot session storage
userbot = None

# 🎯 Start Command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("👋 Welcome! Use /addsession <session_string> to add a session.")

# 🎯 Add Session Command
@bot.on_message(filters.command("addsession"))
async def add_session(client, message):
    global userbot

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("⚠️ Usage: `/addsession <session_string>`")

    session_string = args[1]

    try:
        # Existing userbot को पहले रोकें
        if userbot:
            await userbot.stop()

        # नया userbot शुरू करें
        userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
        await userbot.start()
        
        await message.reply("✅ Session added successfully! Now you can use /report.")
    
    except Exception as e:
        logging.error(f"Error adding session: {e}")
        await message.reply(f"⚠️ Failed to add session. Error: {e}")

# 🎯 Report System (Userbot Reports)
@bot.on_message(filters.command("report"))
async def report_user(client, message):
    global userbot

    if not userbot:
        return await message.reply("⚠️ No session added! Use /addsession first.")

    try:
        args = message.text.split()
        if len(args) < 3:
            return await message.reply("⚠️ Usage: `/report @username reason` (e.g., `/report @user spam`)")

        username = args[1]
        reason = args[2].lower()

        # 🎯 Get user details
        entity = await userbot.get_users(username)
        logging.info(f"✅ Entity Found: {entity}")

        peer = await userbot.resolve_peer(entity.id)
        logging.info(f"✅ Peer Resolved: {peer}")

        # 🎯 Report user
        await userbot.invoke(ReportPeer(peer=peer, reason=InputReportReasonSpam(), message="Reported by bot"))
        await message.reply(f"✅ Successfully reported {username} for {reason}.")
    
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply(f"⚠️ Failed to report. Error: {e}")

# 🎯 Start Bot Properly Without asyncio.run()
async def main():
    await bot.start()
    logging.info("✅ Bot started successfully!")

    try:
        await asyncio.Event().wait()  # Keeps bot running
    except asyncio.CancelledError:
        logging.info("❌ Stopping Bot...")

    finally:
        if userbot:
            await userbot.stop()
        await bot.stop()
        logging.info("✅ Bot stopped successfully!")

# ✅ Properly Handle Event Loop
if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())  
    except KeyboardInterrupt:
        logging.info("❌ Bot manually stopped.")
        loop.run_until_complete(bot.stop())
        if userbot:
            loop.run_until_complete(userbot.stop())
