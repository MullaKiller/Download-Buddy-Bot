import asyncio
from typing import List

from pyrogram import Client
from pyrogram.types import Message

from plugins.utils.logger import get_logger
from plugins.utils.utility import random_emoji_reaction

logger = get_logger(__name__)


class ChannelBotManager:
    def __init__(self):
        self.bots = [
            {
                "name": "Samosa1_bot",
                "client": Client(
                    "Bot1",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7645924051:AAHjbLQ4fm0ErdECl403nBhOxw4kNzn1alQ"
                )
            },
            {
                "name": "Samosa2_bot",
                "client": Client(
                    "Bot2",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7834601337:AAEFGpOKSpy-chZFT0YFLX2IX1inw-CBFLg"
                )
            },
            {
                "name": "Samosa3_bot",
                "client": Client(
                    "Bot3",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7728030809:AAFgcs1Tb0yT7SIMg04k7cFT6MNrDoUXZa8"
                )
            },
            {
                "name": "Samosa4_bot",
                "client": Client(
                    "Bot4",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7558468897:AAEX2KOaCVHts2-7i1NtjL4F9sZ614OZECU"
                )
            },
            {
                "name": "Samosa5_bot",
                "client": Client(
                    "Bot5",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7580912385:AAG-Lrz2DUDFZenbRP80AdsSR7Z995NXRLE"
                )
            },
            {
                "name": "Samosa6_bot",
                "client": Client(
                    "Bot6",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7702846467:AAG42dWItgfMdGbK8p4J3x8CA84jlQSTeWY"
                )
            },
            {
                "name": "Samosa7_bot",
                "client": Client(
                    "Bot7",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7961946749:AAGXuTcdkcslLZXR59dzWYP_5h7e-x1UoNY"
                )
            },
            {
                "name": "Samosa8_bot",
                "client": Client(
                    "Bot8",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7719585732:AAE_ecgmYRjRBQqhEG-hTRnWLRcbtXbDDMM"
                )
            },
            {
                "name": "Samosa9_bot",
                "client": Client(
                    "Bot9",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7538616318:AAEBSFBI-9iB_No1EOGAkOcL4SqbxrzTAPE"
                )
            },
            {
                "name": "Samosa111_bot",
                "client": Client(
                    "Bot10",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7940274792:AAGm0gnsEvoSRzc_d7wBrOytkUdwds5tBWw"
                )
            },
            {
                "name": "Samosa12_bot",
                "client": Client(
                    "Bot11",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7862516536:AAF2oocU1hF5_xyxafHkfZvdJwVL9SydO2Q"
                )
            },
            {
                "name": "Samosa13_bot",
                "client": Client(
                    "Bot12",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="8148522810:AAHN5UFpIZSsVXHl_aaDOJZQwKV5g3HQ_AQ"
                )
            },
            {
                "name": "Samosa14_bot",
                "client": Client(
                    "Bot13",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="8137727069:AAGsohbKZ7tGYqPAXoSnHkdRznam0sXPCHk"
                )
            },
            {
                "name": "Samosa15_bot",
                "client": Client(
                    "Bot14",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7629151175:AAEBd8c6wwjytCstYv36_7gex2nen8eS4pU"
                )
            },
            {
                "name": "Samosa16_bot",
                "client": Client(
                    "Bot15",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="8120416099:AAFqCrk5C7cBMy7HkecA3VwUoOT7icqqK00"
                )
            },
            {
                "name": "Samosa17_bot",
                "client": Client(
                    "Bot16",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7277918007:AAE_Pq2jZEcKKzBs8I-tVopXFyxS_89GzMk"
                )
            },
            {
                "name": "OLD NMA Content bot",
                "client": Client(
                    "Bot18",
                    api_id=20579212,
                    api_hash="4861e861bffd7d533db630c1b941df72",
                    bot_token="7317356373:AAG4nLgjPgkmcVeVGeNJFFfXPyYRMMOjI5Q"
                )
            },
            {
                "name": "Contribution_bot",
                "client": Client(
                    "Bot19",
                    api_id=22999504,
                    api_hash="293765a6ae6fa5880fe8937a834d9126",
                    bot_token="7589544571:AAHvSmvN0lpOy5jbtqm7MS-85SYw18e93WE"
                )
            },
        ]
        self.started_bots = []

    async def start_bot(self, bot):
        """Start a single bot if not already started"""
        if bot not in self.started_bots:
            try:
                await bot["client"].start()
                self.started_bots.append(bot)
                logger.info(f"{bot['name']} started successfully")
            except Exception as e:
                logger.error(f"Error starting {bot['name']}: {e}")
                raise

    async def stop_bot(self, bot):
        """Stop a single bot"""
        if bot in self.started_bots:
            try:
                await bot["client"].stop()
                self.started_bots.remove(bot)
                logger.info(f"{bot['name']} stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping {bot['name']}: {e}")

    async def give_reaction(self, bot, message, emoji):
        """Give reaction with a single bot"""
        try:
            await asyncio.sleep(5)
            await random_emoji_reaction(bot["client"], message, emoji)
            logger.info(f"{bot['name']} gave reaction successfully")
        except Exception as e:
            logger.error(f"Error giving reaction with {bot['name']}: {e}")


# Create a single instance
bot_manager = ChannelBotManager()


async def start_other_bots():
    """Main function to handle all bot reactions"""
    try:
        # Start all other bots
        for bot in bot_manager.bots:
            await bot_manager.start_bot(bot)

    except Exception as e:
        logger.error(f"start all other bots error : {e}")

    # finally:
    #     # Clean up: stop all bots
    #     for bot in bot_manager.started_bots[:]:  # Create a copy of the list to iterate
    #         await bot_manager.stop_bot(bot)


async def stop_other_bots():
    try:
        for bot in bot_manager.started_bots[:]:
            await bot_manager.stop_bot(bot)
    except Exception as e:
        logger.error(f"stop all other bots error : {e}")


async def other_bots_reactions(message: Message, emojis: List):
    try:
        tasks = []
        i = 0
        for bot in bot_manager.bots:
            tasks.append(asyncio.create_task(bot_manager.give_reaction(bot, message, emojis[i % len(emojis)])))
            i += 1

        # Wait for all reactions to complete
        await asyncio.gather(*tasks)
        logger.info("Other bots gave reactions successfully!")
    except Exception as e:
        logger.error(f"Other bots giving reaction failed : {str(e)}")
