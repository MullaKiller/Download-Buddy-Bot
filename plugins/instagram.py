import re
from typing import Tuple, List

import pyrogram.errors.exceptions.bad_request_400
import requests
from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.types import Message, InputMediaVideo, InputMediaPhoto

from config import settings
from plugins.bot import Bot
from plugins.utils.logger import get_logger
from plugins.utils.utility import random_emoji_reaction, get_random_emoji

logger = get_logger(__name__)

headers = {
    "x-rapidapi-key": "5226c6a5dcmsh9002aac61ae8062p133a64jsn6d35d386968e",
    "x-rapidapi-host": "instagram-best-experience.p.rapidapi.com"
}


def extract_post_from_link(url):
    # Regular expression pattern to match Instagram post IDs
    pattern = r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)/?'

    # Search for the pattern in the provided URL
    match = re.search(pattern, url)

    if match:
        return match.group(1)  # Return the captured group (post ID)
    else:
        return None  # Return None if no match is found


# filtering caption removing unnecessary #hastags
def retrieve_caption_and_filter(data) -> str:
    caption = ""
    if cap := data.get("caption"):
        caption = cap["text"]

    caption = caption.split('\n')
    cleaned_captions = []
    for line in caption:
        # Remove hashtags and the words that follow them
        words = line.split()
        filtered_words = [word for word in words if not word.startswith('#')]

        # Join the words back together and remove dots
        cleaned_line = ' '.join(filtered_words).replace('.', '')

        # Only add non-empty lines
        if cleaned_line.strip():
            cleaned_captions.append(cleaned_line.strip())

    # Join the lines back together
    final_text = '\n'.join(cleaned_captions)
    return f"{final_text}\n\n{settings.CUSTOM_MESSAGE}" if len(final_text) < 950 else ""


def retrieve_videos_and_images(data) -> Tuple[List[InputMediaPhoto], List[InputMediaVideo]]:
    all_video_url = []
    all_image_url = []

    if img_v2 := data.get("image_versions2"):
        all_image_url.append(InputMediaPhoto(img_v2["candidates"][0]["url"]))
    if video_v1 := data.get("video_versions"):
        all_video_url.append((InputMediaVideo(video_v1[0]["url"])))

    if "carousel_media" in data and isinstance(data["carousel_media"], list):
        for item in data["carousel_media"]:
            if img_v2 := item.get("image_versions2"):
                all_image_url.append(InputMediaPhoto(img_v2["candidates"][0]["url"]))

            if video_v1 := item.get("video_versions"):
                all_video_url.append(InputMediaVideo(video_v1[0]["url"]))

    return all_image_url, all_video_url


@Bot.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.incoming)
async def instagram(client: Bot, message: Message):
    url = message.text
    try:
        try:
            await message.delete()
        except RPCError:
            pass

        tmp = await message.reply_text("Please wait! 🫷")
        if post_id := extract_post_from_link(url):
            api_url = "https://instagram-best-experience.p.rapidapi.com/post"
            querystring = {"shortcode": f"{post_id}"}
            response = requests.get(api_url, headers=headers, params=querystring, timeout=10)

            if response.status_code == 200:
                data = response.json()
                all_image_url, all_video_url = retrieve_videos_and_images(data)
                caption = retrieve_caption_and_filter(data)
                caption = f"{caption}\nRequested by {message.from_user.mention}"

                if all_image_url:
                    all_image_url[0].caption = caption
                elif all_video_url:
                    all_video_url[0].caption = caption

                try:
                    message_list = await message.reply_media_group(all_image_url + all_video_url)
                    await random_emoji_reaction(client, message_list[0], emoji=get_random_emoji(max_emoji=1))

                except pyrogram.errors.exceptions.bad_request_400.MediaCaptionTooLong:
                    all_image_url[0].caption = ""
                    message_list = await message.reply_media_group(all_image_url + all_video_url)
                    await random_emoji_reaction(client, message_list[0], emoji=get_random_emoji(max_emoji=1))

                except pyrogram.errors.exceptions.bad_request_400.MultiMediaTooLong:
                    tmp_list = all_image_url + all_video_url
                    idx = 0
                    while idx < len(tmp_list):
                        if idx + 9 < len(tmp_list):
                            message_list = await message.reply_media_group(tmp_list[idx:idx + 9])
                            await random_emoji_reaction(client, message_list[0], emoji=get_random_emoji(max_emoji=1))
                            idx += 9
                        else:
                            message_list = await message.reply_media_group(tmp_list[idx:len(tmp_list)])
                            await random_emoji_reaction(client, message_list[0], emoji=get_random_emoji(max_emoji=1))
                            idx += 9

                logger.info(f"Successfully posted media group")

            else:
                await message.reply_text("No media found in the Instagram post.")

        else:
            await message.reply_text("Invalid link")
        await tmp.delete()

    except Exception as e:
        await message.reply_text(f"Something went wrong while processing your request {url}.")
        logger.error(f"Error processing Instagram URL {url}: {str(e)}")
    finally:
        await message.reply_text("Join @nationalMutthal")
