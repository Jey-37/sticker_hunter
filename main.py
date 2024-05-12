import asyncio
import logging
import random
import json

import config
from sticker_price_updater import StickerPriceUpdater
from buff_parser import BuffParser
from notifying import BotNotifier
import message_handlers


def read_json(file_name: str):
    with open(file_name, 'r') as file:
        return json.load(file)

def write_json(file_name: str, data):
    with open(file_name, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


async def sticker_price_updater_task(stickers):
    sticker_updater = StickerPriceUpdater(stickers)
    logging.getLogger("StickerPriceUpdater").setLevel(logging.WARNING)

    try:
        while True:
            await sticker_updater.fetch_sticker_prices()
            write_json('data\\stickers.json', stickers)
            await asyncio.sleep(7200)
    finally:
        write_json('data\\stickers.json', stickers)


async def buff_parser_task(stickers):
    with open('data\\itemids.txt', 'r') as file:
        items = [line.strip().split(';') for line in file]
    random.shuffle(items)

    users = [404404154, 497136005]
    notifier = BotNotifier(config.bot, users)
    buff_parser = BuffParser(items, stickers, notifier)

    while True:
        await buff_parser.fetch_main_data()


async def main():
    stickers = read_json('data\\stickers.json')

    loop = asyncio.get_event_loop()
    loop.create_task(sticker_price_updater_task(stickers))
    loop.create_task(buff_parser_task(stickers))


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
