import config

import telebot
import json
import requests

from telebot import types

# функция определения геопозиции введенного пользователем адреса (в частности станции метро) с помощью 2gis
def func_geo_gis(bot, message):
    # выполнение запроса к Geocoder API 2gis (get-запрос: gis_geo) с ключом API_key_gis
    query = 'СПб метро ' + message.text 
    r = requests.get(url=config.gis_geo, params={
        'q' : query,
        'key': config.API_key_gis,
        'fields' : 'items.point'
    }) 
    result = json.loads(r.text)
    point = str(result['result']['items'][0]['point']['lon']) + ',' + str(result['result']['items'][0]['point']['lat'])
    return point

# функция поиска по местам с помощью 2gis
    # работает с помощью библиотеки requests, запросы отправляются и принимаются согласно документации API поиска по организациям
def func_search_gis(bot, call, point):
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

# функция создания inline клавиатуры
def func_inline_button(bot, c_id, text):
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    button1 = types.InlineKeyboardButton(text='McDonald’s', callback_data='McDonald’s')
    button2 = types.InlineKeyboardButton(text='KFC', callback_data='KFC')
    keyboard.add(button1, button2)
    button3 = types.InlineKeyboardButton(text='Subway', callback_data='Subway')  
    button4 = types.InlineKeyboardButton(text='Burger King', callback_data='Burger King') 
    keyboard.add(button3, button4)

    bot.send_message(c_id, text, reply_markup=keyboard)