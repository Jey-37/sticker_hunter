import asyncio
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup


class BotNotifier():
    def __init__(self, bot, users: list[int]):
        self.bot = bot
        self.users = users

        self.items_pars_time = {}

    def notify(self, data: list[dict]) -> None:
        loop = asyncio.get_event_loop()
        loop.create_task(self.filter_and_send(data))

    async def filter_and_send(self, data: list[dict]):
        for asset in data:
            if self.check_asset(asset):
                #print(f"Timestamps: {asset['created_at']} {asset['updated_at']}")
                for user_id in self.users:
                    message_text = self.build_message_text(asset)
                    message_markup = self.build_message_markup(asset)
                    await self.bot.send_photo(
                        chat_id=user_id,
                        photo=asset['img_src'],
                        caption=message_text,
                        reply_markup=message_markup)

        self.items_pars_time[data[0]['id']] = datetime.now()

    def check_asset(self, asset: dict) -> bool:
        if asset['id'] in self.items_pars_time and asset['updated_at'] < self.items_pars_time[asset['id']]:
            return False
        
        if asset['sp'] > 5:
            return False
        if asset['price'] < 3 or asset['price'] > 1000:
            return False
        if asset['sticker_price']/asset['price'] < 0.3:
            return False

        has_katowice = False
        for sticker in asset['stickers']:
            if 'katowice 2014' in sticker['name'].lower():
                has_katowice = True
                break
        if has_katowice and asset['sp'] > 1:
            return False

        return True

    def build_message_text(self, asset: dict) -> str:
        stickers_text = "\n".join(
            [BotNotifier.STICKER_TEXT_TEMPLATE.format(**sticker) for sticker in asset['stickers']])

        created = self.build_time_string(datetime.now()-asset['created_at'])
        updated = self.build_time_string(datetime.now()-asset['updated_at'])

        return BotNotifier.MESSAGE_TEXT_TEMPLATE.format(
            stickers_text=stickers_text,
            created=created,
            updated=updated,
            **asset)

    def build_message_markup(self, asset: dict) -> ReplyKeyboardMarkup:
        buy_link = BotNotifier.BUY_LINK_TEMPLATE.format(
            item_id=asset['id'], 
            sell_order_id=asset['sell_order_id'],
            **asset['asset_info'])

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='🟢 BUY 🟢', url=buy_link))

        return builder.as_markup()

    def build_time_string(self, dt) -> str:
        if dt.days // 7 >= 2:
            return f"> {dt.days // 7} weeks";
        if dt.days > 0:
            return f"> {dt.days} days";

        time_parts = []
        sec = dt.seconds
        if sec >= 3600:
            time_parts.append(f"{sec // 3600} h")
            sec %= 3600

        if sec >= 60:
            time_parts.append(f"{sec // 60} m")
            sec %= 60

        if sec > 0:
            time_parts.append(f"{sec} s")

        return " ".join(time_parts)


    MESSAGE_TEXT_TEMPLATE = '''<b>{name}</b>
<em>{float}</em>

Price: {price}¥
Min Price: {min_price}¥
Sticker Price: {sticker_price}¥ ({sp}%)

Stickers:
{stickers_text}

{created}  |  {updated}
'''

    STICKER_TEXT_TEMPLATE = "{name} - {price}¥ ({wear}%)"

    BUY_LINK_TEMPLATE = "https://buff.163.com/goods/{item_id}?appid=730&classid={classid}&instanceid={instanceid}&assetid={assetid}&contextid={contextid}&sell_order_id={sell_order_id}"
