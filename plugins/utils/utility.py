import asyncio
import random
from typing import List

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import Message

# from plugins.bot import Bot
from plugins.utils.logger import get_logger

logger = get_logger(__name__)


class MemberTagger:
    def __init__(self, batch_size: int = 5, delay: float = 2.0):
        self.batch_size = batch_size
        self.delay = delay

    async def is_admin(self, client: Client, message: Message) -> bool:
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        except Exception:
            return False

    def create_mention(self, member) -> str:
        return f"<a href='tg://user?id={member.user.id}'>{member.user.first_name}</a>  "

    async def send_mentions(self, client: Client, message: Message, members: List[str], thread_id: int = None):
        mentions_text = " ".join(members)

        if not message.reply_to_message.forward_from and not message.reply_to_message.forward_from_chat and not thread_id:
            await message.reply_to_message.reply(text=mentions_text)
        else:
            text = message.reply_to_message.text or message.reply_to_message.caption or ""
            if message.reply_to_message.text:
                await client.send_message(chat_id=message.chat.id, text=f"{text}\n{mentions_text}",
                                          reply_to_message_id=thread_id if thread_id else message.reply_to_message.id)
            elif message.reply_to_message.media:
                await message.reply_to_message.copy(chat_id=message.chat.id, caption=f"{text}\n{mentions_text}",
                                                    reply_to_message_id=thread_id if thread_id else message.reply_to_message.id)

        await asyncio.sleep(self.delay)

    async def process_members(self, client, chat_id: int) -> List[str]:
        members = []
        async for member in client.get_chat_members(chat_id):
            if not member.user.is_bot and not member.user.is_deleted:
                members.append(self.create_mention(member))
        return members


def get_random_emoji(max_emoji: int) -> List:
    reactions_emoji = [
        "👍", "👎", "❤️", "🔥", "🥰", "👏", "😁", "🤔",
        "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩",
        "🙏", "👌", "🕊️", "🤡", "🥱", "🥴", "😍", "🐳",
        "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡️", "🍌", "🏆",
        "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈",
        "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈",
        "😇", "😨", "🤝", "✍️", "🤗", "🫡", "🎅", "🎄",
        "☃️", "💅", "🗿", "🆒", "💘", "🙊", "🦄", "🤪",
        "😘", "💊", "🙈", "😎", "👾", "🤷‍♂️", "🤷‍♀️", "🤷", "😡"
    ]
    return random.choices(reactions_emoji, k=max_emoji)


async def random_emoji_reaction(client: Client, message: Message, emoji):
    max_retry = 15
    retry = 0
    while retry < max_retry:
        try:
            retry += 1
            await client.send_reaction(message_id=message.id, chat_id=message.chat.id, emoji=emoji)
            return
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
            try:
                await client.send_reaction(message_id=message.id, chat_id=message.chat.id, emoji=emoji)
                return
            except Exception as e:
                logger.error(f"Something went wrong again and again ! : {str(e)}")
        except Exception as e:
            logger.error(f"Set reaction failed. Retrying again {retry} bot name : {client.name}")
            # raise Exception(f"set reaction failed : {client.name}")
