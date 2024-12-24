import asyncio

from plugins.bot import Bot
from plugins.restart import start_scheduled_restart

# Initialize bot
bot = Bot()

# Get event loop
loop = asyncio.get_event_loop()

# Add scheduled restart task to the loop
loop.create_task(start_scheduled_restart())

# Run the bot
bot.run()
