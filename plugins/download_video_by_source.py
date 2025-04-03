import asyncio
import os
import random
import string

import aiohttp
import requests
from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.types import Message

from plugins.bot import Bot


@Bot.on_message(filters.channel & filters.command("d") & filters.chat(-1002417478505))
async def download_video_by_source(client: Bot, message: Message):

    try:
        get_url = message.text.split(" ")[-1]
        full_path = await download_video(get_url, "./outputs")
        if full_path:
            await client.send_video(chat_id=message.chat.id, video=full_path)
            os.remove(full_path)
            await message.delete()
        else:
            await message.reply_text("can't download the video something went wrong!")

    except RPCError as e:
        tmp = await message.reply_text(f"something went wrong ! {e}")
        await asyncio.sleep(5)
        await tmp.delete()


async def download_video(url, save_path):
    try:
        # Extract file name from URL
        file_name = generate_random_name() + ".mp4"
        full_path = os.path.join(save_path, file_name)
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(full_path, 'wb') as file:
                        while True:
                            chunk = await response.content.read(1024*1024)  # Read in chunks of 1 MB
                            if not chunk:
                                break
                            file.write(chunk)
                    print(f"Video downloaded successfully: {full_path}")
                    return full_path
                else:
                    print(f"Failed to download video. HTTP Status Code: {response.status}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Generate a random verification token
def generate_random_name() -> str:
    return "".join(random.choices(string.ascii_letters, k=4))