Телеграм бот Hotel Bot Search



Описание:

Данный телеграм бот позволяет найти выгодные предложения на сайте https://hotels.com.

При помощи специальных команд пользователь может:
1. Подобрать дешёвые отели - команда /lowprice.
2. Подобрать дорогие отели - команда /highprice.
3. Лучшие отели по соотношению цена-удалённость от центра - команда /bestdeal.
4. Посмотреть свою историю поиска отелей - команда - /history.

При разработке проекта использовался открытый API Hotels, который расположен на сайте https://rapidapi.com.



Реализация:

Все данные пользователя хранятся в персональной базе данных, в виде файла формата .json, что позволяет сохранить исторю поиска.

Реализована генерация следующих URL-ссылок:
- на страницу отеля, расположенную на сайте https://hotels.com
- на страницу Google Maps с точкой на объект размещения в соответствии с его координатами на Hotels Api.



Установка:

Перед тем, как начать:
Если вы не пользуетесь Python 3, вам нужно установить его:
Посетите официальный сайт https://python.org - там вы сможете найти всю информацию по установке Python

Так же необходимо установить библиотеку для Python:
telegrambotapi - https://core.telegram.org/bots/api

Создайте на своем компютере папку проекта
Склонируйте этот репозиторий в папку проекта

Зарегистрируйтесь на сайте rapidapi.com:

Перейдите в API Marketplace → категория Travel → Hotels
Нажмите кнопку Subscribe to Test
Выберите бесплатный пакет (Basic)

Скопируйте свой уникальный код RAPIDAPIKEY=*YourRapidKey* в файл проекта main_request.py, в словарь(поле) 'headers'

Пример:
headers = {
    'x-rapidapi-host': 'hotels4.p.rapidapi.com',
    'x-rapidapi-key': "YourRapidKey"
}


Обращаем ваше внимание на то, что у базового пакета есть ограничение по
количеству запросов в месяц, а именно — 500. Поэтому если возникнет проблема с
нехваткой запросов для тестирования проекта, то просто зарегистрируйте ещё один
аккаунт (или даже несколько).



Запустите бота командой python main.py из Терминала из папки с проектом



Описание работы команд:

Команда /help - помощь

Команды /start, /hello_world и /Привет
После ввода команды пользователь получает приветственное сообщение и у пользователя запрашивается команда для дальнейших действий.

Команда /lowprice
После ввода команды у пользователя запрашивается:
Город, где будет проводиться поиск
Количество ночей проживания
Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума)
Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”). При положительном ответе пользователь также вводит количество необходимых фотографий (не больше заранее определённого максимума)

Команда /highprice
После ввода команды у пользователя запрашивается:
Город, где будет проводиться поиск
Количество ночей проживания
Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума)
Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”). При положительном ответе пользователь также вводит количество необходимых фотографий (не больше заранее определённого максимума

Команда /bestdeal
После ввода команды у пользователя запрашивается:
Город, где будет проводиться поиск
Диапазон цен
Диапазон расстояния, на котором находится отель от центра
Количество ночей проживания
Количество отелей, которые необходимо вывести в результате (не больее заранее определённого максимума)
Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”). При положительном ответе пользователь также вводит количество необходимых фотографий, но не больее заранее определённого максимума.

Команда /history
После ввода команды пользователю выводится история поиска отелей:
Дата и время запроса
Команда, которую вводил пользователь
Отели, которые были найдены (с гиперссылкой на страницу отеля)


Окно Telegram-бота при запущенном Python-скрипте воспринимает следующие команды:

/help — помощь по командам бота
/lowprice — вывод самых дешёвых отелей в городе
/highprice — вывод самых дорогих отелей в городе
/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра
/history — вывод истории поиска отелей

Для команд lowprice, highprice и bestdeal сообщение с результатом содержит краткую информацию по каждому отелю. В эту информацию входит:

Название отеля
Адрес 
Ссылка на Google Maps
Ближайшие ориентиры (в т.ч. как далеко расположен от центра)
Цена за ночь 
Суммарная стоимость
N фотографий отеля (если пользователь счёл необходимым их вывод)
Гиперссылка на страницу отеля на Hotels.com