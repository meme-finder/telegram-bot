from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import *
import logging
import aiohttp
import os
import urllib.parse
from PIL import Image
import json
import base64
from io import BytesIO

BOT_TOKEN = os.environ['TOKEN']
api_base = os.environ['API_BASE']
api_pics = os.environ['API_PICS']
api_offer = os.environ['API_OFFER']
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Predlozhka(StatesGroup):
    wait_for_name = State()
    wait_for_photo = State()


@dp.message_handler(commands=['offer'], state="*")
async def meme_offer(message: types.Message):
    await message.answer("Отправьте название мема")
    await Predlozhka.wait_for_name.set()
    print("waiting for name")


@dp.message_handler(state=Predlozhka.wait_for_name)
async def getting_name(message: types.Message, state: FSMContext):
    await state.update_data(meme_name=message.text)
    await message.answer("Теперь отправьте мем одним изображением максимального разрешения")
    await Predlozhka.wait_for_photo.set()
    print('waiting for photo')


@dp.message_handler(content_types=['photo'], state=Predlozhka.wait_for_photo)
async def getting_pic(message: types.Message, state: FSMContext):
    await message.photo[-1].download('picture.jpg')
    img = Image.open('picture.jpg')
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_byte = buffered.getvalue()
    img_base64 = base64.b64encode(img_byte)
    img_str = img_base64.decode('utf-8')
    data = await state.get_data()
    files = {
        "text": data['meme_name'],
        "img": img_str
    }
    session = aiohttp.ClientSession()
    await session.post(api_offer, json=json.dumps(files))
    await session.close()
    await message.answer("Спасибо за предложенный мем")
    await state.finish()


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
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
            pics.attach_photo(types.InputFile.from_url(meme['link']))
        await bot.send_media_group(message.chat.id, media=pics)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
