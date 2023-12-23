import pyvips

from pathlib import Path
from os import listdir
from random import choice
from time import strftime
from config.config import CAPTCHA_IMAGES_TEMPLATES


class Captcha:
    def combine_captcha_images(captcha_images: dict, user_id: int) -> str:
        images = [pyvips.Image.new_from_file(img['image']) for img in captcha_images]
        bands = images[0].bands

        width, height = images[0].width, images[0].height
        combined_image = pyvips.Image.black(2 * width, 2 * height, bands=bands)

        for i, img in enumerate(images):
            row = i // 2
            col = i % 2

            if img.bands != bands:
                img = img.bandjoin([0] * (bands - img.bands))

            combined_image = combined_image.insert(img, col * width, row * height)

        script_directory = Path(__file__).resolve().parent.parent
        user_captcha_output_dir = script_directory / 'captcha_images' / str(user_id) / strftime('%d.%m.%Y %H_%M_%S')
        user_captcha_output_dir.mkdir(parents=True, exist_ok=True)

        user_output_file = user_captcha_output_dir / 'output.png'
        user_output_file_str = str(user_output_file)
        combined_image.write_to_file(user_output_file_str)
        
        return user_output_file_str


    def make_captcha_for_user(user_id: int) -> tuple:
        script_directory = Path(__file__).resolve().parent.parent
        captcha_images = script_directory / 'captcha_images' / CAPTCHA_IMAGES_TEMPLATES
        all_images = []
        for animal in listdir(captcha_images):
            data = {'animal': animal, 'images': []}
            animal = captcha_images / animal

            for png in listdir(animal):
                data['images'].append(str(animal / png))
            all_images.append(data)

        captcha_images = []
        while len(captcha_images) < 4:
            data = {
                'animal': '',
                'image': ''
            }
            animal = choice(all_images)
            if not animal['images']: 
                all_images.remove(animal)
                continue

            random_picture = choice(animal['images'])
            animal['images'].remove(random_picture)
            data['animal'] = animal['animal']
            data['image'] = random_picture
            captcha_images.append(data)

        return choice(captcha_images)['animal'], captcha_images, Captcha.combine_captcha_images(captcha_images, user_id)