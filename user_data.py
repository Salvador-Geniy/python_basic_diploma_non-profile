from dataclasses import dataclass
from typing import Dict, List, Union, Any, Optional
from telebot import types
import re
import json
import os
from botrequests import main_request, history


@dataclass
class DataUser:
    """Класс DataUser. Для хранения данных пользователя"""
    user_id: int = None
    city_list: dict = None
    city_id: str = None
    city_name: str = None
    night_value: int = None
    hotels_value: int = None
    needed_photo: bool = False
    photos_value: int = None
    flag_additional_questions: bool = False
    price_range: list = None
    dist_range: list = None
    sorted_func: str = None
    history: dict = None
    lang: str = 'ru_RU'
    cur: str = 'USD'


def write_data(user_id: int, key: str, value: Union[int, str, List[Union[int, float]], None, Dict[str, Union[str, List[str]]]]) -> None:
    """Запись данных пользователя в БД
    params:
    user_id: user id,
    key: ключ,
    value: значение
    """
    i_data = read_data(user_id)
    with open(os.path.join('database', f'{user_id}.json'), 'w') as file:
        i_data[key] = value
        json.dump(i_data, file, indent=4)


def read_data(user_id: int) -> Dict[str, Dict[Any, Any]]:
    """Чтение данных пользователя из БД
    params:
    user_id: user id
    """
    path = os.path.join('database', f'{user_id}.json')
    try:
        with open(path, 'r') as file:
            i_data = json.load(file)
    except FileNotFoundError:
        i_data = {}
        with open(path, 'w') as file:
            json.dump(i_data, file, indent=4)
    return i_data


def set_city(user: Optional[DataUser], city_id: str) -> str:
    """Функция определения названия города"""
    for city_name, city_data in user.city_list.items():
        if city_data == city_id:
            return city_name


def set_price_range(message: types.Message) -> List[int]:
    """Функция установки диапазона цен"""
    pattern = r'[0-9]+'
    price_range = list(map(int, re.findall(pattern, message.text)))
    price_range.sort()
    if len(price_range) == 1:
        price_range.insert(0, 0)
    elif len(price_range) > 2:
        price_range = price_range[:2]

    return price_range


def set_dist_range(message: types.Message) -> List[int]:
    """Функция установки диапазона расстояний"""
    pattern = r'[0-9]+'
    dist_range = list(map(int, re.findall(pattern, message.text)))
    dist_range.sort()
    if len(dist_range) == 1:
        dist_range.insert(0, 0)
    elif len(dist_range) > 2:
        dist_range = dist_range[:2]

    return dist_range


def get_hotels(user: Optional[DataUser]) -> Union[Dict[str, Any], None]:
    """Получение списка отелей
    params:
    user: user
    """
    hotels_data = main_request.hotels_search(user=user, sorted_func=user.sorted_func)
    key, value = history.get_history(hotels_data=hotels_data, user=user)
    write_data(user_id=user.user_id, key=key, value=value)

    return hotels_data or None



def get_address(i_data: Dict[str, Any]) -> str:
    """
    Геттер для получения адреса отеля
    params:
    i_data: данные отеля
    """
    return ', '.join(list(filter(lambda x: isinstance(x, str) and len(x) > 2, list(i_data['address'].values()))))


def get_photos(user: Optional[DataUser], hotel_id: int) -> Union[List[str], None]:
    """Геттер для получения фото отеля
    params:
    user_id: user id
    hotel_id: hotel id
    """
    count_photo = user.photos_value
    photos = main_request.photos_search(count_photo, hotel_id)
    result = []
    for i_photo in photos:
        url_photo = i_photo['baseUrl'].replace('{size}', 'w')
        result.append(url_photo)

    return result or None



def get_landmarks(i_data: Dict[str, Any]) -> str:
    """
    Геттер для получения ориентиров и расстояния до отеля
    :params:
    i_data: данные отеля
    """
    return ', '.join(['\n{label}: {distance}'.format(label=info['label'], distance=info['distance'])
                      for info in i_data['landmarks']])


def count_total_price(user: Optional[DataUser], price: str) -> str:
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


def get_answer(i_data: Dict[str, Any], user: Optional[DataUser]) -> str:
    """Функция формирования ответа на запрос пользователя
    params:
    i_data: список отелей
    user: user
    """
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
        link=f'https://hotels.com/ho{i_data["id"]}'
    )
    return answer