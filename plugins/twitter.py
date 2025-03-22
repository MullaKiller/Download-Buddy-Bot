import re
from typing import Tuple, List

import pyrogram.errors.exceptions.bad_request_400
import requests
from pyrogram import filters
from pyrogram.types import Message, InputMediaVideo, InputMediaPhoto

from config import settings
from plugins.bot import Bot
from plugins.utils.logger import get_logger
from plugins.utils.utility import random_emoji_reaction, get_random_emoji

logger = get_logger(__name__)

headers = {
    "x-rapidapi-key": "5226c6a5dcmsh9002aac61ae8062p133a64jsn6d35d386968e",
    "x-rapidapi-host": "twitter-api45.p.rapidapi.com"
}


def extract_post_from_link(url):
    # Regular expression pattern to match Instagram post IDs
    pattern = r'/(?:status)/([A-Za-z0-9_-]+)/?'

    # Search for the pattern in the provided URL
    match = re.search(pattern, url)

    if match:
        return match.group(1)  # Return the captured group (post ID)
    else:
        return None  # Return None if no match is found


# filtering caption removing unnecessary #hastags
def retrieve_caption_and_filter(data) -> str:
    caption = data.get("display_text") if data.get("display_text") else ""
    url_regex = r"https?://\S+|www\.\S+"
    caption = re.sub(url_regex, "", caption)

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

    if entities := data.get("entities"):

        if medias := entities.get("media"):

            for media in medias:

                if photo := media.get("media_url_https"):
                    all_image_url.append(InputMediaPhoto(photo))

                if video_info := media.get("video_info"):
                    if video_url := video_info.get("variants")[-1]["url"]:
                        all_video_url.append(InputMediaVideo(video_url.split("?")[0]))

    return all_image_url, all_video_url


@Bot.on_message(filters.regex(r'(https?://)?(www\.)?(twitter\.com|x\.com)/.+') & filters.incoming)
async def twitter(client: Bot, message: Message):
    url = message.text

    try:
        await message.delete()
        tmp = await message.reply_text("Please wait! 🫷")
        if post_id := extract_post_from_link(url):
            api_url = "https://twitter-api45.p.rapidapi.com/tweet.php"
            querystring = {"id": f"{post_id}"}
            response = requests.get(api_url, headers=headers, params=querystring)
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

                logger.info(f"Successfully posted media group")
        else:
            await message.reply_text("No media found in the Instagram post.")
        await tmp.delete()
    except Exception as e:
        await message.reply_text(f"Something went wrong while processing your request {url}.")
        logger.error(f"Error processing Twitter URL {url}: {str(e)}")
    finally:
        await message.reply_text("Join @nationalMutthal")
