from aiogram import Bot, Dispatcher, executor, types
import logging
import aiohttp
import os
import urllib.parse

BOT_TOKEN = os.environ['TOKEN']
api_base = os.environ['API_BASE']
api_pics = os.environ['API_PICS']
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


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
    response = await session.get(f"{api_base}/images?s={urllib.parse.quote(text.encode('utf-8'))}")
    memes = await response.json()
    pics = []
    for meme in memes:
        link = meme['link']
        pics.append(link)
    for i in range(10):
        await bot.send_photo(message.chat.id, types.InputFile.from_url(pics[i])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
