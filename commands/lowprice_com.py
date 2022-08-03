import requests
import json
from dataclasses import asdict
from typing import Dict, List, Any, Union, Optional


def lowprice(my_query: Optional['QueryString'], hotel_url: str, headers: Dict[str, str]) -> Union[List[Any], None]:
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