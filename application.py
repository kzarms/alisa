# coding: utf-8
# UTF-8.
from __future__ import unicode_literals
from dbfunctions import *
#
import json
import logging

from flask import Flask, request
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Session storage
sessionStorage = {}

# Start flask with POST method listening
@app.route("/", methods=['POST'])

def main():
# Main function
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

# Hanle dialog
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        #New user, return welcome message     
        res['response']['text'] = 'Привет, что ищешь?'
        return

    # Take user text
    text = req['request']['command'].lower()
    res['response']['text'] = 'работаю ...'
    #execute seach function on top of this text
    result = CoreSearch(text)
    #if req['request']['original_utterance'].lower() in [
    #    'нет',
    #    'отстань',
    #    'я не пью',
    #    'мне нельзя',
    #]:
    #    # Пользователь согласился, прощаемся.
    #    res['response']['text'] = 'Жаль, а ведь так хорошо начали ...'
    #    return

    # Если нет, то убеждаем его купить слона!
    #res['response']['text'] = 'Все говорят "%s", а ты реально хочешь пива?' % (
    #    req['request']['original_utterance']
    #)
    #res['response']['buttons'] = get_suggests(user_id)
    # if len(result) > 0:
    #     res['response']['text'] = " ".join(result)
    # else:
    #     res['response']['text'] = "Не удалось найти ваш фильм, попробуйте другой."

    #retun results from seach function
    res['response']['text'] = result
    #add suggessted buttons
    res['response']['buttons'] = []
# Функция возвращает две подсказки для ответа.
# def get_suggests(user_id):
#     session = sessionStorage[user_id]

#     # Выбираем две первые подсказки из массива.
#     suggests = [
#         {'title': suggest, 'hide': True}
#         for suggest in session['suggests'][:2]
#     ]

#     # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
#     session['suggests'] = session['suggests'][1:]
#     sessionStorage[user_id] = session

#     # Если осталась только одна подсказка, предлагаем подсказку
#     # со ссылкой на Яндекс.Маркет.
#     if len(suggests) < 2:
#         suggests.append({
#             "title": "Лови",
#             "url": "https://market.yandex.ru/search?text=пиво",
#             "hide": True
#         })

#     return suggests