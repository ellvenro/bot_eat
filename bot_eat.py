import config
import functions

import telebot
import json
import requests

from telebot import types

# необходимые глобальные переменные
point = ''                                                  # местоположение на карте (долгота и широта, разделенные ',')

print('Бот запущен. Нажмите Ctrl+C для завершения')
bot = telebot.TeleBot(config.token)

# функция обработки локации
    # принимает местоположение пользователя и приводит к необходимому виду (долгота и широта, разделенные ',') для последующего отправления запроса в Яндекс
    # вызывает функцию создания inline клавиатуры 
@bot.message_handler(content_types=['location'])
def func_location(message):
    global point
    point = str(message.location.longitude) + ','+ str(message.location.latitude)
    functions.func_inline_button(bot, message.chat.id, functions.msg['start'])

# функция обработки команды /start
    # создает клавиатуру с возможностью отправки местоположения
@bot.message_handler(commands=['start'])
def func_start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button = types.KeyboardButton(text='Отправить местоположение', request_location=True)
    keyboard.add(button)
    bot.send_message(message.chat.id, functions.msg['loc'], reply_markup=keyboard)

# функция обработки inline кнопок
    # запускает функцию поиска по организациям
    # вызывает функцию создания inline клавиатуры
@bot.callback_query_handler(func=lambda call: True)
def func_call(call):
    if point == '':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id, text=functions.msg['loc'])
    elif (call.data == 'McDonald’s' or call.data == 'KFC' or call.data == 'Subway' or call.data == 'Burger King'):
        functions.func_search_gis(bot, call, point)
    elif call.data == 'var':
        functions.func_var(bot, call)

# функция обработки текста
    # определяет геопозицию введенного пользователем адреса (в частности станции метро)
    # вызывает функцию создания inline клавиатуры
@bot.message_handler(content_types=['text'])
def func_text(message):
    global point
    point = functions.func_geo_gis(bot, message)
    functions.func_inline_button(bot, message.chat.id, functions.msg['start'])

bot.polling()
#if __name__ == '__main__':
#	bot.infinity_polling()
