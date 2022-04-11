from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import *
import logging
import aiohttp
import os
import urllib.parse

BOT_TOKEN = '5267899048:AAHf1qikSVTAhilni6oCXePjIhv8hnGT_kg'
api_base = os.environ['API_BASE']
api_pics = os.environ['API_PICS']
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


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
    pics = types.MediaGroup()
    for meme in memes:
        pics.attach_photo(types.InputFile.from_url(meme['link']))
    await bot.send_media_group(message.chat.id, media=pics)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
