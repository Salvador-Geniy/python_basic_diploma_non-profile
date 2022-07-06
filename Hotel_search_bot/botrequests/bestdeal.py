import requests
import json
import re
from typing import Dict, List, Any


def get_querystring(user_city_id: str, hotels_value: int, today: str, lang: str, cur: str, price_range: List[int]):
    """Функция для получения querystring
    params:
    user_city_id: id города
    hotels_value: кол-во отелей
    today: актуальная дата
    lang: язык
    cur: валюта
    price_range: ценовой диапазон.
    """
    my_query = {"destinationId": user_city_id, "pageNumber": "1", "pageSize": str(hotels_value),
                   "checkIn": today, "checkOut": today, "adults1": "1",
                   "locale": lang, "currency": cur, "sortOrder": "DISTANCE_FROM_LANDMARK",
                   'priceMin': min(price_range), 'priceMax': max(price_range)}
    return my_query


def get_url(user_city_id: str, today: str, price_range: List[int], sort_order: str) -> str:
    """Функция для получения url
    params:
    user_city_id: id города
    today: актуальная дата
    price_range: ценовой диапазон
    sort_order: порядок сортировки
    """
    my_url = (f'https://hotels.com/search.do?destination-id={user_city_id}&q-check-in={today}&q-check-out={today}'
          f'&q-rooms=1&q-room-0-adults=2&q-room-0-children=0&f-price-min={min(price_range)}'
          f'&f-price-max={max(price_range)}&f-price-multiplier=1&sort-order={sort_order}')
    return my_url


def get_hotels_dict(hotels_list: List[Any]) -> Dict[str, Dict[str, int]]:
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
        rate_plan = hotel.get('ratePlan', None)
        if rate_plan is not None:
            price = hotel['ratePlan']['price'].get('current')
        else:
            price = '-'
        coordinate = '+'.join(map(str, hotel['coordinate'].values()))
        hotels_dict[name] = {'id': id, 'name': name, 'address': address, 'landmarks': landmarks, 'price': price, 'coordinate': coordinate}
    return hotels_dict


def bestdeal(user_city_id: str, lang: str, cur: str, hotels_value: int, hotel_url: str, headers: Dict[str, str],
             today: str, price_range: List[int], dist_range: List[int]):
    """Функция поиска лучших отелей(ближе к центру города и низкой ценой)
    params:
    user_city_id: id города
    lang: язык
    cur: валюта
    hotels_value: кол-во отелей для поиска
    hotel_url: ссылка на отель
    headers: headers
    today: актуальная дата
    price_range: диапазон цен
    dist_range: диапазон расстояний
    """
    querystring = get_querystring(user_city_id, hotels_value, today, lang, cur, price_range)

    url = get_url(user_city_id, today, price_range, querystring["sortOrder"])

    hotels_list = []
    pattern = r'\d[,.]?\d'
    while len(hotels_list) < hotels_value:
        try:
            response = requests.get(hotel_url, headers=headers, params=querystring, timeout=20)
            data = json.loads(response.text)
            result = data['data']['body']['searchResults']['results']
            if not result:
                return None, None
            for i_hotel in result:
                distance = re.findall(pattern, i_hotel['landmarks'][0]['distance'])[0].replace(',', '.')
                if float(distance) > max(dist_range):
                    raise ValueError('Превышено максимальное расстояние от центра города.')
                elif min(dist_range) <= float(distance) <= max(dist_range):
                    hotels_list.append(i_hotel)

            querystring['pageNumber'] = str(int(querystring.get('pageNumber')) + 1)

        except ValueError:
            break

    hotels_dict = get_hotels_dict(hotels_list)

    return hotels_dict, url