import asyncio
import json
import logging
from typing import Any

import aiohttp
from fake_useragent import UserAgent


class StickerPriceUpdater():
    def __init__(self, stickers: dict[str:dict[str:Any]]):
        self.stickers = stickers

        self.ua = UserAgent()

        self.timeout_time = 10

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.WARNING)

    '''def get_sticker_price_by_history(self, item_id: int) -> float:
        item_trade_history_url = f"https://buff.163.com/api/market/goods/bill_order?game=csgo&goods_id={item_id}&_=1715161647506"

        response = requests.get(url=item_trade_history_url, headers={'User-Agent': self.ua.random})
        if 'data' in response.json():
            item_buff_data = response.json()['data']
            return float(item_buff_data['items'][0]['price'])

        return 0'''

    async def get_sticker_price(self, item_id: int, session, retry: int = 3) -> float:
        item_buff_api_url = f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={item_id}&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1714321866242"
        headers = {
            "User-Agent": self.ua.random,
            "Locale-Supported": "en",
        }
        
        async with session.get(item_buff_api_url, headers=headers) as response:
            if response.ok:
                item_buff_data = (await response.json())['data']
            
                if len(item_buff_data['items']):
                    return float(item_buff_data['items'][0]['price'])
            else:
                if retry > 0:
                    self.logger.info(f'retry={retry} => {item_buff_api_url}')
                    await asyncio.sleep(self.timeout_time)
                    return await self.get_sticker_price(item_id=item_id, session=session, retry=(retry - 1))
                
        return 0
        
    async def fetch_sticker_prices(self) -> None:
        async with aiohttp.ClientSession() as session:
            ind = 0
            for sticker_name, sticker_data in self.stickers.items():
                sticker_data['price'] = await self.get_sticker_price(item_id=sticker_data['id'], session=session)
                ind += 1
                self.logger.info(f'[PROCESSED] ID {sticker_data["id"]} NAME {sticker_name} ({ind/len(self.stickers):.2f}%)')
