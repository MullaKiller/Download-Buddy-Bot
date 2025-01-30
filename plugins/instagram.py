import json

import requests
from pyrogram import filters
from pyrogram.types import Message, InputMediaVideo, InputMediaPhoto

from config import CUSTOM_MESSAGE, EMBEDEZ_API_KEY
from plugins.bot import Bot
from plugins.utils.logger import get_logger
from plugins.utils.utility import random_reactions

logger = get_logger(__name__)

header = {"Authorization": f"Bearer {EMBEDEZ_API_KEY}"}


# filtering caption removing unnecessary #hastags
async def filter_caption(caption: str) -> str:
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
    return f"{final_text}\n\n{CUSTOM_MESSAGE}" if len(final_text) < 1024 else ""


@Bot.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.incoming)
async def instagram(client: Bot, message: Message):
    try:
        url = message.text
        api_url = f"https://embedez.com/api/v1/providers/combined?q={url}"
        response = requests.get(api_url, headers=header)

        logger.info(f"embedez api connected succesfully!")
        if response.status_code == 200:
            data = response.json()
            # print(json.dumps(data, indent=4))
            content = data['data']['content']
            caption = f"{await filter_caption(content['description'])}\nRequested by {message.from_user.mention} "

            media_group = []
            for media in content['media']:

                if len(media_group) == 10:
                    break

                if "/reel/" in url and media['type'] == "video":
                    media_group.append(InputMediaPhoto(media["thumbnail"]["url"]))
                    media_group.append(InputMediaVideo(media["source"]["url"]))

                elif "/p/" in url:
                    if media['type'] == "photo":
                        media_group.append(InputMediaPhoto(media["source"]["url"]))
                    elif media['type'] == "video":
                        media_group.append(InputMediaVideo(media["source"]["url"]))

            media_group[0].caption = caption
            message_list = await message.reply_media_group(media_group)
            await random_reactions(client, message_list[0])
        else:
            await message.reply_text(
                "I only download public and non-adult photos and videos🫥\n Join @nationalMutthal !")

        await message.delete()
    except Exception as e:
        await message.reply_text("Something went wrong!😑\n Join @nationalMutthal !")
        logger.error(f"Error: {str(e)}")
    finally:
        await message.reply_text("https://t.me/nationalMutthal/321")
