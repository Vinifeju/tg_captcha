
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ChatPermissions
from aiogram import Bot


class CaptchaBotUtils:

    BOT_CAPTCHA_LABELS = {
        'black': 'Черный',
        'blue': 'Синий',
        'brown': 'Коричневый',
        'green': 'Зеленый',
        'purple': 'Пурпурный',
        'red': 'Красный',
        'yellow': 'Желтый',
    }

    CAPTCHA_USER_JOIN_MESSAGE = '@{0} Пройдите проверку у меня, для получения доступа к чату'
    CAPTCHA_OPEN_SESSION_MESSAGE = '🔑 Подтвердите что вы человек'
    CAPTCHA_CAPTION_MESSAGE = '🔍 Выберите одну (или несколько) частей этого фото в которых есть животное - <b>{0}</b> потом нажмите <b>Отправить</b>'
    CAPTCHA_WRONG_ANSWER_MESSAGE = '❌ Ответ неверный, у вас есть еще {0} попыток, после чего сессия будет закрыта'
    CAPTCHA_SUCCESS_MESSAGE = '✅ Можете продолжить общение в чате'
    CAPTCHA_CLOSE_SESSION_MESSAGE = '🔒 Вы потратили все свои попытки, сессия закрыта'
    CAPTCHA_NO_SESSION_MESSAGE = '❗ Вас нет в базе данных. Либо ваша сессия закрыта'
    CAPTCHA_WRONG_ANSWER_COUNT = 3

    CAPTCHA_KEYBOARD = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 5)
            ],
            [
                InlineKeyboardButton(text='🔑 Отправить', callback_data='send'),
            ]
        ]
    )

    MUTE_PERMISSION = ChatPermissions(
        can_send_messages=False,
    )
    DEFAULT_PERMISSION = ChatPermissions(
        can_send_messages=True,
    )

    async def auto_unmute(bot: Bot, user_id: int, channels: list):
        for channel in channels:
            await bot.restrict_chat_member(channel, user_id, CaptchaBotUtils.DEFAULT_PERMISSION)