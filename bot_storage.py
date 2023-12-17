from aiogram import types

from json import loads, dumps
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def check_user(func):
    async def wrapper(message: types.Message):
        if not r.exists(message.from_user.id):
            return await message.answer('❗️ Вас нет в базе. Либо вы превысили лимит ожидания капчи. Попробуйте /reset @ссылка_на_группу')
        await func(message)
    return wrapper


class RedisBotStorage:
    
    def save_user_auth(user_id: int, chat_id: int, captcha_color: str, images: list, output: str) -> str:
        captcha_template = []
        for i in range(len(images)):
            if images[i]['color'] == captcha_color:
                captcha_template.append({
                    'color_number': i + 1,
                    'color_category': images[i]['color']
                })

        user_auth = {
            'chat': chat_id,
            'captcha': {
                'color': captcha_color,
                'output_image': output,
                'captcha_template': captcha_template,
                'user_answers': [],
                'wrong_answers_count': 0
            }
        }
        user_auth = dumps(user_auth)
        r.setex(user_id, 3600, user_auth)


    def update_user_captcha_answers(user_id: int, page_number: int):
        user_auth = r.get(user_id)
        user_auth_alive = r.ttl(user_id)

        user_auth = loads(user_auth)
        user_auth['captcha']['user_answers'] += [page_number]
        r.setex(user_id, user_auth_alive, dumps(user_auth)) 
