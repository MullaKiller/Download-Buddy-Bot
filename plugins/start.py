import asyncio
import json
import os
import re
from typing import List

from pyrogram import filters
from pyrogram.errors import FloodWait, WebpageMediaEmpty, WebpageCurlFailed
from pyrogram.types import Message

from config import CHANNEL1, CHANNEL2
from plugins.bot import Bot
from plugins.utils.fake_reaction import other_bots_reactions
from plugins.utils.logger import get_logger
from plugins.utils.utility import MemberTagger, random_emoji_reaction

logger = get_logger(__name__)


@Bot.on_message(filters.group & filters.command("alls") & filters.reply)
async def tag_every_user(client: Bot, message: Message):
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


@Bot.on_message(filters.channel)
async def edit_channel_messages_and_media(client: Bot, message: Message):
    try:

        if message.chat.id not in [CHANNEL1, CHANNEL2]:
            return

        # Reactions methods
        await random_emoji_reaction(client, message)
        await other_bots_reactions(message)

        # Extract current message text
        text = message.text or message.caption or ""

        # Regex to check if text contains only emojis
        emoji_pattern = re.compile(r'^[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF\U0001F1E6-\U0001F1FF\s]+$')

        if emoji_pattern.fullmatch(text.strip()):
            return  # Ignore messages that contain only emojis

        await asyncio.sleep(5)

        # Append "#nma" if it's not already included
        if "#NMA" not in text and message.chat.id == CHANNEL1:
            updated_text = f"{text}\n\n#NMA #General"

            if message.text:
                # Edit text message
                await message.edit_text(updated_text)
            elif message.caption or not message.media_group_id:
                # Edit media message with a caption
                await message.edit_caption(updated_text)

        if "#NMA" not in text and message.chat.id == CHANNEL2:
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
