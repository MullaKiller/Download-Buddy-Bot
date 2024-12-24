import asyncio
import os
import sys
from datetime import datetime

import pytz
from pyrogram import filters
from pyrogram.types import Message

from config import OWNER_ID
from plugins.bot import Bot
from plugins.utils.logger import get_logger

logger = get_logger(__name__)

CHECK_INTERVAL = 60


# Initialize the scheduled restart task
async def start_scheduled_restart():
    try:
        await schedule_daily_restart()
    except Exception as e:
        logger.error(f"Failed to initialize scheduled restart: {str(e)}")


# Perform the actual restart operation
async def perform_restart():
    try:
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        logger.error(f"Error during restart: {str(e)}")


# Check if it's time to restart (12:00 AM IST)
def is_restart_time() -> bool:
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    return now.hour == 0 and now.minute == 0


# Schedule daily restart at 12:00 AM IST
async def schedule_daily_restart():
    while True:
        try:
            if is_restart_time():
                logger.info("It's restart time! Executing scheduled restart")
                await perform_restart()

            # Sleep for a short interval instead of the whole day
            await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"Error in scheduled restart: {str(e)}")
            await asyncio.sleep(30)  # Short sleep on error before retry


# Handle manual restart command
@Bot.on_message(filters.private & filters.command("restart") & filters.user(OWNER_ID))
async def restart_command(client: Bot, message: Message):
    status_msg = await message.reply_text(
        text="<i>Trying To Restarting.....</i>", quote=True
    )

    await asyncio.sleep(5)
    await status_msg.edit("<i>Server Restarted Successfully ✅</i>")
    await perform_restart()
