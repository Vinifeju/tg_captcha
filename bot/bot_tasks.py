import asyncio
from shutil import rmtree
from pathlib import Path
from config.config import USER_CAPTCHA_DIR_ALIVE

async def captcha_dir_auto_remove(captcha_dir_path: str):
    await asyncio.sleep(USER_CAPTCHA_DIR_ALIVE)

    captcha_dir = Path(captcha_dir_path)

    if captcha_dir.exists():
        rmtree(captcha_dir.parent.parent)