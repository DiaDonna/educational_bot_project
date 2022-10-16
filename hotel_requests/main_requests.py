import requests
import json
import re

from googletrans import Translator
from typing import Dict, List, Tuple


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


def location_search(country: str) -> Dict[str, int] | None:
    """
    Функция для выполнения API запроса на поиск приближенных локаций (по названию или территориально) к названию города

    :param country: название города для запроса по поиску приближенных локаций

    :return: Словарь с вариантами локаций, где ключ - это русифицированное название локации, а значение - его ID
             ИЛИ None, если по заданному названию не найдено ничего приближенного

    """

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


def hotels_search(destination_id: int, hotels_qnt: int, check_in: str, check_out: str, sort_order: str) \
        -> Dict[int, str]:
    """
    Функция для выполнения API запроса на поиск отелей по параметру сортировки цены (либо от дешевого к дорогому
    либо наоборот) в заданной локации

    :param destination_id: ID локации, где выполняется поиск отелей;
    :param hotels_qnt: количество отелей, которое необходимо вывести в подборке;
    :param check_in: дата заезда;
    :param check_out: дата выезда;
    :param sort_order: название ключа сортировки.

    :return: Словарь с вариантами отелей, где ключ - это ID отеля, а значение - описание отеля (название, адрес, звезды,
             рейтинг, цена за ночь, объекты инфраструктуры рядом)

    """

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
                           price_min: int, price_max: int, max_distance: int) -> Dict[int, str]:
    """
    Функция для выполнения API запроса на поиск отелей по параметру удаленности от центра и вхождению в указанный
    диапазон цены за ночь в заданной локации

    :param destination_id: ID локации, где выполняется поиск отелей;
    :param hotels_qnt: количество отелей, которое необходимо вывести в подборке;
    :param check_in: дата заезда;
    :param check_out: дата выезда;
    :param sort_order: название ключа сортировки;
    :param price_min: цена минимум за ночь;
    :param price_max: цена максимум за ночь;
    :param max_distance: максимальное расстояние от центра города.

    :return: Словарь с вариантами отелей, где ключ - это ID отеля, а значение - описание отеля (название, адрес, звезды,
             рейтинг, цена за ночь, объекты инфраструктуры рядом)

    """

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


def photos_search(hotel_id: int, photos_qnt: int) -> List[str]:
    """
    Функция для выполнения API запроса на поиск фото отелей

    :param hotel_id: ID отеля;
    :param photos_qnt: количество фото по отелю.

    :return: Список url-ссылок на фото в том количестве, которое указано

    """

    querystring = {"id": hotel_id}
    response = requests.request("GET", photo_url, headers=headers, params=querystring)
    data = json.loads(response.text)

    count = 0
    photos_url_list = []
    while count < photos_qnt:
        if count == 0:
            # тут берется одно фото номеров отеля
            cur_photo_url = data['roomImages'][0]['images'][0]['baseUrl'].replace('{size}', 'w')
            photos_url_list.append(cur_photo_url)
        else:
            # остальное количество добирается из фото самого отеля
            cur_photo_url = data['hotelImages'][count]['baseUrl'].replace('{size}', 'w')
            photos_url_list.append(cur_photo_url)
        count += 1

    return photos_url_list


def coordinates_search(hotel_id: int, check_in: str, check_out: str) -> Tuple[float, float]:
    """
    Функция для выполнения API запроса на поиск координат отеля для последующего вывода геолокации

    :param hotel_id: ID отеля;
    :param check_in: дата заезда;
    :param check_out: дата выезда.

    :return: Координаты (долгота и широта)

    """

    querystring = {"id": hotel_id, "checkIn": check_in, "checkOut": check_out, "adults1": "1", "currency": "RUB",
                   "locale": "ru_RU"}
    response = requests.request("GET", details_url, headers=headers, params=querystring)
    data = json.loads(response.text)

    longitude: float = data['data']['body']['pdpHeader']['hotelLocation']['coordinates']['longitude']
    latitude: float = data['data']['body']['pdpHeader']['hotelLocation']['coordinates']['latitude']

    return longitude, latitude
