from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import *
import logging
import aiohttp
import os
import urllib.parse
import base64
from io import BytesIO

BOT_TOKEN = os.environ['TOKEN']
api_base = os.environ['API_BASE']
api_pics = os.environ['API_PICS']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    print(
        f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    return True


@dp.message_handler(commands=['start', 'help'])
async def help_pls(message: types.Message):
    await message.answer('''Данный бот предназначен для поиска мемов по описанию. Чтобы найти мем, просто отправьте 
    боту его описание в текстовом виде, и он выдаст вам первые 10 мемов подходящих под ваще описание. Команда /next 
    - выдача следующих 10 мемов, команда /info - информация о создателях бота, API и тп''')


@dp.message_handler(commands=['info'])
async def info_pls(message: types.Message):
    await message.answer('''Lol данная команда пока не готова''')


@dp.message_handler(commands=['next'])
async def next_meme(message: types.Message):
    await message.answer('''Lol данная команда пока не готова''')


@dp.message_handler()
async def get_meme(message: types.Message):
    text = message.text
    session = aiohttp.ClientSession()
    response = await session.get(f"{api_base}/images?limit=10&q={urllib.parse.quote(text)}")
    memes = await response.json()
    await session.close()
    if len(memes) == 0:
        await message.answer('''Error 404 memes not found''')
    else:
        pics = types.MediaGroup()
        for meme in memes:
            id = meme['id']
            link = f"{api_pics}/normal/{id[:2]}/{id[2:4]}/{id}.webp"
            pics.attach_photo(types.InputFile.from_url(link))
        await bot.send_media_group(message.chat.id, media=pics)


@dp.message_handler(content_types=['document'])
async def post_meme(message: types.Message):
    img = BytesIO()
    img_bytes = await message.document.thumb.download(destination=img)
    img_base64 = base64.b64encode(img_bytes.read())
    img_str = img_base64.decode('utf-8')
    files = {
        "text": message.text,
        "image": img_str
    }
    session = aiohttp.ClientSession()
    await session.post(f'{api_base}/images', json=files)
    await session.close()
    await message.answer("Спасибо за предложенный мем")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
