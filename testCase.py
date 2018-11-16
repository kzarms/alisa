#import io
import requests
import sqlite3
from datetime import datetime, timedelta
#import datetime

def MyPostCommand(remote, command, i):
    if remote:
        URL = "https://kzaralisa.azurewebsites.net" 
        #URL = "https://alisa.ikot.eu"
    else:
        URL = "http://127.0.0.1:5000"
    if (command == '') and (i == 1):
        result = True
    else:
        result = False  
    HEADERS = {'Content-Type': 'application/json'}
    DATA = {
        "meta": {
            "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
            "interfaces": {
            "screen": {}
            },
            "locale": "ru-RU",
            "timezone": "UTC"
        },
        "request": {
            "command": command,
            "nlu": {
            "entities": [],
            "tokens": [
                ""
            ]
            },
            "original_utterance": command,
            "type": "SimpleUtterance"
        },
        "session": {
            "message_id": i,
            "new": result,
            "session_id": "aa78144d-44710a9e-64ff4317-ad1be4d5",
            "skill_id": "6b89b259-e2f2-44fb-b203-17833d97595a",
            "user_id": "468F375A4A728CBB299ADEC2EFAE67F25B5D8694223508B783EA9BA08601600C"
        },
        "version": "1.0"
    }    
    r = requests.post(url = URL, json = DATA, headers = HEADERS)
    data = r.json()
    return data['response']['text']

def getFilmList():
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    cmd = 'SELECT nameRu FROM films'
    cur.execute(cmd)
    filmList = cur.fetchall()
    con.close()
    return filmList

filmList = getFilmList()
#for i in range(10,20):
for i in range(len(filmList)):
    n = datetime.now()
    result = MyPostCommand(False, filmList[i][0], 2)
    print(('серия' in result.lower()), filmList[i][0], result, datetime.now() - n,)

keywords = ['ping','пинг',
            'как тебя зовут','помощь','что ты умеешь',
            'спасибо','благодарю',
            'все','выход','конец','завешить','стоп',
            'добавить сериал','подробнее','сериал','смотреть',]
#test fist key phrases (not related to previouse search)
for i in range(4):
    result = MyPostCommand(False, keywords[i], 2)
    print('серии' in result.lower() or 'reply' in result.lower() , keywords[i],)

for i in range(5,12):
    result = MyPostCommand(False, keywords[i], 2)
    print('.' in result.lower(), keywords[i],)

#execute search to the random film
for i in range(100,101):
    resutl = MyPostCommand(False, filmList[i][0], 2)
    result1 = MyPostCommand(False, 'сериал', 3)
    result2 = MyPostCommand(False, 'смотреть', 4)
    print((('сериал' in result1.lower()) and ('слышала' in result2.lower())), filmList[i][0],)

# print(MyPostCommand(False, 'тбв', 2))
# print(MyPostCommand(False, 'сериал', 3))
# print(MyPostCommand(False, 'смотреть', 4))

# for i in range(3,len(keywords)):
#     result = MyPostCommand(False, keywords[i], 2)
#     print(keywords[i], result,)
# for film in filmList:    
#     result = MyPostCommand(False, film[0], 2)
#     print(('серия' in result.lower()), film[0], result,)

#MyPostCommand(False, "Теория большого взрыва", 2)