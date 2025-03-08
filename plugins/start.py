import asyncio
import json
import os
import re
from typing import List

from pyrogram import filters
from pyrogram.errors import FloodWait, WebpageMediaEmpty, WebpageCurlFailed
from pyrogram.types import Message, ReplyKeyboardMarkup

from config import settings
from plugins.bot import Bot
from plugins.utils.fake_reaction import other_bots_reactions
from plugins.utils.logger import get_logger
from plugins.utils.utility import MemberTagger, random_emoji_reaction, get_random_emoji


KEYBOARD = ReplyKeyboardMarkup(
    [
        ["/start", "/set_env"],
    ],
    resize_keyboard=True,  # Makes the keyboard smaller and neater
    is_persistent=True  # Makes the keyboard persistent
)

logger = get_logger(__name__)


@Bot.on_message(filters.private & filters.command("set_env") & filters.user(settings.OWNER_ID))
async def set_env(client: Bot, message: Message):
    try:
        await message.reply(settings.get_all_values(), reply_markup=KEYBOARD)

        key = await ask_(client, message, "Enter the key name:")

        if not key:
            return await message.reply("❌ Key name is required.")

        value = await ask_(client, message, "Enter the value (type 'empty' for blank):")
        if value is None:
            return await message.reply("❌ No value provided.")

        # Convert "empty" to an actual empty string
        value = "" if value.lower() == "empty" else value

        # Try updating .env and send confirmation
        if settings.update_env_value(key, value):  # Ensure this function is correctly defined
            await message.reply(f"✅ Successfully set `{key}` to `{value}`.")
        else:
            await message.reply("❌ Failed to update .env. Key might not exist.")

    except Exception as e:
        print(f"Error in set_env_by_owner: {e}")
        await message.reply("⚠️ An unexpected error occurred.")


@Bot.on_message(filters.group & filters.command("alls") & filters.reply)
async def alls(client: Bot, message: Message):
    tagger = MemberTagger()

    if not await tagger.is_admin(client, message):
        await message.reply("Only administrators can use this command.")
        return

    try:
        await message.delete()
        members = await tagger.process_members(client, message.chat.id)

        for i in range(0, len(members), tagger.batch_size):

            batch = members[i:i + tagger.batch_size]

            try:
                await tagger.send_mentions(client, message, batch, message.message_thread_id)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await tagger.send_mentions(client, message, batch, message.message_thread_id)
            except Exception as e:
                logger.error(f"Error sending to user : {str(e)}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")


@Bot.on_message(filters.channel & (filters.chat(settings.CHANNEL1) | filters.chat(settings.CHANNEL2)))
async def edit_channel_messages_and_media(client: Bot, message: Message):
    try:

        if message.chat.id in [settings.CHANNEL1, settings.CHANNEL2]:

            # Reactions methods
            await random_emoji_reaction(client, message, emoji=get_random_emoji(max_emoji=1))
            if settings.EMOJI:
                await other_bots_reactions(message, emojis=settings.EMOJI)
            else:
                await other_bots_reactions(message, emojis=get_random_emoji(max_emoji=4))

            # Extract current message text
            text = message.text or message.caption or ""

            # Regex to check if text contains only emojis
            emoji_pattern = re.compile(r'^[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF\U0001F1E6-\U0001F1FF\s]+$')

            if emoji_pattern.fullmatch(text.strip()):
                return  # Ignore messages that contain only emojis

            await asyncio.sleep(5)

            # Append "#nma" if it's not already included
            if "#NMA" not in text and message.chat.id == settings.CHANNEL1:
                updated_text = f"{text}\n\n#NMA #General"

                if message.text:
                    # Edit text message
                    await message.edit_text(updated_text)
                elif message.caption or not message.media_group_id:
                    # Edit media message with a caption
                    await message.edit_caption(updated_text)

            elif "#NMA" not in text and message.chat.id == settings.CHANNEL2:
                updated_text = f"{text}\n\n#NMA #Content"

                if message.text:
                    # Edit text message
                    await message.edit_text(updated_text)
                elif message.caption or not message.media_group_id:
                    # Edit media message with a caption
                    await message.edit_caption(updated_text)

    except Exception as e:
        logger.error(f"Error editing channel message: {str(e)}")


# @Bot.on_message(filters.channel & filters.command("custom_samosa"))
async def send_videos(client: Bot, message: Message):
    try:
        videos_data = await load_exist_file_if_present(file_name="desi_site_videos_data")
        logger.info("send json videos data to telegram!")
        logger.info(f"len : {len(videos_data)}")

        failed_videos = []
        for video in videos_data:
            try:
                await send_single(client, message, video)
                logger.info(f"Sent {video['title']} successfully!")
                # Add a longer delay between videos to avoid rate limiting
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Failed to send video {video['title']}: {str(e)}")
                failed_videos.append(video)
                # Continue with next video instead of stopping
                continue

        if failed_videos:
            logger.warning(f"Failed to send {len(failed_videos)} videos. Retrying...")
            logger.warning(f"{failed_videos}")
            for video in failed_videos:
                try:
                    await send_single(client, message, video)
                    logger.info(f"Retry successful for {video['title']}")
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Retry failed for {video['title']}: {str(e)}")

        logger.info("Finished processing all videos")
        await client.send_message(
            chat_id=message.chat.id,
            text=f"Process completed.\nSuccessfully sent: {len(videos_data) - len(failed_videos)}\nFailed: {len(failed_videos)}"
        )

    except Exception as e:
        logger.error(f"Error in send_videos command: {str(e)}")
        await client.send_message(
            chat_id=message.chat.id,
            text=f"An error occurred while processing videos: {str(e)}"
        )


async def send_single(client: Bot, message: Message, video):
    max_retries = 3
    current_retry = 0

    while current_retry < max_retries:
        try:
            if not video.get('link') or not video.get('title'):
                logger.warning(f"Missing link or title in video data: {video}")
                return

            await client.send_video(
                video=video['link'],
                caption=video['title'],
                chat_id=message.chat.id
            )
            return

        except FloodWait as e:
            wait_time = e.value + 5
            logger.warning(f"FloodWait detected, waiting for {wait_time} seconds")
            await asyncio.sleep(wait_time)
            current_retry += 1

        except (WebpageCurlFailed, WebpageMediaEmpty) as e:
            logger.warning(f"Media issue, sending as text message instead: {str(e)}")
            try:
                await client.send_message(
                    chat_id=message.chat.id,
                    text=f"Title: {video['title']}\n\nLink: {video['link']}"
                )
                return
            except FloodWait as e:
                wait_time = e.value + 5
                logger.warning(f"FloodWait on text message, waiting for {wait_time} seconds")
                await asyncio.sleep(wait_time)
                current_retry += 1

        except Exception as e:
            logger.error(f"Error sending video {video['title']}: {str(e)}")
            current_retry += 1
            if current_retry < max_retries:
                await asyncio.sleep(5)  # Wait before retry
            else:
                raise  # Re-raise if max retries reached


async def load_exist_file_if_present(file_name: str) -> List:
    try:
        file_path = os.path.abspath(f"plugins/{file_name}.json")
        if not os.path.exists(file_path):
            logger.error(f"File not found : {file_path}")
            return []

        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            logger.info(f"Successfully loaded {len(data)} videos from {file_path}")
            return data

    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_name}.json: {e}")
        return []
    except PermissionError as e:
        print(f"Permission denied when trying to read {file_name}.json: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error reading {file_name}.json: {e}")
        return []


async def ask_(client: Bot, message: Message, name: str) -> str | None:
    try:
        response = await client.ask(
            text=f"Enter {name} 🔢\n /cancel to cancel : ",
            chat_id=message.from_user.id,
            timeout=60,
        )

        if response.text == "/cancel":
            await response.reply("Cancelled 😉!")
            return None

        return response.text

    except Exception as e:
        logger.error(f"Error in ask_: {str(e)}")
        return None
