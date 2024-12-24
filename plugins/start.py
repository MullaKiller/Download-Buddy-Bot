import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Optional
import instaloader
import yt_dlp
from pyrogram import filters
from pyrogram.types import Message, InputMediaVideo, InputMediaPhoto

from plugins.bot import Bot


class MediaType(Enum):
    VIDEO = "video"
    AUDIO = "audio"
    PHOTO = "photo"


@dataclass
class Platform:
    name: str
    pattern: str


class MediaDownloader:
    SUPPORTED_PLATFORMS = {
        "youtube": Platform("YouTube", r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'),
        "twitter": Platform("Twitter", r'(https?://)?(www\.)?(twitter\.com|x\.com)/.+'),
        "instagram": Platform("Instagram", r'(https?://)?(www\.)?(instagram\.com)/.+')
    }
    MAX_FILE_SIZE = 500 * 1024 * 1024
    PROGRESS_UPDATE_INTERVAL = 5
    OUTPUT_DIR = Path("outputs")

    def __init__(self):
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self._last_progress_update = {}

    def _cleanup_files(self, dirname: str) -> None:
        try:
            target_dir = self.OUTPUT_DIR / dirname
            print(target_dir)
            if target_dir.exists():
                shutil.rmtree(target_dir)
        except Exception as e:
            print(f"Error cleaning up directory: {e}")

    async def _update_progress(self, current: int, total: int, message: Message,
                               status_msg: Message) -> None:
        msg_id = f"{message.chat.id}-{status_msg.id}"
        now = datetime.now()

        if (msg_id not in self._last_progress_update or
                (now - self._last_progress_update[msg_id]).total_seconds() >= self.PROGRESS_UPDATE_INTERVAL):
            try:
                progress = round(current * 100 / total)
                await status_msg.edit_text(f"Uploading...\n\n{progress}%")
                self._last_progress_update[msg_id] = now
            except Exception as e:
                print(f"Progress update error: {e}")

    async def downoad_yt_x_videos(self, message: Message, url: str, media_type: str = "video"):

        status_msg = await message.reply_text('Processing...')
        dirname = str(int(datetime.now().timestamp() * 1000))
        target_dir = self.OUTPUT_DIR / dirname
        try:
            target_dir.mkdir(parents=True, exist_ok=True)  # Create subdirectory

            # choosing media type
            if media_type == "video":
                print("cum video")
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': f'{target_dir}/{dirname}.%(ext)s',
                    'max_filesize': self.MAX_FILE_SIZE,
                    'cookiefile': './cookies.txt',
                    'quiet': True,
                    'no_warnings': True,
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4'
                    }]
                }
            else:
                print("cum audio ")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{target_dir}/{dirname}.%(ext)s',
                    'max_filesize': self.MAX_FILE_SIZE,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3'
                    }]
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = f"{info.get('title', 'Unknown Title')}\n\nDownloaded by @nationalMutthal"

                if media_type == "video":
                    metadata = {
                        'caption': title,
                        'width': info['requested_downloads'][0].get('width'),
                        'height': info['requested_downloads'][0].get('height'),
                        'duration': info.get('duration')
                    }
                else:
                    metadata = {
                        'title': title,
                        'performer': info.get('uploader', 'Unknown'),
                        'duration': info.get('duration'),
                        'caption': title
                    }
                filepath = info['requested_downloads'][0]['filepath']
                if isinstance(filepath, (int, float)):
                    raise ValueError("Invalid file path received")

                if Path(filepath).exists() and Path(filepath).stat().st_size > self.MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds {self.MAX_FILE_SIZE // 1024 // 1024}MB limit")
                await status_msg.edit_text('Sending file to Telegram...')
                progress = partial(self._update_progress, message=message, status_msg=status_msg)

                if media_type == "video":
                    await message.reply_video(filepath, progress=progress, **metadata)
                else:
                    await message.reply_audio(filepath, progress=progress, **metadata)
                await status_msg.delete()

        except yt_dlp.utils.DownloadError:
            await status_msg.edit_text('Download failed: 😞')
        except ValueError as ve:
            await status_msg.edit_text(str(ve))
        except Exception as e:
            await status_msg.edit_text(f"Error: {str(e)}")
        finally:
            self._cleanup_files(dirname)

    async def download_instagram_post_and_reels(self, message: Message, url: str):

        status_msg = await message.reply_text('Processing...')
        dirname = str(int(datetime.now().timestamp() * 1000))
        target_dir = self.OUTPUT_DIR / dirname

        try:
            target_dir.mkdir(parents=True, exist_ok=True)  # Create subdirectory

            # Extract shortcode from URL (handles both /p/ and /reel/ URLs)
            if "/p/" in url:
                shortcode = url.split("/p/")[1].split("/")[0]
            elif "/reel/" in url:
                shortcode = url.split("/reel/")[1].split("/")[0]
            else:
                raise ValueError("Invalid Instagram URL. Must be a post or reel URL.")

            # Get post using shortcode
            L = instaloader.Instaloader(dirname_pattern=f"{self.OUTPUT_DIR / dirname}")
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target=f"{self.OUTPUT_DIR / dirname}")  # Download to subdirectory

            # Handle media files
            media_files = []
            base_pattern = f"{post.date_utc:%Y-%m-%d_%H-%M-%S}_UTC"

            # Look for both numbered and non-numbered files
            for file in target_dir.glob(f"{base_pattern}*.jpg"):
                media_files.append(file)
            for file in target_dir.glob(f"{base_pattern}*.mp4"):
                media_files.append(file)

            # For carousel posts, there will be additional numbered files
            if post.typename == "GraphSidecar":
                base_path = self.OUTPUT_DIR / dirname / f"{post.owner_username}_{post.date_utc:%Y-%m-%d_%H-%M-%S}_UTC"
                i = 1
                while (base_path.parent / f"{base_path.stem}_{i}.jpg").exists():
                    media_files.append(base_path.parent / f"{base_path.stem}_{i}.jpg")
                    i += 1
                while (base_path.parent / f"{base_path.stem}_{i}.mp4").exists():
                    media_files.append(base_path.parent / f"{base_path.stem}_{i}.mp4")
                    i += 1

            # Check file sizes
            for file_path in media_files:
                if file_path.stat().st_size > self.MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds {self.MAX_FILE_SIZE // 1024 // 1024}MB limit")

            # Send files to Telegram
            await status_msg.edit_text('Sending files to Telegram...')

            # Create media group
            media_group = []
            for media_file in sorted(media_files):
                if media_file.suffix.lower() in ['.mp4', '.mov', '.avi']:
                    media_group.append(InputMediaVideo(media_file))
                else:
                    media_group.append(InputMediaPhoto(media_file))

            # Add caption to first media only
            if media_group:
                media_group[0].caption = f"{post.caption}\n\nDownloaded by @nationalMutthal"

            # Send as group
            await message.reply_media_group(media_group)
            await status_msg.delete()

        except instaloader.exceptions.InstaloaderException:

            await status_msg.edit_text('Download failed: 😞')

        except ValueError as ve:

            await status_msg.edit_text(str(ve))

        except Exception as e:

            await status_msg.edit_text(f"Error: {str(e)}")

        finally:
            self._cleanup_files(dirname)

    def validate_url(self, url: str) -> Optional[Platform]:
        return next((platform for platform in self.SUPPORTED_PLATFORMS.values()
                     if re.match(platform.pattern, url)), None)


@Bot.on_message(filters.text & filters.group & ~filters.command("audio"))
async def download_command(client: Bot, message: Message):
    downloader = MediaDownloader()
    url = message.text
    print(message.text)
    if downloader.SUPPORTED_PLATFORMS["youtube"] == downloader.validate_url(url) or downloader.SUPPORTED_PLATFORMS[
        "twitter"] == downloader.validate_url(url):
        await downloader.downoad_yt_x_videos(message, url)
    elif downloader.SUPPORTED_PLATFORMS["instagram"] == downloader.validate_url(url):
        await downloader.download_instagram_post_and_reels(message, url)


@Bot.on_message(filters.command("audio") & filters.group)
async def download_audio_command(client: Bot, message: Message):
    print(f"Command received: {message.text}")
    print(f"Chat type: {message.chat.type}")
    print(f"Is command: {message.text.startswith('/')}")
    print(f"Is group: {message.chat.type == 'group' or message.chat.type == 'supergroup'}")

    try:
        # Extract URL
        if len(message.text.split()) > 1:
            url = message.text.split(maxsplit=1)[1].strip()
            print(f"URL from direct command: {url}")
        elif message.reply_to_message and message.reply_to_message.text:
            url = message.reply_to_message.text.strip()
            print(f"URL from reply: {url}")
        else:
            print("No URL found")
            await message.reply_text("Please provide a URL or reply to a message containing a URL")
            return

        downloader = MediaDownloader()
        platform = downloader.validate_url(url)
        print(f"Detected platform: {platform.name if platform else 'None'}")

        if not platform:
            await message.reply_text("Invalid URL. Please provide a valid YouTube, Twitter, or Instagram URL")
            return

        print(f"Processing URL: {url} for platform: {platform.name}")
        if platform == downloader.SUPPORTED_PLATFORMS["youtube"] or \
                platform == downloader.SUPPORTED_PLATFORMS["twitter"]:
            await downloader.downoad_yt_x_videos(message, url, "audio")
        elif platform == downloader.SUPPORTED_PLATFORMS["instagram"] and "/reel/" in url:
            await downloader.downoad_yt_x_videos(message, url, "audio")
        else:
            await message.reply_text("This type of content cannot be converted to audio")

    except Exception as e:
        print(f"Error in audio command: {str(e)}")
        await message.reply_text(f"Error processing audio command: {str(e)}")