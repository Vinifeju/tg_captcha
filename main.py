from asyncio import run
from icecream import ic

from bot.bot import bot, dp, router
from config.config import bot_logger


async def bot_start() -> None:
    bot_logger.debug('Bot started')


async def main() -> None:
    dp.include_router(router=router)
    await bot_start()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    try:
        run(main())
    except BaseException as e:
        ic(e)
        bot_logger.exception(f'Error {e}')
    