from os import environ
from pathlib import Path

BOT_TOKEN = environ.get('TG_CAPTCHA_BOT_TOKEN')

import logging

def logging_setup():
    logs = Path.cwd() / './logs'

    if not logs.exists():
        logs.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(level=logging.NOTSET)
    logger = logging.getLogger(__name__)

    debug_handler = logging.FileHandler(logs / 'debug.log')
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    debug_handler.setFormatter(debug_formatter)
    logger.addHandler(debug_handler)

    logging.getLogger().setLevel(logging.NOTSET)

    return logger