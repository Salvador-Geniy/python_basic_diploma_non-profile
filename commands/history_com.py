from user_data import read_data


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
        history += f"Дата запроса: {date}\nКомманда: {info['Command']}\nВарианты отелей:\n{hotels}"
    if history == '':
        return 'История запросов пуста.'

    return history