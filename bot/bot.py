from aiogram import Bot, Dispatcher, Router
from aiogram.filters.command import Command
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import Message, CallbackQuery
from aiogram.types import ChatMemberUpdated
from aiogram.types.input_file import FSInputFile
from asyncio import create_task

from json import loads, dumps

from .captcha import Captcha
from .bot_tools import CaptchaBotUtils
from .bot_tasks import captcha_dir_auto_remove
from .filters import ChatTypeFilter
from .middlewares import GetUserMiddleware

from storage.bot_storage import CaptchaBotStorage
from config.config import bot_logger, BOT_TOKEN, REDIS_HOST, REDIS_PORT, CAPTCHA_AUTH_ALIVE

# bot init
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router(name=__name__)
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())
router.message.filter(ChatTypeFilter(chat_type=['private']))

# Redis init
r = CaptchaBotStorage(REDIS_HOST, REDIS_PORT)
r.captcha_time = CAPTCHA_AUTH_ALIVE


@router.message(Command('start'))
async def start(message: Message) -> None:
    bot_logger.debug(f'Check user - {message.from_user.id} {message.from_user.first_name} {message.from_user.last_name}')
    await message.answer(CaptchaBotUtils.CAPTCHA_OPEN_SESSION_MESSAGE)

    user = r.get_last(message.from_user.id)
    user = loads(user)

    if not user.get('captcha'):
        random_animal, captcha_images, user_captcha_picture_path = Captcha.make_captcha_for_user(message.from_user.id)
        user = r.save_user_captcha(
            user_id=message.from_user.id,
            chat_id=user['chat'],
            captcha_animal=random_animal,
            images=captcha_images,
            output=user_captcha_picture_path
        )
        # Автоудаление папки если пользователь так и не стал проходить капчу
        create_task(captcha_dir_auto_remove(user_captcha_picture_path))

    await bot.send_photo(
        chat_id=message.from_user.id, 
        photo=FSInputFile(user['captcha']['output_image']), 
        caption=CaptchaBotUtils.CAPTCHA_CAPTION_MESSAGE.format(user['captcha']['animal']), 
        reply_markup=CaptchaBotUtils.CAPTCHA_KEYBOARD,
        parse_mode='HTML'
    )


@router.callback_query(lambda c: c.data in '1234')
async def update_user_answers_callback(callback: CallbackQuery) -> None:
    user = loads(r.get_last(callback.from_user.id))
    if not user.get('captcha'): return

    r.update_user_captcha_answers(callback.from_user.id, int(callback.data))


@router.callback_query(lambda c: c.data == 'send')
async def send_captcha_callback(callback: CallbackQuery) -> None:
        user = loads(r.get_last(callback.from_user.id))
        if not user.get('captcha'): return
        
        all_keys_startswith_user_id = r.found_startswith_key(callback.from_user.id)
        user_ttl = r.ttl(all_keys_startswith_user_id[-1])

        captcha_template_answers = [i['animal_number'] for i in user['captcha']['captcha_template']]

        if captcha_template_answers == sorted(user['captcha']['user_answers']):
            bot_logger.debug(f'''Captcha solve - {callback.from_user.username} Server - {user['chat']} ''')

            all_channels_with_mute = [i.split(' ')[-1] for i in all_keys_startswith_user_id]
            await CaptchaBotUtils.auto_unmute(bot, callback.from_user.id, all_channels_with_mute)
            r.delete(*all_keys_startswith_user_id)
            await callback.message.answer(CaptchaBotUtils.CAPTCHA_SUCCESS_MESSAGE)
            
        else:
            user['captcha']['user_answers'] = []
            user['captcha']['wrong_answers_count'] += 1

            if user['captcha']['wrong_answers_count'] >= CaptchaBotUtils.CAPTCHA_WRONG_ANSWER_COUNT:
                bot_logger.debug(f'''Captcha close - {callback.from_user.username} Server - {user['chat']} ''')
                r.delete(*all_keys_startswith_user_id)
                return await bot.send_message(chat_id=callback.from_user.id, text=CaptchaBotUtils.CAPTCHA_CLOSE_SESSION_MESSAGE)

            await bot.send_message(
                chat_id=callback.from_user.id,
                text=CaptchaBotUtils.CAPTCHA_WRONG_ANSWER_MESSAGE.format(
                    CaptchaBotUtils.CAPTCHA_WRONG_ANSWER_COUNT - user['captcha']['wrong_answers_count']
                    )
            )
            r.setex(all_keys_startswith_user_id[-1], user_ttl, dumps(user))


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def new_member(event: ChatMemberUpdated, bot: Bot) -> None:
    bot_logger.debug(f'''Mute user - {event.new_chat_member.user.id} {event.new_chat_member.user.username} Server - {event.chat.id} ''')

    r.save_user_join(event.new_chat_member.user.id, event.chat.id)
    await bot.restrict_chat_member(event.chat.id, event.new_chat_member.user.id, CaptchaBotUtils.MUTE_PERMISSION)
    await event.answer(CaptchaBotUtils.CAPTCHA_USER_JOIN_MESSAGE.format(event.new_chat_member.user.username))