# coding: utf-8
# UTF-8.
#
from __future__ import unicode_literals

import json
import logging

from dbfunctions import *

from flask import Flask, request
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Session storage
sessionStorage = {}

# Start flask with POST method listening
@app.route("/", methods=['POST'])

#main function
def main():
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
    if (text == 'добавить сериал') and (sessionStorage[user_id] == 0):
        res['response']['text'] = 'Спасибо! Мы проверим ваше обращение и добавим интересующий сериал в ближайшее вермя'
        return
    if text == 'подробнее':
        if sessionStorage[user_id] != 0:
            #res['response']['text'] = getFilmInfoLocal(str(sessionStorage[user_id]))
            res['response']['text'] = 'Заглушка для подробной информации о серии'            
        else:
            res['response']['text'] = 'Я потеряла нить нашей беседы :)'
        return
    if text == 'сериал':
        if sessionStorage[user_id] != 0:
            res['response']['text'] = getFilmInfoLocal(str(sessionStorage[user_id]))
        else:
            res['response']['text'] = 'Я потеряла нить нашей беседы :)'
        return
    if text == 'cмотреть':
        if sessionStorage[user_id] != 0:
            res['response']['text'] = 'Слышала, что есть альтернативные вариаты просмотра ;)'
            res['response']['end_session'] = True
        else:
            res['response']['text'] = 'Я потеряла нить нашей беседы :)'
        return
    #no more key works, execute seach function on top of this text
    # print('test search')
    result = CoreSearch(text)
    #save intId into dictionary
    sessionStorage[user_id] = result[1]
    #return result to user
    res['response']['text'] = result[0]
    #res['response']['text'] = CoreSearch(text)
    #add suggessted buttons
    if result[1] == 0:        
        res['response']['buttons'] = [
            {
                "title": "Добавить сериал",
            }
        ]
    if result[1] != 0:
        res['response']['buttons'] = [
            {
                "title": "Подробнее",
            },
            {
                "title": "Сериал",
            },
            {
                "title": "Смотреть",
                "url": OfficialURL(result[1]),
                #"hide": True
            }
        ]


