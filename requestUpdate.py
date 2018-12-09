import requests


def requestUpdate(remote, command, i):
    if remote:
        URL = "https://kzaralisa.azurewebsites.net"
        #URL = "https://alisa.ikot.eu/app"
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

print(str(requestUpdate("1", "477b0c56-3dc5-4b69-ae85-a2eec9e378ce", 1)))
