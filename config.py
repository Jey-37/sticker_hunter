import os
from dotenv import load_dotenv

load_dotenv()


import logging

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s  %(levelname)s %(name)s: %(message)s", 
    datefmt='%I:%M:%S')

logging.getLogger("asyncio").setLevel(logging.WARNING)


from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

BOT_TOKEN = os.getenv('BOT_TOKEN')

dp = Dispatcher()
bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
