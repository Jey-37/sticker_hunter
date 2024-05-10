import json


with open('data\\buffids.json', 'r') as file:
    items = json.load(file)

stickers = {}
for title, id in items.items():
    if title.startswith("Sticker"):
        stickers[title[10:]] = { 'id' : id }

with open('data\\stickers.json', 'w') as file:
    json.dump(stickers, file)
