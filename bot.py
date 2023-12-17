import asyncio

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import ChatMemberUpdated
from aiogram.handlers import MessageHandler
from aiogram.filters.command import Command
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.filters.base import Filter
from aiogram.enums import ParseMode

from bot_utils import *
from config import BOT_TOKEN, logging_setup
from captcha import Captcha
from bot_storage import r, RedisBotStorage, check_user

from json import loads, dumps
from pathlib import Path
from shutil import rmtree

import logging


bot = Bot(BOT_TOKEN)
dp = Dispatcher()
my_router = Router(name=__name__)

my_router.message.filter(
    ChatTypeFilter(chat_type=['private'])
)

bog_log = logging_setup()


async def bot_start() -> None:
    bog_log.debug('Bot started')


@my_router.message(Command('start'))
@check_user
async def start(message: types.Message) -> None:
    bog_log.debug(f'Check user - {message.from_user.id} {message.from_user.first_name} {message.from_user.last_name}')
    await message.answer('🔒 Подтвердите что вы человек')

    user = loads(r.get(message.from_user.id))
    await bot.send_photo(
        chat_id=message.from_user.id, 
        photo=types.FSInputFile(user['captcha']['output_image']), 
        caption=captcha_message.format(user['captcha']['color']), 
        reply_markup=captcha_keyboard,
        parse_mode='HTML'
    )
    

@my_router.callback_query()
@check_user
async def inline_keyboard_callback(callback: CallbackQuery) -> None:
    if callback.data == 'send':
        user = loads(r.get(callback.from_user.id))
        user_ttl = r.ttl(callback.from_user.id)

        captcha_template_answers = [str(i['color_number']) for i in user['captcha']['captcha_template']]

        if captcha_template_answers == user['captcha']['user_answers']:

            await bot.restrict_chat_member(user['chat'], callback.from_user.id, default_permission)

            r.delete(callback.from_user.id)
            rmtree(Path('captcha_images') / str(callback.from_user.id))
            await bot.send_message(
                chat_id=callback.from_user.id,
                text='✅ Капча успешно пройдена. Можете продолжить общение в группе'
            )

        else:
            user['captcha']['user_answers'] = []
            user['captcha']['wrong_answers_count'] += 1

            if user['captcha']['wrong_answers_count'] >= 3:
                r.delete(callback.from_user.id)
                rmtree(Path('captcha_images') / str(callback.from_user.id))
                return await bot.send_message(chat_id=callback.from_user.id, text=captcha_close_session_message)


            await bot.send_message(
                chat_id=callback.from_user.id,
                text=captcha_wrong_answer_message.format(captcha_wrong_answers_count - user['captcha']['wrong_answers_count'])
            )
            r.setex(callback.from_user.id, user_ttl, dumps(user))

    elif callback.data in ['1', '2', '3', '4']:
        RedisBotStorage.update_user_captcha_answers(callback.from_user.id, callback.data)


@my_router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def new_member(event: ChatMemberUpdated, bot: Bot) -> None:
    bog_log.debug(f'Mute user - {event.new_chat_member.user.id} {event.new_chat_member.user.first_name} {event.new_chat_member.user.first_name}')

    await bot.restrict_chat_member(event.chat.id, event.new_chat_member.user.id, mute_permission)
    await event.answer(f"<b>Вы, {event.new_chat_member.user.first_name} были замучены, пройдите пожалуйста капчу у меня</b>",
            parse_mode="HTML")

    random_color, captcha_images, user_captcha_picture_path = Captcha.make_captcha_for_user(event.new_chat_member.user.id)
    RedisBotStorage.save_user_auth(
        user_id=event.new_chat_member.user.id,
        chat_id=event.chat.id,
        captcha_color=random_color,
        images=captcha_images,
        output=user_captcha_picture_path
    )


async def main() -> None:
    dp.include_router(my_router)
    try:
        await bot_start()
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        bog_log.exception(f'Error {e}')


if __name__ == '__main__':
    asyncio.run(main())