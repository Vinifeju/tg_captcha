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

Создаем бота в BotFather и кидаем его токен в переменную окружения
`export TG_CAPTCHA_BOT_TOKEN=<Ваш токен>` 

Ну и прописываем
`python3 main.py`


Приглашаем бота в вашу любую группу и даем ему права мутить пользователей
![бот](https://i.ibb.co.com/P9VXTdP/2023-12-25-160338.png)

###Проверял на версииях питона - `Python 3.10.12` на `3.12` вроде как не работает aiogram на `3.11` должно все работать

