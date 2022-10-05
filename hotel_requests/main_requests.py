import json
import requests
import re

from googletrans import Translator


# для параметра headers в запросе
headers = {
    "X-RapidAPI-Key": "088b8231c2msh7843f1ca13e9994p18788ajsnb33bd8a9d1d0",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

city_url = "https://hotels4.p.rapidapi.com/locations/v2/search"  # для поиска локаций
hotels_url = "https://hotels4.p.rapidapi.com/properties/list"  # для поиска отелей
photo_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"  # для поиска фото
details_url = "https://hotels4.p.rapidapi.com/properties/get-details"   # для уточнения координат отеля на карте

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


def hotels_search_bestdeal(destination_id: int, hotels_qnt: int, check_in: str, check_out: str, sort_order: str,
                           price_min: int, price_max: int, max_distance: int):

    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": "25", "checkIn": check_in,
                   "checkOut": check_out, "adults1": "1", "priceMin": price_min, "priceMax": price_max,
                   "sortOrder": sort_order, "locale": "ru_RU", "currency": "RUB"}
    response = requests.request("GET", hotels_url, headers=headers, params=querystring)
    data = json.loads(response.text)

    hotels_dict = dict()
    for info in data['data']['body']['searchResults']['results']:

        # Если количество вариантов в словаре на данный момент уже равно кол-ву отелей, которое хотел пользователь, то
        # прерываем цикл и возвращаем словарь с подходящими вариантами
        if len(hotels_dict) < int(hotels_qnt):

            # Если расстояние от центра города больше, чем хочет пользователь, то возвращаем словарь с вариантами,
            # которые есть на данный момент (даже если он пустой)
            if float(info['landmarks'][0]['distance'][:-3].replace(',', '.')) > max_distance:
                break

            # Иначе если с расстоянием все в норме, то проверяем вхождение в диапазон цен.
            # Если проходим, то заносим вариант в словарь
            elif price_min <= float(info["ratePlan"]["price"]["current"][:-4].replace(',', '')) <= price_max:

                hotels_dict[info['id']] = f'\N{hotel} {info["name"]} ' \
                                          f'\nАдрес: {info["address"]["streetAddress"]}' \
                                          f'\n\N{glowing star} {str(info["starRating"])}' \
                                          f'\nРейтинг: {str(info["guestReviews"]["rating"])}' \
                                          f'\nЦена за ночь: {str(info["ratePlan"]["price"]["current"])}' \
                                          f'\nРасстояние от центра города: {str(info["landmarks"][0]["distance"])}\n'

    return hotels_dict


def photos_search(hotel_id: int, photos_qnt: int):
    querystring = {"id": hotel_id}
    response = requests.request("GET", photo_url, headers=headers, params=querystring)
    data = json.loads(response.text)

    count = 0
    photos_url_list = []
    while count < photos_qnt:
        if count == 0:
            cur_photo_url = data['roomImages'][0]['images'][0]['baseUrl'].replace('{size}', 'w')
            photos_url_list.append(cur_photo_url)
        else:
            cur_photo_url = data['hotelImages'][count]['baseUrl'].replace('{size}', 'w')
            photos_url_list.append(cur_photo_url)
        count += 1

    return photos_url_list


def coordinates_search(hotel_id: int, check_in: str, check_out: str):
    querystring = {"id": hotel_id, "checkIn": check_in, "checkOut": check_out, "adults1": "1", "currency": "RUB",
                   "locale": "ru_RU"}
    response = requests.request("GET", details_url, headers=headers, params=querystring)
    data = json.loads(response.text)

    longitude: float = data['data']['body']['pdpHeader']['hotelLocation']['coordinates']['longitude']
    latitude: float = data['data']['body']['pdpHeader']['hotelLocation']['coordinates']['latitude']

    return longitude, latitude
