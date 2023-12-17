from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ChatPermissions, Message
from aiogram.filters import Filter

captcha_wrong_answers_count = 3

captcha_message = '🔍 Выберите одну (или несколько) частей этого фото в которых преобладает цвет {0} потом нажмите <b>Отправить</b>'
captcha_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='1', callback_data='1'),
            InlineKeyboardButton(text='2', callback_data='2'),
            InlineKeyboardButton(text='3', callback_data='3'),
            InlineKeyboardButton(text='4', callback_data='4'),
        ],
        [
            InlineKeyboardButton(text='🔑 Отправить', callback_data='send'),
        ]

    ]
)
captcha_wrong_answer_message = '❌ Ответ неверный, у вас есть еще {0} попыток, после чего сессия будет закрыта.'
captcha_close_session_message = '🔒 Вы потратили все свои попытки, сессия закрыта.'

mute_permission = ChatPermissions(
    can_send_messages=False,
)

default_permission = ChatPermissions(
    can_send_messages=True,
)


# Фильтр для ДМ
class ChatTypeFilter(Filter):
    def __init__(self, chat_type: list): # [2]
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type