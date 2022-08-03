from database.user_data import read_data
from typing import Dict, List, Tuple, Union
import datetime
from commands.command import user


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


def history_com(user_id: int) -> str:
    """Функция подготовки сообщения истории запросов пользователя.
    params:
    user_id: user id
    """
    history = ''
    hist_file = read_data(user_id)
    for date, info in hist_file.items():
        hotels = ''
        for i_hotel in info['Hotels']:
            hotels += f'{i_hotel}\n'
        history += (f"{user.get_ans('request_date')}: {date}"
                    f"\n{user.get_ans('command_name')}: {info['Command'].title()}"
                    f"\n{user.get_ans('hotels_options')}:\n{hotels}")
    if history == '':
        return f"{user.get_ans('empty_history')}."

    return history