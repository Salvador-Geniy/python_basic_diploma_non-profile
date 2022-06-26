import telebot
import re
import config
from telebot import types
import user_data
from typing import Callable, Union
import functools

bot = telebot.TeleBot(config.token)


def exc_handler(method: Callable):
    """Декоратор. Обрабатывает ошибки, перезапускает бот"""
    @functools.wraps(method)
    def wrapper(message: Union[types.Message, types.CallbackQuery]) -> None:
        try:
            method(message)
        except Exception:
            bot.send_message(message.chat.id, 'Что-то пошло не так... Давай сначала?')
            welcome(message)
    return wrapper


@bot.message_handler(regexp=r'.*[Пп]ривет.*')
@bot.message_handler(commands=['start', 'hello_world'])
@exc_handler
def welcome(message):
    """Стартовое сообщение.Выбор команды"""
    user = message.from_user.first_name
    bot.send_message(message.chat.id, 'Привет, <b>{user}</b>. Я могу помочь вам с поиском отеля.\nВыберите команду:'
                                      '\n/bestdeal - отели ближе к центру города, с низкой ценой' \
                                      '\n/lowprice - отели с низкой ценой' \
                                      '\n/highprice - отели с высокой ценой' \
                                      '\n/history - история поиска'.format(user=user), parse_mode='html')


@bot.message_handler(commands=['history'])
@exc_handler
def print_history(message):
    """Вывод истории запросов пользователя"""
    history = user_data.get_history(user_id=message.from_user.id)
    for date, info in history.items():
        ans = '\nДата запроса: {time}' \
              '\nКомманда: {command}' \
              '\nВарианты отелей:'.format(
            time=date,
            command=info['Command'],
        )
        bot.send_message(message.from_user.id, ans)
        for item in info['Hotels']:
            bot.send_message(message.from_user.id, item, parse_mode='HTML', disable_web_page_preview=True)




@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
@exc_handler
def set_func(message):
    """Установка функции, выбраной пользователем"""
    user_data.set_sorted_func(chat_id=message.chat.id, func=re.search(r'\w+', message.text).group())
    bot.send_message(chat_id=message.chat.id, text='Введите название города.')

    
@bot.message_handler(content_types=['text'])
@exc_handler
def choose_city(message):
    """Выбор города"""
    temp = bot.send_message(chat_id=message.chat.id, text='Поиск...')
    result = user_data.get_city_list(message)
    keyboard = types.InlineKeyboardMarkup()
    if not result:
        bot.send_message(chat_id=message.chat.id, text='Город не найден')
        bot.register_next_step_handler(message, choose_city)
    else:
        for city_name, city_id in result.items():
            keyboard.add(types.InlineKeyboardButton(text=city_name, callback_data=city_id))
        bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id, text='Результаты:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'Результаты:' in call.message.text)
@exc_handler
def city_setter(call: types.CallbackQuery) -> None:
    """Установка выбранного города"""
    user_data.set_city(chat_id=call.message.chat.id, value=call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if user_data.get_flag_additional_questions(chat_id=call.message.chat.id):
        choose_price_range(call.message)
    else:
        choose_night_value(call.message)


@exc_handler
def choose_price_range(message: types.Message) -> None:
    """Выбор диапазона цен"""
    bot.send_message(chat_id=message.chat.id, text='Введите ценовой диапзон.(цена за сутки в USD)\nНапример: 1 100; 1-100; 1,100')
    bot.register_next_step_handler(message, choose_dist_range)


@exc_handler
def choose_dist_range(message: types.Message) -> None:
    """Обработка диапазона цен, выбор диапазона расстояний"""
    price_range = list(map(int, re.findall(r'[0-9]+', message.text)))
    price_range.sort()
    if len(price_range) == 1:
        price_range.insert(0, 0)
    elif len(price_range) > 2:
        price_range = price_range[:2]

    user_data.set_price_range(chat_id=message.chat.id, value=price_range)
    bot.send_message(message.chat.id, 'Введите диапазон расстояний от центра города.\nНапример: 1 10; 1-10; 1,10')
    bot.register_next_step_handler(message, choose_night_value)


@exc_handler
def choose_night_value(message: types.Message) -> None:
    """Обработка диапазона расстояний, выбор кол-ва ночей пребывания"""
    dist_range = list(map(int, re.findall(r'[0-9]+', message.text)))
    dist_range.sort()
    if len(dist_range) == 1:
        dist_range.insert(0, 0)
    elif len(dist_range) > 2:
        dist_range = dist_range[:2]
    user_data.set_dist_range(chat_id=message.chat.id, value=dist_range)
    bot.send_message(message.chat.id, 'Введите количество ночей пребывания')
    bot.register_next_step_handler(message, hotel_value)


@exc_handler
def hotel_value(message: types.Message) -> None:
    """Обработка кол-ва ночей пребывания, выбор кол-ва отелей для поиска"""
    nights = int(message.text)
    user_data.set_night_value(chat_id=message.chat.id, value=nights)
    bot.send_message(message.chat.id, 'Введите количество отелей для поиска(макс. 10)')
    bot.register_next_step_handler(message, photo_need)


@exc_handler
def photo_need(message: types.Message) -> None:
    """Обработка кол-ва отелей для поиска, выбор необходимости загрузки фото"""
    hotel_value = int(message.text)
    user_data.set_hotels_value(chat_id=message.chat.id, value=hotel_value)
    keyboard = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton('Да', callback_data='yes')
    but_2 = types.InlineKeyboardButton('Нет', callback_data='no')
    keyboard.add(but_1, but_2)
    bot.send_message(message.chat.id, 'Загрузить фото отелей?', reply_markup=keyboard)


@exc_handler
@bot.callback_query_handler(func=lambda call: 'Загрузить фото отелей?' in call.message.text)
def ask_photo_value(call: types.CallbackQuery) -> None:
    """Установка флага необходимости загрузки фото"""
    answer = call.data
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if answer == 'yes':
        user_data.set_needed_photo(chat_id=call.message.chat.id, value=True)
        set_photo_value(call.message)
    else:
        user_data.set_needed_photo(chat_id=call.message.chat.id, value=False)
        get_results(call.message)


@exc_handler
def set_photo_value(message: types.Message):
    """Выбор кол-ва фото"""
    bot.send_message(message.chat.id, 'Введите количество фото для загрузки по каждому отелю(макс. - 7)')
    bot.register_next_step_handler(message, get_results)


@exc_handler
def get_results(message: types.Message) -> None:
    """Получение результатов"""
    if user_data.get_needed_photo(chat_id=message.chat.id):
        user_data.set_photos_value(chat_id=message.chat.id, value=int(message.text))

    temp = bot.send_message(chat_id=message.chat.id, text='Поиск...')
    hotels_dict, hotel_link = user_data.get_hotels(user_id=message.chat.id)
    nights = user_data.read_data(message.chat.id)['night_value']
    if hotels_dict:
        bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id, text='Вот, что я нашёл:')
        for index, i_data in enumerate(hotels_dict.values()):
            if index + 1 > user_data.get_hotels_value(chat_id=message.chat.id):
                break
            answer = '\nОтель: {name}' \
                     '\nАдрес: {address}' \
                     '\nРасстояние до: {distance}' \
                     '\nЦена за сутки: {price}' \
                     '\nЦена за {nights} ночей: ${total_price}' \
                     '\nПосмотеть на Google maps: {address_link}' \
                     '\nПодробнее по ссылке: {link}\n'.format(
                name=i_data['name'],
                address_link='https://www.google.ru/maps/place/' + i_data['coordinate'],
                address=user_data.get_address(i_data),
                distance=user_data.get_landmarks(i_data),
                price=i_data['price'],
                nights=nights,
                total_price=user_data.count_total_price(message.chat.id, i_data['price']),
                link='https://hotels.com/ho' + str(i_data['id'])
            )
            bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True)
            if user_data.get_needed_photo(chat_id=message.chat.id):
                photo_list = user_data.get_get_photos(user_id=message.chat.id, hotel_id=i_data['id'])
                try:
                    for i_photo in photo_list:
                        bot.send_photo(chat_id=message.chat.id, photo=i_photo)

                except Exception:
                    bot.send_message(message.chat.id, 'Фото получить не удалось.')

    else:
        bot.send_message(message.chat.id, 'Поиск не дал результатов...')


bot.polling(non_stop=True, interval=0)