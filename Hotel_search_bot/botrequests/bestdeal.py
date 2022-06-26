import requests
import json
import re
from typing import Dict, List


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
    today: дата
    price_range: диапазон цен
    dist_range: диапазон расстояний
    """
    querystring = {"destinationId": user_city_id, "pageNumber": "1", "pageSize": str(hotels_value),
                   "checkIn": today, "checkOut": today, "adults1": "1",
                   "locale": "{}".format(lang), "currency": cur, "sortOrder": "DISTANCE_FROM_LANDMARK",
                   'priceMin': min(price_range), 'priceMax': max(price_range)}

    url = f'https://hotels.com/search.do?destination-id={user_city_id}&q-check-in={today}&q-check-out={today}' \
          f'&q-rooms=1&q-room-0-adults=2&q-room-0-children=0&f-price-min={min(price_range)}' \
          f'&f-price-max={max(price_range)}&f-price-multiplier=1&sort-order={querystring["sortOrder"]}'

    hotels_list = []
    while len(hotels_list) < hotels_value:
        try:
            response = requests.request('GET', hotel_url, headers=headers, params=querystring, timeout=20)
            data = json.loads(response.text)
            result = data['data']['body']['searchResults']['results']
            if not result:
                return None, None
            for i_hotel in result:
                distance = re.findall(r'\d[,.]?\d', i_hotel['landmarks'][0]['distance'])[0].replace(',', '.')
                if float(distance) > max(dist_range):
                    raise ValueError('Превышено максимальное расстояние от центра города.')
                elif min(dist_range) <= float(distance) <= max(dist_range):
                    hotels_list.append(i_hotel)

            querystring['pageNumber'] = str(int(querystring.get('pageNumber')) + 1)

        except ValueError:
            break

    hotels_dict = {hotel['name']: {'id': hotel['id'], 'name': hotel['name'], 'address': hotel['address'],
                                   'landmarks': hotel['landmarks'], 'price': hotel['ratePlan']['price'].get(
            'current') if hotel.get('ratePlan', None) else '-', 'coordinate': '+'.join(
            map(str, hotel['coordinate'].values()))}
                   for hotel in hotels_list}

    return hotels_dict, url