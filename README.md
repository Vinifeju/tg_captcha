# Капча - бот для телеграм групп

### Инструкция

Если вы на Windows то для работа нам нужен WSL
Установка WSL - https://learn.microsoft.com/ru-ru/windows/wsl/install
после установки зайдите в консоль и просто пропишите `wsl` потом выйдите из mnt директории `cd ~`

Клонируем репозиторий
`git clone https://github.com/Vinifeju/tg_captcha`

Создадим виртуальное окружение
`python -m venv venv`

Активируем виртуальное окружение
`source venv/bin/activate`

Установим пакеты из requirements.txt
`pip3 install -r requirements.txt`

Установим пакет libvips для быстрой работы с изображениями
`sudo apt-get install libvips`

Ну и прописываем
`python3 main.py`

