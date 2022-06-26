"""Модуль user_data. Описывает взаимодействие с базой данных пользователей (json-формат) и модулем botrequests"""

from typing import Dict, List, Union, Any
import re
import json
import os
from botrequests import main_request, lowprice, highprice, bestdeal, history


sorted_functions = {
    'lowprice': lowprice.lowprice,
    'highprice': highprice.highprice,
    'bestdeal': bestdeal.bestdeal
}

data = {
    'city_list': None,
    'city_id': None,
    'city_name': None,
    'night_value': None,
    'hotels_value': None,
    'needed_photo': False,
    'photos_value': None,
    'flag_additional_questions': None,
    'price_range': [],
    'dist_range': [],
    'sorted_func': None,
    'history': dict(),
    'lang': 'en_EN',
    'cur': 'USD'
}


def write_data(user_id: int, key: str, value: Union[int, str, List[Union[int, float]], None, Dict[str, Union[str, List[str]]]]) -> None:
    """Запись данных пользователя в БД
    params:
    user_id: user id,
    key: ключ,
    value: значение
    """
    i_data = read_data(user_id)
    with open(os.path.join('database', str(user_id) + '.json'), 'w') as file:
        i_data[key] = value
        json.dump(i_data, file, indent=4)


def read_data(user_id: int):
    """Чтение данных пользователя из БД
    params:
    user_id: user id
    """
    try:
        with open(os.path.join('database', str(user_id) + '.json'), 'r') as file:
            i_data = json.load(file)
    except FileNotFoundError:
        i_data = data
        with open(os.path.join('database', str(user_id) + '.json'), 'w') as file:
            json.dump(i_data, file, indent=4)
    return i_data


def get_flag_additional_questions(chat_id: int) -> Union[bool, None]:
    """Геттер для получения значения флага доп. вопросов
    params:
    chat_id: chat id
    """
    return read_data(user_id=chat_id)['flag_additional_questions']


def get_city_list(message) -> Dict[str, str]:
    """Получение списка городов
    params:
    message: message
    """
    city_dict = main_request.check_city(message)
    write_data(user_id=message.chat.id, key='city_list', value=city_dict)
    return city_dict


def get_hotels(user_id: int) -> Any:
    """Получение списка отелей
    params:
    user_id: user id
    """
    i_data = read_data(user_id=user_id)
    sorted_func = sorted_functions[i_data['sorted_func']]
    hotels_data = main_request.hotels_search(data=i_data, sorted_func=sorted_func)
    key, value = history.get_history(hotels_data=hotels_data, user_data=i_data)
    i_history = read_data(user_id=user_id)['history']
    i_history[key] = value
    write_data(user_id=user_id, key='history', value=i_history)
    if hotels_data:
        return hotels_data
    return None, None


def get_get_photos(user_id: int, hotel_id: int) -> Union[List[str], None]:
    """Геттер для получения фото отеля
    params:
    user_id: user id
    hotel_id: hotel id
    """
    i_data = read_data(user_id)
    photos = main_request.photos_search(i_data, hotel_id)
    result = []
    for i_photo in photos:
        url_photo = i_photo['baseUrl'].replace('{size}', 'w')
        result.append(url_photo)
    if result:
        return result
    return None


def get_needed_photo(chat_id: int) -> Union[bool, None]:
    """Геттер для получения значения флага необходмиости вывода фотографий отеля
    params:
    chat_id: chat id
    """
    return read_data(user_id=chat_id)['needed_photo']


def set_needed_photo(chat_id: int, value: Union[bool, None]) -> None:
    """Сеттер для установки значения флага необходмиости вывода фотографий отеля
        params:
        chat_id: chat id
        value: значение флага
        """
    write_data(user_id=chat_id, key='needed_photo', value=value)


def set_sorted_func(chat_id: int, func: str) -> None:
    """Сеттер для установки сортирующей функции
    params:
    chat_id: chat id
    func: название функции
    """
    if func == 'bestdeal':
        write_data(user_id=chat_id, key='flag_additional_questions', value=True)
    else:
        write_data(user_id=chat_id, key='flag_additional_questions', value=False)
    write_data(user_id=chat_id, key='sorted_func', value=func)


def get_history(user_id: int) -> Any:
    """Геттер для получения истории поиска
    params:
    user_id: user id
    """
    i_file = os.path.join('database', '{user_id}.json'.format(user_id=user_id))
    with open(i_file, 'r') as file:
        data = json.load(file)
    hist = data['history']
    return hist


def get_address(i_data: Dict[str, Any]) -> str:
    """
    Геттер для получения адреса отеля
    params:
    i_data: данные отеля
    """
    return ', '.join(list(filter(lambda x: isinstance(x, str) and len(x) > 2, list(i_data['address'].values()))))


def get_price_range(chat_id: int) -> List[int]:
    """Геттер для получения диапазона цен отелей
    params:
    chat_id: chat id
    """
    return read_data(user_id=chat_id)['price_range']


def set_price_range(chat_id: int, value: List[int]) -> None:
    """Сеттер для установки диапазона цен отелей
    params:
    chat_id: chat id
    value: ценовой диапазон, заданный пользователем
    """
    write_data(user_id=chat_id, key='price_range', value=value)


def get_dist_range(chat_id: int) -> List[int]:
    """Геттер для получения диапазона расстояний
    params:
    chat_id: chat id
    """
    return read_data(user_id=chat_id)['dist_range']


def set_dist_range(chat_id: int, value: List[int]) -> None:
    """Сеттер для установки диапазона расстояний
    params:
    chat_id: chat id
    value: диапазон расстояний
    """
    write_data(user_id=chat_id, key='dist_range', value=value)


def get_photos_value(chat_id: int) -> Union[int, None]:
    """Геттер для получения кол-ва фото для каждого отеля
    params:
    chat_id: chat id
    """
    return read_data(user_id=chat_id)['photos_value']


def set_photos_value(chat_id:int, value: int) -> None:
    """Сеттер для установки кол-ва фото для каждого отеля
    params:
    chat_id: chat id
    value: количество фото
    """
    if value > 7:
        value = 7
    write_data(user_id=chat_id, key='photos_value', value=value)
    
    
def get_hotels_value(chat_id: int) -> Union[int, None]:
    """Геттер для получения кол-ва отелей
    params:
    chat_id: chat id
    """
    return read_data(user_id=chat_id)['hotels_value']


def set_hotels_value(chat_id: int, value: int) -> None:
    """Сеттер для установки кол-ва отелей
    params:
    chat_id: chat id
    value: количество отелей
    """
    if value > 10:
        value = 10
    write_data(user_id=chat_id, key='hotels_value', value=value)


def get_city_id(chat_id: int) -> str:
    """Геттер для получения id города
    params:
    chat_id: chat id
    """
    return read_data(user_id=chat_id)['city_id']


def set_city(chat_id: int, value: str) -> None:
    """Сеттер для установки id и названия города
    params:
    chat_id: chat id
    value: id города
    """
    write_data(user_id=chat_id, key='city_id', value=value)
    city_list = read_data(user_id=chat_id)['city_list']
    for city_name, city_data in city_list.items():
        if city_data == value:
            write_data(user_id=chat_id, key='city_name', value=city_name)


def get_landmarks(i_data: Dict[str, Any]) -> str:
    """
    Геттер для получения обработанных ориентиров варианта размещения (отеля).
    :param i_data: данные варианта размещения (отеля)
    :return: ориентиры варианта размещения (отеля)
    """
    return ', '.join(['\n{label}: {distance}'.format(label=info['label'], distance=info['distance'])
                      for info in i_data['landmarks']])


def set_night_value(chat_id: int, value: int) -> None:
    """Сеттер для установки кол-ва ночей пребывания
    params:
    chat_id: chat id
    value: кол-во ночей пребывания
    """
    write_data(user_id=chat_id, key='night_value', value=value)


def count_total_price(chat_id: int, price: str) -> str:
    """Рассчёт итоговой стоимости номера в отеле
    params:
    chat_id: chat id
    price: стоимость номера за ночь
    """
    nights = read_data(chat_id)['night_value']
    daily_price = int(re.search(r'[0-9]+', price).group())
    result = nights * daily_price
    return str(result)