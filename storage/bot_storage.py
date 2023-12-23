from redis import Redis
from json import dumps, loads


class CaptchaBotStorage(Redis):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.captcha_time = 3600


    def found_startswith_key(self, user_id: int) -> dict:
        '''Получение всех ключей которые начинаются с user_id'''
        cursor = 0
        found_keys = []

        while True:
            cursor, keys = self.scan(cursor, match=f'{user_id}*')
            found_keys += [key.decode() for key in keys]

            if cursor == 0:
                break

        return found_keys
    

    def get_last(self, user_id: int):
        '''Получение последнего user'''

        user_keys = self.found_startswith_key(user_id)
        if not user_keys: return None
        return self.get(user_keys[-1]).decode()


    def save_user_join(self, user_id: int, chat_id: int) -> bool:
        user_join = {
            'chat': chat_id
        }
        return self.setex(f'{user_id} {chat_id}', self.captcha_time, dumps(user_join))


    def save_user_captcha(self, user_id: int, chat_id: int, captcha_animal: str, images: list, output: str) -> dict:
        user_key = self.found_startswith_key(user_id)[-1]
        captcha_template = []
        
        for i, j in enumerate(images):
            if j['animal'] == captcha_animal:
                captcha_template.append({
                    'animal_number': i + 1,
                    'animal_category': j['animal']
                })

        user = {
            'chat': chat_id,
            'captcha': {
                'animal': captcha_animal,
                'output_image': output,
                'captcha_template': captcha_template,
                'user_answers': [],
                'wrong_answers_count': 0,
            }
        }
        user_json = dumps(user)
        self.setex(user_key, self.captcha_time, user_json)

        return user


    def update_user_captcha_answers(self, user_id: int, page_number: int):
        key = self.found_startswith_key(user_id)[-1]
        user = self.get_last(user_id)
        user_alive = self.ttl(key)
        user = loads(user)
        user['captcha']['user_answers'].append(page_number)

        self.setex(key, user_alive, dumps(user)) 