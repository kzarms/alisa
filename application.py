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

def buttons(id):
    URLs = {
        'CBS': 'https://www.cbs.com',
        'HBO': 'www.hbogo.com', 
        'Showtime': 'https://www.sho.com',
        'Netflix': 'https://www.netflix.com',
    }

    f = open('films.csv', mode="r", encoding="utf-8")
    films = csv.reader(f, delimiter='\t')
    for row in films:
        if id == row[0]:
            #we found a film, close file and exit form the loop
            f.close()
            break
    return URLs[row[8]]


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
        res['response']['text'] = 'Заглушка для подробной информации'
        return
    if text == 'cмотреть':
        res['response']['text'] = 'Слышала, что есть альтернативные вариаты просмотра ;)'
        res['response']['end_session'] = True
        return
    #res['response']['text'] = 'работаю ...'
    #execute seach function on top of this text
    result = CoreSearch(text)
    sessionStorage[user_id] = result[1]
    #
    res['response']['text'] = result[0]
    #add suggessted buttons
    if result[1] != None:
        res['response']['buttons'] = [
            {
                "title": "Смотреть",
                "payload": {},
                "url": buttons(result[1]),
                "hide": True
            },
            {
                "title": "Инфо",
            }
        ]
