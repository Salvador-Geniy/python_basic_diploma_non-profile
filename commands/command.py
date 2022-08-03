from loader import bot
from user_data import *
import functools
from typing import Union, Callable
from telebot import types
from botrequests import main_request
import commands
from dataclasses import asdict


user = DataUser()


def exc_handler(method: Callable):
    """Декоратор. Обрабатывает ошибки, перезапускает бот"""
    @functools.wraps(method)
    def wrapper(message: Union[types.Message, types.CallbackQuery]) -> None:
        try:
            method(message)
        except Exception:
            bot.send_message(chat_id=message.chat.id, text=user.get_ans('restart'))
            welcome(message)
    return wrapper


@bot.message_handler(regexp=r'.*[Пп]ривет.*')
@bot.message_handler(commands=['start', 'hello_world'])
@exc_handler
def welcome(message):
    """Стартовое сообщение.Выбор команды"""
    user.user_id = message.from_user.id
    user.history = {}
    bot.send_message(message.chat.id, user.get_ans('start'), parse_mode='html')


@bot.message_handler(commands=['history'])
def print_history(message):
    """Вывод истории запросов пользователя"""
    user.user_id = message.from_user.id
    history = commands.history_com.history_com(message.from_user.id)
    bot.send_message(chat_id=message.chat.id, text=user.get_ans('found'))
    bot.send_message(message.from_user.id, history, parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
@exc_handler
def set_func(message):
    """Установка функции, выбраной пользователем"""
    user.user_id = message.from_user.id
    pattern = r'\w+'
    user.sorted_func = re.search(pattern, message.text).group()
    if user.sorted_func == 'bestdeal':
        user.flag_additional_questions = True
    bot.send_message(chat_id=message.chat.id, text=user.get_ans('city_name'))


@bot.message_handler(content_types=['text'])
@exc_handler
def choose_city(message):
    """Выбор города"""
    temp = bot.send_message(chat_id=message.chat.id, text=user.get_ans('search'))
    result = main_request.check_city(message)
    user.city_list = result
    keyboard = types.InlineKeyboardMarkup()
    for city_name, city_id in result.items():
        keyboard.add(types.InlineKeyboardButton(text=city_name, callback_data=city_id))
    bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id, text=user.get_ans('results'), reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: user.get_ans('results') in call.message.text)
@exc_handler
def city_setter(call: types.CallbackQuery) -> None:
    """Установка выбранного города"""
    user.city_id = call.data
    user.city_name = set_city(user, call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)

    if user.flag_additional_questions:
        choose_price_range(call.message)
    else:
        choose_night_value(call.message)


@exc_handler
def choose_price_range(message: types.Message) -> None:
    """Выбор диапазона цен"""
    bot.send_message(chat_id=message.chat.id, text=user.get_ans('price_range'))
    bot.register_next_step_handler(message, choose_dist_range)


@exc_handler
def choose_dist_range(message: types.Message) -> None:
    """Обработка диапазона цен, выбор диапазона расстояний"""
    user.price_range = set_price_range(message)
    bot.send_message(chat_id=message.chat.id, text=user.get_ans('dist_range'))
    bot.register_next_step_handler(message, choose_night_value)


@exc_handler
def choose_night_value(message: types.Message) -> None:
    """Обработка диапазона расстояний, выбор кол-ва ночей пребывания"""
    user.dist_range = set_dist_range(message)
    bot.send_message(chat_id=message.chat.id, text=user.get_ans('night_count'))
    bot.register_next_step_handler(message, hotel_value)


@exc_handler
def hotel_value(message: types.Message) -> None:
    """Обработка кол-ва ночей пребывания, выбор кол-ва отелей для поиска"""
    user.night_value = int(message.text)
    bot.send_message(chat_id=message.chat.id, text=user.get_ans('hotel_count'))
    bot.register_next_step_handler(message, photo_need)


@exc_handler
def photo_need(message: types.Message) -> None:
    """Обработка кол-ва отелей для поиска, выбор необходимости загрузки фото"""
    user.hotels_value = int(message.text)
    keyboard = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(user.get_ans('positive'), callback_data='yes')
    but_2 = types.InlineKeyboardButton(user.get_ans('negative'), callback_data='no')
    keyboard.add(but_1, but_2)
    bot.send_message(chat_id=message.chat.id, text=user.get_ans('need_hotel_photo'), reply_markup=keyboard)


@exc_handler
@bot.callback_query_handler(func=lambda call: user.get_ans('need_hotel_photo') in call.message.text)
def ask_photo_value(call: types.CallbackQuery) -> None:
    """Установка флага необходимости загрузки фото"""
    answer = call.data
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if answer == 'yes':
        user.needed_photo = True
        set_photo_value(call.message)
    else:
        get_results(call.message)


@exc_handler
def set_photo_value(message: types.Message):
    """Выбор кол-ва фото"""
    bot.send_message(chat_id=message.chat.id, text=user.get_ans('count_photo'))
    bot.register_next_step_handler(message, get_results)


@exc_handler
def get_results(message: types.Message) -> None:
    """Получение результатов"""
    if user.needed_photo:
        user.photos_value = int(message.text)

    temp = bot.send_message(chat_id=message.chat.id, text=user.get_ans('search'))
    hotels_dict = get_hotels(user)

    if hotels_dict:
        bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id, text=user.get_ans('found'))
        for index, data in enumerate(hotels_dict.values()):
            if index + 1 > user.hotels_value:
                break
            i_data = asdict(data)
            answer = get_answer(i_data, user)
            bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True)
            if user.needed_photo:
                photo_list = get_photos(user, i_data['id'])
                try:
                    for i_photo in photo_list:
                        bot.send_photo(chat_id=message.chat.id, photo=i_photo)

                except Exception:
                    bot.send_message(chat_id=message.chat.id, text=user.get_ans('no_photo'))

    else:
        bot.send_message(chat_id=message.chat.id, text=user.get_ans('no_result'))