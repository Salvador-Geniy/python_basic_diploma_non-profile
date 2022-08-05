import re
import requests
import json
from typing import Dict, Optional, List
import datetime
from telebot import types
from database.func_data import *
import commands


city_url = 'https://hotels4.p.rapidapi.com/locations/search'
hotel_url = 'https://hotels4.p.rapidapi.com/properties/list'
photo_url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'


headers = {
    'x-rapidapi-host': 'hotels4.p.rapidapi.com',
    'x-rapidapi-key': "abc44378b1msh3fa9fc2dad36980p1307b2jsn57be16cb77e4"
}


def city_request(message: types.Message):
    """Выполнение HTTP-запроса - поиск городов
    params:
    message: ссобщение пользователя
    :param message:
    """
    querystring = {"query": message.text, "locale": 'en_EN'}
    response = requests.get(city_url, headers=headers, params=querystring, timeout=10)
    data = json.loads(response.text)
    city_data = data['suggestions'][0]['entities']
    return city_data


def check_city(message: types.Message) -> Dict[str, str]:
    """Функция формирования списка городов"""
    city_data = city_request(message)
    pattern = '(\\w+)[\n<]'
    city_dict = {', '.join((city['name'], re.findall(pattern, city['caption']+'\n')[-1])): city['destinationId']
                 for city in city_data}

    return city_dict


def hotels_search(user: Optional['DataUser'], sorted_func: str) -> Dict[str, Optional[Hotel]]:
    """Выполнение HTTP-запроса - поиск отелей
    params:
    user: данные пользователя
    sorted_func: функция для запроса
    """
    today = datetime.date.today()
    my_query = QueryString(destinationId=user.city_id, pageSize=user.hotels_value,
                           locale=user.lang, currency=user.cur, checkIn=str(today),
                           checkOut=str(today))
    if sorted_func == 'bestdeal':
        my_query.sortOrder = "DISTANCE_FROM_LANDMARK"
        my_query.priceMin = min(user.price_range)
        my_query.priceMax = max(user.price_range)
        hotels_list = commands.bestdeal_com.best(my_query, user, hotel_url, headers)
    else:
        if sorted_func == 'lowprice':
            my_query.sortOrder = "PRICE"
            hotels_list = commands.lowprice_com.lowprice(my_query=my_query, hotel_url=hotel_url, headers=headers)

        elif sorted_func == 'highprice':
            my_query.sortOrder = "PRICE_HIGHEST_FIRST"
            hotels_list = commands.highprice_com.highprice(my_query=my_query, hotel_url=hotel_url, headers=headers)

    hotels_dict = get_hotels_dict(hotels_list)
    return hotels_dict


def get_hotels_dict(hotels_list) -> Dict[str, Optional[Hotel]]:
    """Функция для получения hotels_dict
    params:
    hotels_list: список отелей
    """
    hotels_dict = {}
    for hotel in hotels_list:
        name = hotel['name']
        id = hotel['id']
        address = hotel['address']
        landmarks = hotel['landmarks']
        price = hotel.get('ratePlan', {}).get('price', {}).get('current', '-')
        coordinate = '+'.join(map(str, hotel['coordinate'].values()))

        hotels_dict[name] = Hotel(id=id, name=name, address=address, landmarks=landmarks,
                                  price=price, coordinate=coordinate)

    return hotels_dict or None


def photos_search(count_photo: int, hotel_id: int) -> List[str]:
    """Выполнение HTTP-запроса - поиск фото
    params:
    data: данные пользователя
    hotel_id: hotel id
    """
    querystring = {'id': '{}'.format(hotel_id)}
    response = requests.get(photo_url, headers=headers, params=querystring, timeout=10)
    photo_data = json.loads(response.text)
    photos_address = photo_data['hotelImages'][:count_photo]

    return photos_address