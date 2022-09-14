import json
import requests
import re

from googletrans import Translator

city_url = "https://hotels4.p.rapidapi.com/locations/v2/search"
headers = {
    "X-RapidAPI-Key": "b5d40d9d17mshccf3e96f4a95378p1fe11cjsn8c7187ecc997",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

translator = Translator()


def location_search(country: str):
    querystring = {"query": country, "locale": "en_US", "currency": "USD"}
    response = requests.request("GET", city_url, headers=headers, params=querystring)
    data = json.loads(response.text)

    variants_dict = dict()
    try:
        for item in data['suggestions'][0]['entities']:
            address = re.sub(r'(<(/?[^>]+)>)', '', item['caption'])
            variants_dict[translator.translate(address, dest='ru').text] = item['destinationId']

        if len(variants_dict) == 0:
            return None
        return variants_dict

    except TypeError:
        pass
