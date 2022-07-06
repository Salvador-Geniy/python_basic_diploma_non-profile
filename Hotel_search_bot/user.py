from dataclasses import dataclass, asdict
from typing import Dict, List, Union, Any
import re
import json
import os
from botrequests import main_request, lowprice, highprice, bestdeal, history


@dataclass
class Data:
    """Дата-класс"""
    user_id: int = None
    city_list: dict = None
    city_id: str = None
    city_name: str = None
    night_value: int = None
    hotel_value: int = None
    needed_photo: bool = False
    photos_value: int = None
    flag_additional_questions: bool = False
    price_range: list = None
    dist_range: list = None
    sorted_func: str = None
    history: dict = None
    lang: str = 'en_EN'
    cur: str = 'USD'
    sorted_functions = {
        'bestdeal': bestdeal.bestdeal,
        'lowprice': lowprice.lowprice,
        'highprice': highprice.highprice
    }

# class Data:
#
#     sorted_functions = {
#         'bestdeal': bestdeal.bestdeal,
#         'lowprice': lowprice.lowprice,
#         'highprice': highprice.highprice
#     }
#
#     def __init__(self):
#         self.user_id = None
#         self.city_list = []
#         self.city_id = None
#         self.city_name = None
#         self.night_value = None
#         self.hotel_value = None
#         self.needed_photo = False
#         self.photos_value = None
#         self.flag_additional_questions = False
#         self.price_range = []
#         self.dist_range = []
#         self.sorted_func = None
#         self.history = dict()
#         self.lang = 'en_EN'
#         self.cur = 'USD'


def set_city(user, city_id: str) -> str:
    for city_name, city_data in user.city_list.items():
        if city_data == city_id:
            return city_name


def set_price_range(message):
    pattern = r'[0-9]+'
    price_range = list(map(int, re.findall(pattern, message.text)))
    price_range.sort()
    if len(price_range) == 1:
        price_range.insert(0, 0)
    elif len(price_range) > 2:
        price_range = price_range[:2]

    return price_range


def set_dist_range(message):
    pattern = r'[0-9]+'
    dist_range = list(map(int, re.findall(pattern, message.text)))
    dist_range.sort()
    if len(dist_range) == 1:
        dist_range.insert(0, 0)
    elif len(dist_range) > 2:
        dist_range = dist_range[:2]

    return dist_range


def get_hotels(user) -> Any:
    """Получение списка отелей
    params:
    user: user
    """
    sorted_func = user.sorted_functions[user.sorted_func]
    hotels_data = main_request.hotels_search(user=user, sorted_func=sorted_func)
    key, value = history.get_history(hotels_data=hotels_data, user=user)
    user.history[key] = value
    if hotels_data:
        return hotels_data
    return None, None


def get_address(i_data: Dict[str, Any]) -> str:
    """
    Геттер для получения адреса отеля
    params:
    i_data: данные отеля
    """
    return ', '.join(list(filter(lambda x: isinstance(x, str) and len(x) > 2, list(i_data['address'].values()))))


def get_photos(user, hotel_id: int) -> Union[List[str], None]:
    """Геттер для получения фото отеля
    params:
    user_id: user id
    hotel_id: hotel id
    """
    count_photo = user.photos.value
    photos = main_request.photos_search(count_photo, hotel_id)
    result = []
    for i_photo in photos:
        url_photo = i_photo['baseUrl'].replace('{size}', 'w')
        result.append(url_photo)
    if result:
        return result
    return None


def get_landmarks(i_data: Dict[str, Any]) -> str:
    """
    Геттер для получения обработанных ориентиров варианта размещения (отеля).
    :param i_data: данные варианта размещения (отеля)
    :return: ориентиры варианта размещения (отеля)
    """
    return ', '.join(['\n{label}: {distance}'.format(label=info['label'], distance=info['distance'])
                      for info in i_data['landmarks']])


def count_total_price(user, price: str) -> str:
    """Рассчёт итоговой стоимости номера в отеле
    params:
    chat_id: chat id
    price: стоимость номера за ночь
    """
    nights = user.night_value
    pattern = r'[0-9]+'
    daily_price = int(re.search(pattern, price).group())
    result = nights * daily_price
    return str(result)


def get_answer(i_data, user):
    answer = ('\nОтель: {name}'
              '\nАдрес: {address}'
              '\nРасстояние до: {distance}'
              '\nЦена за сутки: {price}'
              '\nЦена за {nights} ночей: ${total_price}'
              '\nПосмотеть на Google maps: {address_link}'
              '\nПодробнее по ссылке: {link}\n').format(
        name=i_data['name'],
        address_link='https://www.google.ru/maps/place/{id}'.format(id=i_data['coordinate']),
        address=get_address(i_data),
        distance=get_landmarks(i_data),
        price=i_data['price'],
        nights=user.night_value,
        total_price=count_total_price(user, i_data['price']),
        link='https://hotels.com/ho{id}'.format(id=str(i_data['id']))
    )
    return answer


def write_test(user):
    data = asdict(user)
    file_name = f'{user.user_id}test.json'
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)