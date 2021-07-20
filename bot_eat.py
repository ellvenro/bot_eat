import config

import telebot
import json
import requests

from telebot import types

# необходимые глобальные переменные
point = ''                                                  # местоположение на карте (долгота и широта, разделенные ',')
msg = {                                                     # сообщение, которые выводятся пользователю
    'start' : 'Тут можно перекусить.. Что выберешь?)',
    'loc' : 'Покажи на карте, где ты находишься\n\nНу а если ты в СПб, можешь ввести ближайшую станцию метро..',
    'call' : 'Оо.. Есть еще места, где можно перекусить, можешь выбрать'
}

print('Бот запущен. Нажмите Ctrl+C для завершения')
bot = telebot.TeleBot(config.token)

# функция обработки локации
    # принимает местоположение пользователя и приводит к необходимому виду (долгота и широта, разделенные ',') для последующего отправления запроса в Яндекс
    # вызывает функцию создания inline клавиатуры 
@bot.message_handler(content_types=['location'])
def func_location(message):
    global point
    point = str(message.location.longitude) + ','+ str(message.location.latitude)
    func_inline_button(message.chat.id, msg['start'])

# функция обработки команды /start
    # создает клавиатуру с возможностью отправки местоположения
@bot.message_handler(commands=['start'])
def func_start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button = types.KeyboardButton(text='Отправить местоположение', request_location=True)
    keyboard.add(button)
    bot.send_message(message.chat.id, msg['loc'], reply_markup=keyboard)

# функция обработки inline кнопок
    # запускает функцию поиска по организациям
@bot.callback_query_handler(func=lambda call: True)
def func_call(call):
    if (call.data == 'McDonald’s' or call.data == 'KFC' or call.data == 'Subway' or call.data == 'Burger King'):
        if point == '':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg['loc'])
        else:
            func_search_gis(call)

# функция обработки текста
    # определяет геопозицию введенного пользователем адреса (в частности станции метро)
    # вызывает функцию создания inline клавиатуры
@bot.message_handler(content_types=['text'])
def func_text(message):
    func_geo_gis(message)
    func_inline_button(message.chat.id, msg['start'])

# Функция определения геопозиции введенного пользователем адреса (в частности станции метро) с помощью 2gis
def func_geo_gis(message):
    # выполнение запроса к Geocoder API 2gis (get-запрос: gis_geo) с ключом API_key_gis
    query = 'СПб метро ' + message.text 
    r = requests.get(url=config.gis_geo, params={
        'q' : query,
        'key': config.API_key_gis,
        'fields' : 'items.point'
    }) 
    result = json.loads(r.text)
    global point
    point = str(result['result']['items'][0]['point']['lon']) + ',' + str(result['result']['items'][0]['point']['lat'])

# Функция определения геопозиции введенного пользователем адреса (в частности станции метро) с помощью Яндекс
def func_geo_yandex(message):
    # выполнение запроса к HTTP Геокодер Яндекс (get-запрос: yandex_geo) с ключом API_key_geo
    r = requests.get(url=config.yandex_geo, params={
        'geocode' : query,
        'apikey': config.API_key_geo,
        'format' : 'json'
    })    
    result = json.loads(r.text)
    global point
    point = result['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    point = point[:9] + ',' + point[10:]





# функция поиска по местам с помощью 2gis
    # работает с помощью библиотеки requests, запросы отправляются и принимаются согласно документации API поиска по организациям
    # вызывает функцию создания inline клавиатуры 
def func_search_gis(call):

    # выполнение запроса Places API 2gis (get-запрос: gis_search) с ключом API_key_gis
    r = requests.get(url=config.gis_search, params={
        'q' : call.data,
        'key': config.API_key_gis,
        'point' : point,
        'type' : 'branch',
        'fields' :'items.point,items.schedule',
        'radius' : '1000'
    }) 
    result = json.loads(r.text)

    try:
        i = result['result']['total']
        if i == 1:
            text1 = 'Я нашел ' + str(i) + ' ресторан по твоему выбору'
        elif (i > 1 and i < 5):
            text1 = 'Я нашел ' + str(i) + ' ресторана по твоему выбору'
        else:
            text1 = 'Я нашел ' + str(i) + ' ресторанов по твоему выбору'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text1)
        for item in result['result']['items']:
            bot.send_venue(call.message.chat.id, item['point']['lat'], item['point']['lon'], item['name'], item['address_name'])
    except:
        text1 = 'Ресторанов '+ call.data + ' рядом нет..('
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text1)

    func_inline_button(call.message.chat.id, msg['call'])

# функция поиска по организациям с помощью Яндекс
    # работает с помощью библиотеки requests, запросы отправляются и принимаются согласно документации API поиска по организациям
    # вызывает функцию создания inline клавиатуры 
def func_search_yandex(call):
    # выполнение запроса API поиска по организациям Яндекс (get-запрос: yandex_search) с ключом API_key_search
    r = requests.get(url=config.yandex_search, params={
      'apikey': config.API_key_search,
      'text': call.data,
      'lang': 'ru_RU',
      'type': 'biz',
      'll': point,
      'spn': '0.050000,0.015000',
      'rspn': 1
    })    
    result = json.loads(r.text)

    i = result['properties']['ResponseMetaData']['SearchResponse']['found']
    if i != 0:
        text1 = ''
        if i == 1:
            text1 = 'Я нашел ' + str(i) + ' ресторан по твоему выбору'
        elif (i > 1 and i < 5):
            text1 = 'Я нашел ' + str(i) + ' ресторана по твоему выбору'
        else:
            text1 = 'Я нашел ' + str(i) + ' ресторанов по твоему выбору'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text1)
        for item in result['features']:
            bot.send_venue(call.message.chat.id, item['geometry']['coordinates'][1], item['geometry']['coordinates'][0], item['properties']['CompanyMetaData']['name'], item['properties']['CompanyMetaData']['address'])
    else:
        text1 = 'Ресторанов '+ call.data + ' рядом нет..('
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text1)

    func_inline_button(call.message.chat.id, msg['call'])
    
# функция создания inline клавиатуры
def func_inline_button(c_id, text):
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    button1 = types.InlineKeyboardButton(text='McDonald’s', callback_data='McDonald’s')
    button2 = types.InlineKeyboardButton(text='KFC', callback_data='KFC')
    keyboard.add(button1, button2)
    button3 = types.InlineKeyboardButton(text='Subway', callback_data='Subway')  
    button4 = types.InlineKeyboardButton(text='Burger King', callback_data='Burger King') 
    keyboard.add(button3, button4)

    bot.send_message(c_id, text, reply_markup=keyboard)




bot.polling()
#if __name__ == '__main__':
#	bot.infinity_polling()
