import requests
import json
import re
from dataclasses import asdict
from typing import Dict, List, Any, Union, Optional


def best(my_query: Optional['QueryString'], user: Optional['DataUser'], hotel_url: str, headers: Dict[str, str]) -> Union[List[Any], None]:
    """Функция поиска лучших отелей по соотношению цена-расстояние до центра
    params:
    my_query: querystring
    user: user
    hotel_url: hotel url
    headers: headers
    """
    hotels_list = []
    pattern = r'\d[,.]?\d'
    querystring = asdict(my_query)
    while len(hotels_list) < user.hotels_value:
        try:
            response = requests.get(hotel_url, headers=headers, params=querystring, timeout=20)
            data = json.loads(response.text)
            result = data['data']['body']['searchResults']['results']
            if not result:
                return None
            for i_hotel in result:
                distance = re.findall(pattern, i_hotel['landmarks'][0]['distance'])[0].replace(',', '.')
                if float(distance) > max(user.dist_range):
                    raise ValueError('Превышено максимальное расстояние от центра города.')
                elif min(user.dist_range) <= float(distance) <= max(user.dist_range):
                    hotels_list.append(i_hotel)

            querystring['pageNumber'] = str(int(querystring.get('pageNumber')) + 1)

        except ValueError:
            break
    return hotels_list


def price(my_query: Optional['QueryString'], hotel_url: str, headers: Dict[str, str]) -> Union[List[Any], None]:
    """Функция для поиска отелей с лучшей ценой (дешёвых/дорогих)
    params:
    my_query: querystring
    hotel_url: hotel url
    headers: headers
    """
    querystring = asdict(my_query)
    response = requests.get(hotel_url, headers=headers, params=querystring, timeout=20)
    data = json.loads(response.text)
    hotels_list = data['data']['body']['searchResults']['results']

    return hotels_list or None