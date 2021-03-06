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
            "command": "477b0c56-3dc5-4b69-ae85-a2eec9e378cd",
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
for i in range(len(filmList)):
    n = datetime.now()
    result = MyPostCommand(False, filmList[i][0], 2)
    print(('серия' in result.lower()) or ('съемки' in result.lower()), (datetime.now() - n).total_seconds(), filmList[i][0], result, )

keywords = ['ping','пинг',
            'как тебя зовут','помощь','что ты умеешь',
            'привет','здравствуй','здравствуйте','хай','hi',
            'спасибо','благодарю',
            'все','выход','конец','завешить','стоп',
            'добавить сериал','подробнее','сериал','сайт',]
#test fist key phrases (not related to previouse search)
for i in range(4):
    result = MyPostCommand(False, keywords[i], 2)
    print('серии' in result.lower() or 'reply' in result.lower() , keywords[i],)

for i in range(5,21):
    result = MyPostCommand(False, keywords[i], 2)
    print('.' in result.lower(), keywords[i],)

print(MyPostCommand(False, 'тбв', 2))

wastePhrase = "это пустая фраза "
for i in range(0,20):
    n = datetime.now()
    result = MyPostCommand(False, (wastePhrase + filmList[i][0]), 2)
    print(('серия' in result.lower()) or ('съемки' in result.lower()), (datetime.now() - n).total_seconds(), filmList[i][0], result, )

#typo mistake
for i in range(0,20):
    n = datetime.now()
    result = MyPostCommand(False, filmList[i][0][1:], 2)
    print(('серия' in result.lower()), (datetime.now() - n).total_seconds(), filmList[i][0], result, )

#execute search to the random film
for i in range(0,20):
    resutl = MyPostCommand(False, filmList[i][0], 2)
    result1 = MyPostCommand(False, 'сериал', 3)
    result2 = MyPostCommand(False, 'сайт', 4)
    print((('сериал' in result1.lower()) and ('приятного' in result2.lower())), filmList[i][0],)

print(MyPostCommand(True, 'что посмотреть?', 2))
print(MyPostCommand(False, 'куку', 4))
# print(MyPostCommand(False, 'сериал', 3))
# print(MyPostCommand(False, 'сайт', 4))

# for i in range(3,len(keywords)):
#     result = MyPostCommand(False, keywords[i], 2)
#     print(keywords[i], result,)
# for film in filmList:
#     result = MyPostCommand(False, film[0], 2)
#     print(('серия' in result.lower()), film[0], result,)

#MyPostCommand(False, "Теория большого взрыва", 2)