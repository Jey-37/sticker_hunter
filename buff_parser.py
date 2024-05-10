import asyncio
import json
import logging
from typing import Any

import aiohttp
from fake_useragent import UserAgent


class BuffParser():
    def __init__(self, items, stickers, notifier):
        self.stickers = stickers
        self.notifier = notifier
        self.items = items

        self.ua = UserAgent()

        self.timeout_time = 10

        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_item_data(self, item_id: int, item_name: str, session, retry: int = 3) -> list[dict]:
        item_buff_api_url = f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={item_id}&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1714321866242"
        
        items_data = []
        headers = {'User-Agent': self.ua.random}

        async with session.get(item_buff_api_url, headers=headers) as response:
            if response.ok:
                item_buff_data = (await response.json())['data']

                for item in item_buff_data['items']:
                    if len(item['asset_info']['info']['stickers']) == 0 or item['sticker_premium'] is None:
                        continue
                    
                    stickers_data = []
                    stickers_sum_price = 0
                    for sticker in item['asset_info']['info']['stickers']:
                        sticker_info = self.stickers.get(sticker['name'], None)

                        sticker_price = 0
                        if sticker_info and 'price' in sticker_info:
                            sticker_price = sticker_info['price']

                        stickers_sum_price += sticker_price

                        stickers_data.append({
                            "name": sticker['name'],
                            "wear": 100-int(sticker['wear']*100),
                            "price": sticker_price
                        })
                    else:
                        if 'inspect_url' in item['asset_info']['info']:
                            img_src = item['asset_info']['info']['inspect_url']
                        else:
                            img_src = item['asset_info']['info']['original_icon_url']
                        
                        item_info = {
                            "id": item_id,
                            "name": item_name,
                            "price": float(item['price']),
                            "min_price": float(item_buff_data['items'][0]['price']),
                            "float": item['asset_info']['paintwear'],
                            "img_src": img_src,
                            "sp": int(item['sticker_premium']*100),
                            "sticker_price": round(stickers_sum_price, 2),
                            "stickers": stickers_data,
                            "asset_info": item['asset_info'],
                            "sell_order_id": item["id"]
                        }

                        items_data.append(item_info)
        
                return items_data
            else:
                self.logger.warning(f'Got an error with fetching {item_name}')

        return []
        
    async def fetch_main_data(self) -> None:
        async with aiohttp.ClientSession() as session:
            ind = 0
            for item_id, item_name in self.items:
                item_data = await self.get_item_data(item_id=item_id, item_name=item_name, session=session)
                self.notifier.notify(item_data)
                ind += 1
                self.logger.info(f'[PROCESSED] ID {item_id} NAME {item_name} ({ind/len(self.items):.2f}%)')
