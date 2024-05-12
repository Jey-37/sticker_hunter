import asyncio
import logging
from datetime import datetime

import aiohttp
from fake_useragent import UserAgent


class BuffParser():
    ITEM_API_URL_TEMPLATE = "https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={item_id}&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1714321866242"

    def __init__(self, items, stickers, notifier):
        self.stickers = stickers
        self.notifier = notifier
        self.items = items

        self.ua = UserAgent()

        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_item_data(self, item_id: int, item_name: str, session, retry: int = 3) -> list[dict] | None:
        url = BuffParser.ITEM_API_URL_TEMPLATE.format(item_id=item_id)
        
        headers = {
            "User-Agent": self.ua.random,
            "Locale-Supported": "en",
        }

        async with session.get(url, headers=headers) as response:
            if response.ok:
                item_buff_data = (await response.json())['data']

                items_data = []

                for item in item_buff_data['items']:
                    try:
                        if len(item['asset_info']['info']['stickers']) == 0 or item['sticker_premium'] is None:
                            continue
                    
                        stickers_data = []
                        stickers_sum_price = 0
                        for sticker in item['asset_info']['info']['stickers']:
                            sticker_info = self.stickers.get(
                                sticker['name'].lower().replace("  ", " "), None)
                            if sticker_info is None:
                                self.logger.info(f"Unknown sticker showed up: {sticker['name']}")
                                break

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
                                "sell_order_id": item['id'],
                                "created_at": datetime.fromtimestamp(item['created_at']),
                                "updated_at": datetime.fromtimestamp(item['updated_at'])
                            }
                            
                            items_data.append(item_info)
                    except Exception as ex:
                        self.logger.warning(f'Got an error while processing of {item_name}')
                return items_data
            else:
                self.logger.warning(f'Got a problem with fetching {item_name}')

        return None
        
    async def fetch_main_data(self) -> None:
        async with aiohttp.ClientSession() as session:
            ind = 0
            for item_id, item_name in self.items:
                item_data = await self.get_item_data(item_id=item_id, item_name=item_name, session=session)
                if item_data:
                    self.notifier.notify(item_data)
                ind += 1
                self.logger.info(f'[PROCESSED] ID {item_id} NAME {item_name} ({ind/len(self.items):.2f}%)')
                