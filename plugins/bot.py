import sys
from datetime import datetime
from typing import Optional

from aiohttp import web
from pyrogram import Client
# fix for current pyrogram
from pyrogram import utils
from pyrogram.enums import ParseMode

from config import (
    API_HASH,
    APP_ID,
    TG_BOT_WORKERS,
    TG_BOT_TOKEN,
    OWNER_ID,
    PORT,
)
from plugins import web_server
from plugins.utils.fake_reaction import start_other_bots, stop_other_bots
from plugins.utils.logger import get_logger


# Determine the type of peer from its ID
def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    return "channel" if peer_id_str.startswith("-100") else "chat"


# Replace program's peer type function
utils.get_peer_type = get_peer_type_new


# Custom exception for bot initialization errors.
class BotInitError(Exception):
    pass


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        self.username: Optional[str] = None
        self.LOGGER = get_logger(__name__)
        self.uptime = datetime.now()

    # Setup web server for bot
    async def setup_web_server(self) -> None:
        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            bind_address = "0.0.0.0"
            await web.TCPSite(app, bind_address, PORT).start()
        except Exception as e:
            self.LOGGER.error(f"Web server setup error: {str(e)}")
            raise BotInitError("Web server setup failed")

    # Start the bot and initialize all required components.
    async def start(self) -> None:
        try:
            await super().start()
            me = await self.get_me()
            self.username = me.username

            # Set parse mode and start web server
            self.set_parse_mode(ParseMode.HTML)
            await self.setup_web_server()

            self.LOGGER.info("Bot0 is running successfully!")
            await start_other_bots()
            self.LOGGER.info("All the bots are started and running.")

            # Send startup notification
            await self.send_message(chat_id=OWNER_ID, text="Bot has started!")
        except Exception as e:
            self.LOGGER.error(f"Bot startup failed: {str(e)}")
            sys.exit(1)

    # Stop the bot gracefully
    async def stop(self, *args) -> None:
        try:
            await super().stop()
            self.LOGGER.info("Bot0 stopped successfully.")
            await stop_other_bots()
            self.LOGGER.info("All the bots are stopped.")
        except Exception as e:
            self.LOGGER.error(f"Error while stopping bot: {str(e)}")
