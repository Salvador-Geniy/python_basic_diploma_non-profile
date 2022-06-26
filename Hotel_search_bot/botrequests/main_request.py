import re
import requests
import json
from typing import Dict
import datetime
from telebot import types


city_url = 'https://hotels4.p.rapidapi.com/locations/search'
hotel_url = 'https://hotels4.p.rapidapi.com/properties/list'
photo_url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'


headers = {
    'x-rapidapi-host': 'hotels4.p.rapidapi.com',
    'x-rapidapi-key': "abc44378b1msh3fa9fc2dad36980p1307b2jsn57be16cb77e4"
}


def check_city(message: types.Message) -> Dict[str, str]:
    """
    Выполнение HTTP-запроса - поиск городов
    params:
    message: ссобщение пользователя
    """

    querystring = {"query": message.text, "locale": 'en_EN'}
    response = requests.request("GET", city_url, headers=headers, params=querystring, timeout=10)
    data = json.loads(response.text)

    city_dict = {', '.join((city['name'], re.findall('(\\w+)[\n<]', city['caption']+'\n')[-1])): city['destinationId']
                 for city in data['suggestions'][0]['entities']}
    return city_dict


def hotels_search(data, sorted_func):
    """Выполнение HTTP-запроса - поиск отелей
    params:
    data: данные пользователя
    sorted_func: функция для запроса
    """
    if data['sorted_func'] == "bestdeal":
        hotels_data = sorted_func(user_city_id=data['city_id'], lang=data['lang'], cur=data['cur'],
                                  hotels_value=data['hotels_value'], hotel_url=hotel_url, headers=headers,
                                  today=datetime.date.today(), price_range=data['price_range'],
                                  dist_range=data['dist_range'])
    else:
        hotels_data = sorted_func(user_city_id=data['city_id'], lang=data['lang'], cur=data['cur'],
                                  hotels_value=data['hotels_value'], hotel_url=hotel_url, headers=headers,
                                  today=datetime.date.today())
    return hotels_data


def photos_search(data, hotel_id: int):
    """Выполнение HTTP-запроса - поиск фото
    params:
    data: данные пользователя
    hotel_id: hotel id
    """
    querystring = {'id': '{}'.format(hotel_id)}
    response = requests.request('GET', photo_url, headers=headers, params=querystring, timeout=10)
    photo_data = json.loads(response.text)
    photos_address = photo_data['hotelImages'][:data['photos_value']]
    return photos_address