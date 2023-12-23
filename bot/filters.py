from aiogram.types import Message
from aiogram.filters import Filter


class ChatTypeFilter(Filter):
    def __init__(self, chat_type: list): # [2]
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type