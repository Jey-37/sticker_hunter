from aiogram.filters import CommandStart
from aiogram.types import Message

from config import dp


@dp.message(CommandStart())
async def start_command_handler(message: Message):
    print(message.chat.id)
    