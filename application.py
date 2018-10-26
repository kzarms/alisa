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
    if text == 'инфо':
        if sessionStorage[user_id] != 0:
            res['response']['text'] = getFilmInfoLocal(sessionStorage[user_id])
            #res['response']['text'] = 'Заглушка для подробной информации'
        else:
            res['response']['text'] = 'Я потеряла нить нашей беседы :)'
        return
    if text == 'cмотреть':
        res['response']['text'] = 'Слышала, что есть альтернативные вариаты просмотра ;)'
        res['response']['end_session'] = True
        return

    #execute seach function on top of this text
    # print('test search')
    result = CoreSearch(text)
    print(result)
    sessionStorage[user_id] = result[1]
    print(sessionStorage)
    #
    res['response']['text'] = result[0]
    #res['response']['text'] = CoreSearch(text)
    #add suggessted buttons
    if result[1] != 0:
        res['response']['buttons'] = [
            {
                "title": "Смотреть",
                "url": OfficialURL(result[1]),
                "hide": True
            },
            {
                "title": "Инфо",
            }
        ]


