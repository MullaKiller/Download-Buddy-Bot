import asyncio
import random
from typing import List

from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from plugins.bot import Bot


class MemberTagger:
    def __init__(self, batch_size: int = 5, delay: float = 2.0):
        self.batch_size = batch_size
        self.delay = delay

    async def is_admin(self, client: Bot, message: Message) -> bool:
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        except Exception:
            return False

    def create_mention(self, member) -> str:
        return f"<a href='tg://user?id={member.user.id}'>{member.user.first_name}</a>  "

    async def send_mentions(self, client: Bot, message: Message, members: List[str], thread_id: int = None):
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


def random_emoji():
    # List of emojis to use as reactions
    reactions_emoji = ["👍", "❤️", "🔥", "🥰", "👏", "🎉", "🤩", "😁", "🤔", "🤯", "🤬", "😢", "🤮", "💩", "🙏", "👌", "🕊️", "🤡", "🥱",
                       "🥴", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡️", "🍌", "🎃", "🎄", "☃️", "🎋", "🎊"]

    # Choose one random reaction
    return random.choice(reactions_emoji)
