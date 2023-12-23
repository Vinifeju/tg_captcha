from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any

from .bot_tools import CaptchaBotUtils
from storage.bot_storage import CaptchaBotStorage


class GetUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        

        user_keys = CaptchaBotStorage().found_startswith_key(event.from_user.id)
        if user_keys:
            return await handler(event, data)
        
        return await event.answer(CaptchaBotUtils.CAPTCHA_NO_SESSION_MESSAGE)