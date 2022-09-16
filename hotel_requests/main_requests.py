import json
import requests
import re

from googletrans import Translator


# для параметра headers в запросе
headers = {
    "X-RapidAPI-Key": "b5d40d9d17mshccf3e96f4a95378p1fe11cjsn8c7187ecc997",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

city_url = "https://hotels4.p.rapidapi.com/locations/v2/search"  # для поиска локаций
hotels_url = "https://hotels4.p.rapidapi.com/properties/list"  # для поиска отелей
photo_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"  # для поиска фото

# объект класса Translator из библиотеки googletrans для всех действий, касающихся перевода
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


def hotels_search(destination_id: int, hotels_qnt: int, check_in: str, check_out: str, sort_order: str):
    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": hotels_qnt, "checkIn": check_in,
                   "checkOut": check_out, "adults1": "1", "sortOrder": sort_order, "locale": "ru_RU", "currency": "RUB"}
    response = requests.request("GET", hotels_url, headers=headers, params=querystring)
    data = json.loads(response.text)

    hotels_dict = dict()
    for info in data['data']['body']['searchResults']['results']:

        nearby = ''
        for i_dict in info['landmarks']:
            nearby += f"{i_dict['label']} - {i_dict['distance']}, "

        hotels_dict[info['id']] = f'\N{hotel} {info["name"]} ' \
                                  f'\nАдрес: {info["address"]["streetAddress"]}' \
                                  f'\n\N{glowing star} {str(info["starRating"])}' \
                                  f'\nРейтинг: {str(info["guestReviews"]["rating"])}' \
                                  f'\nЦена за ночь: {str(info["ratePlan"]["price"]["current"])}' \
                                  f'\nРядом: {nearby[:-2]}\n'

    return hotels_dict


def photos_search(hotel_id: int, photos_qnt: int):
    querystring = {"id": hotel_id}
    response = requests.request("GET", photo_url, headers=headers, params=querystring)
    data = json.loads(response.text)

    count = 0
    photos_url_list = []
    while count < photos_qnt:
        if count == 0:
            cur_photo_url = data['roomImages'][0]['images'][0]['baseUrl'].replace('{size}', 'y')
            photos_url_list.append(cur_photo_url)
        else:
            cur_photo_url = data['hotelImages'][count]['baseUrl'].replace('{size}', 'y')
            photos_url_list.append(cur_photo_url)
        count += 1

    return photos_url_list
