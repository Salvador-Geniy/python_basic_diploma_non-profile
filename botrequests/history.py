from typing import Dict, List, Tuple, Union, Optional
import datetime


def get_history(hotels_data, user) -> Tuple[str, Dict[str, Union[str, List[str]]]]:
    """Функция записи истории поиска
    params:
    hotels_data: данные по отелю
    user: данные пользователя
    """
    result = hotels_data
    cur_time = datetime.datetime.now().strftime('%d %b %Y %H:%M:%S')
    my_list = []
    for i_hotel, i_data in result.items():
        my_list.append('<a href="{url}{id}">{name}</a>'.format(
            url='https://hotels.com/ho', id=str(i_data.id), name=i_hotel))
    my_dict = {}

    my_dict['Command'] = user.sorted_func
    my_dict['Hotels'] = my_list

    key = cur_time
    value = my_dict

    return key, value