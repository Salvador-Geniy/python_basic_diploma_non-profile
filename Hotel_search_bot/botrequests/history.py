from typing import Dict, List, Tuple, Union
import datetime


def get_history(hotels_data: Union[Tuple[Union[Dict[str, Dict[str, Union[str, None]]], None], Union[str, None]]],
                user_data: Dict[str, Union[int, str, None, List[Union[int, float]], Dict[str, Union[str, List[str]]]]]):
    """Функция записи истории поиска
    params:
    hotels_data: данные по отелю
    user_data: данные пользователя
    """
    result, hotel_url = hotels_data
    cur_time = datetime.datetime.now().strftime('%d %b %Y %H:%M:%S')
    my_list = []
    for i_hotel, i_data in result.items():
        my_list.append('<a href="{url}">{name}</a>'.format(
            url='https://hotels.com/ho' + str(i_data['id']), name=i_hotel))
    my_dict = {}

    my_dict['Command'] = user_data['sorted_func']
    my_dict['Hotels'] = my_list

    key = cur_time
    value = my_dict

    return key, value