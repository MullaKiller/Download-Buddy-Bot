import asyncio
import re

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import CHANNEL1, CHANNEL2
from plugins.bot import Bot
from plugins.utils.fake_reaction import run_all_bots
from plugins.utils.logger import get_logger
from plugins.utils.utility import MemberTagger, random_emoji_reaction

logger = get_logger(__name__)

'''
@dataclass
class Platform:
    name: str
    pattern: str


class MediaDownloader:
    SUPPORTED_PLATFORMS = {
        # "youtube": Platform("YouTube", r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'),
        "twitter": Platform("Twitter", r'(https?://)?(www\.)?(twitter\.com|x\.com)/.+'),
        "instagram": Platform("Instagram", r'(https?://)?(www\.)?(instagram\.com)/.+')
    }
    MAX_FILE_SIZE = 500 * 1024 * 1024
    PROGRESS_UPDATE_INTERVAL = 5
    OUTPUT_DIR = Path("outputs")

    def __init__(self):
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self._last_progress_update = {}
        self.api_key = EMBEDEZ_API_KEY
        self.youtube_service = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=self.api_key
        )

    def _cleanup_files(self, dirname: str) -> None:
        try:
            target_dir = self.OUTPUT_DIR / dirname
            if target_dir.exists():
                shutil.rmtree(target_dir)
        except Exception as e:
            logger.error(f"Error cleaning up directory: {str(e)}")

    async def _update_progress(self, current: int, total: int, message: Message,
                               status_msg: Message) -> None:
        try:

            # Ensure `current` and `total` are integers
            current = int(current)
            total = int(total)
            msg_id = f"{message.chat.id}-{status_msg.id}"
            now = datetime.now()

            # Update progress only if interval has elapsed
            if (msg_id not in self._last_progress_update or
                    (now - self._last_progress_update[msg_id]).total_seconds() >= self.PROGRESS_UPDATE_INTERVAL):
                progress = round(current * 100 / total)
                await status_msg.edit_text(f"Uploading...\n\n{progress}%")
                self._last_progress_update[msg_id] = now

        except Exception as e:
            logger.error(f"Progress update error: {str(e)}")

    async def download_yt_video_audio(self, message: Message, url: str, media_type: str = "video"):
        status_msg = await message.reply_text('Processing...')
        dirname = str(int(datetime.now().timestamp() * 1000))
        target_dir = self.OUTPUT_DIR / dirname

        try:
            logger.info(f"Starting download for URL: {url}")
            target_dir.mkdir(parents=True, exist_ok=True)

            # Extract the video ID from the URL
            video_id_match = re.search(r'(?:v=|youtu\.be/|shorts/)([\w-]+)', url)

            if not video_id_match:
                raise ValueError("Invalid YouTube URL.")

            video_id = video_id_match.group(1)
            logger.info(f"Extracted video ID: {video_id}")

            # Fetch video metadata
            request = self.youtube_service.videos().list(part="snippet,contentDetails", id=video_id)
            response = request.execute()

            if not response["items"]:
                raise ValueError("No video found with the provided ID.")

            video_info = response["items"][0]
            title = f"{video_info["snippet"]["title"]}\n\nRequested by {message.from_user.mention}\n\n{CUSTOM_MESSAGE}"
            duration = video_info["contentDetails"]["duration"]
            logger.info(f"Video metadata fetched. Title: {title}")

            # Use yt_dlp for downloading the video
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best' if media_type == "video" else 'bestaudio/best',
                'outtmpl': f'{target_dir}/{dirname}.%(ext)s',
                'max_filesize': self.MAX_FILE_SIZE,
                'quiet': False,  # Enable output for debugging
                'no_warnings': False,  # Enable warnings for debugging
                'verbose': True,  # Add verbose output
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }] if media_type == "video" else [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3'
                }],
            }

            logger.info("Starting yt-dlp download")
            await status_msg.edit_text('Starting download...')

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    logger.info("Extracting video info...")
                    info = ydl.extract_info(url, download=True)
                    logger.info("Info extraction completed")

                    if 'requested_downloads' not in info:
                        logger.error("No 'requested_downloads' in info")
                        raise ValueError("Download failed: No download information available")

                    filepath = info['requested_downloads'][0]['filepath']
                    logger.info(f"Download completed. Filepath: {filepath}")

                    if not Path(filepath).exists():
                        logger.error(f"File not found at path: {filepath}")
                        raise ValueError("Download failed: File not found")

                    # Check file size
                    file_size = Path(filepath).stat().st_size
                    logger.info(f"File size: {file_size} bytes")

                    if file_size > self.MAX_FILE_SIZE:
                        raise ValueError(f"File size exceeds {self.MAX_FILE_SIZE // 1024 // 1024}MB limit")

                    # Send to Telegram
                    await status_msg.edit_text('Sending file to Telegram...')
                    progress = partial(self._update_progress, message=message, status_msg=status_msg)

                    if media_type == "video":
                        await message.reply_video(filepath, caption=title, progress=progress)
                    else:
                        await message.reply_audio(filepath, title=title, progress=progress)

                    await status_msg.delete()

                except Exception as ydl_error:
                    logger.error(f"yt-dlp internal error: {str(ydl_error)}")
                    raise

        except HttpError as he:
            logger.error(f"YouTube API error: {str(he)}")
            await status_msg.edit_text('Failed to fetch video details 😞')
            await asyncio.sleep(15)
            await status_msg.delete()
        except yt_dlp.utils.DownloadError as de:
            logger.error(f"yt_dlp error: {str(de)}")
            await status_msg.edit_text(f'Download failed: {str(de)} 😞')
            await asyncio.sleep(15)
            await status_msg.delete()
        except ValueError as ve:
            logger.error(f"Value error: {str(ve)}")
            await status_msg.edit_text(str(ve))
            await asyncio.sleep(15)
            await status_msg.delete()
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            await status_msg.edit_text(f"Something went wrong: {str(e)} 😑")
            await asyncio.sleep(15)
            await status_msg.delete()
        finally:
            self._cleanup_files(dirname)

    async def download_twitter_video_audio(self, message: Message, url: str, media_type: str = "video",
                                           is_channel: bool = False):

        status_msg = await message.reply_text('Processing...')
        dirname = str(int(datetime.now().timestamp() * 1000))
        target_dir = self.OUTPUT_DIR / dirname
        try:
            target_dir.mkdir(parents=True, exist_ok=True)  # Create subdirectory

            # Use yt_dlp for downloading the video
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best' if media_type == "video" else 'bestaudio/best',
                'outtmpl': f'{target_dir}/{dirname}.%(ext)s',
                'max_filesize': self.MAX_FILE_SIZE,
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }] if media_type == "video" else [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3'
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filepath = info['requested_downloads'][0]['filepath']
                title = f"{info.get('title', 'Unknown Title')}\n\nRequested by {message.from_user.mention}\n\n{CUSTOM_MESSAGE}" if not is_channel else ""

                # Check file size
                if Path(filepath).stat().st_size > self.MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds {self.MAX_FILE_SIZE // 1024 // 1024}MB limit")

                await status_msg.edit_text('Sending file to Telegram...')
                progress = partial(self._update_progress, message=message, status_msg=status_msg)

                if media_type == "video":
                    await message.reply_video(filepath, caption=title, progress=progress)
                else:
                    await message.reply_audio(filepath, caption=title, progress=progress)
                await status_msg.delete()

        except yt_dlp.utils.DownloadError as ed:
            logger.error(f"Getting error from yt_dlp download error : {str(ed)}")
            await status_msg.edit_text('Download failed: 😞')
            await asyncio.sleep(15)
            await status_msg.delete()
        except ValueError as ve:
            logger.error(f"Value error : {str(ve)}")
            await asyncio.sleep(15)
            await status_msg.delete()
        except Exception as e:
            logger.error(f"Error : {str(e)}")
            await status_msg.edit_text(f"Something went wrong 😑")
            await asyncio.sleep(15)
            await status_msg.delete()
        finally:
            self._cleanup_files(dirname)

    async def download_instagram_post_and_reels(self, message: Message, url: str, is_channel: bool = False):

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

            if media_group and len(post.caption) < 950:
                words = post.caption
                media_group[
                    0].caption = f"{words}\n\nRequested by {message.from_user.mention}\n\n{CUSTOM_MESSAGE}" if not is_channel else ""

            # Send as group
            await message.reply_media_group(media_group)
            await status_msg.delete()

        except instaloader.exceptions.InstaloaderException as ie:
            logger.error(f" Instaloader error : {str(ie)}")
            await status_msg.edit_text('Download failed: 😞')
            await asyncio.sleep(15)
            await status_msg.delete()
        except ValueError as ve:
            logger.error(f"Value error : {str(ve)}")
            await asyncio.sleep(15)
            await status_msg.delete()

        except Exception as e:
            logger.error(f"Error : {str(e)}")
            await status_msg.edit_text(f"Error: {str(e)}")
            await asyncio.sleep(15)
            await status_msg.delete()
        finally:
            self._cleanup_files(dirname)

    def validate_url(self, url: str) -> Optional[Platform]:
        return next((platform for platform in self.SUPPORTED_PLATFORMS.values()
                     if re.match(platform.pattern, url)), None)
'''


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

        # Reactions methods
        await random_emoji_reaction(client, message)
        await run_all_bots(message)

        if message.chat.id not in [CHANNEL1, CHANNEL2]:
            return
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
