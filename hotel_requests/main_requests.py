import json
import requests
import re

from telebot.types import Message

city_url = "https://hotels4.p.rapidapi.com/locations/v2/search"
headers = {
    "X-RapidAPI-Key": "b5d40d9d17mshccf3e96f4a95378p1fe11cjsn8c7187ecc997",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def location_search(message: Message):
    querystring = {"query": message.text, "locale": "en_US", "currency": "USD"}
    response = requests.request("GET", city_url, headers=headers, params=querystring)
    data = json.loads(response.text)

    variants_dict = dict()
    for item in data['suggestions'][0]['entities']:
        address = re.sub(r'(<(/?[^>]+)>)', '', item['caption'])
        variants_dict[address] = item['destinationId']

    return variants_dict
