# importing the requests library 
import csv
import io
import requests
from datetime import datetime, timedelta

token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDExNjY4NjAsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MTA4MDQ2MCwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.mqZi5mUntc7_0kFM4FKbmri7kESL2Y68l0v8iMTJf5IjOfjvMLQ5CvJrkErtNuERqu_ymEzlEG-Bx6YWG4vZJUGXDCnTVx4Y3i3jIFdzCm88LQsMNTw-Euw5IyS8Sr62n_8VXRcM2iTLVjT7Cfi5L_a9bKVWCs4WpLIA-Hri0uXcHjXB7LBX2JBMVtl8e536ASGoqc3pEHF9s4xUf4o4evz-ZVXgI6dzjGNTy0zXmbW1_YkjE8cG0wdSTNMjie6pq6euvP4EEdq7lOecTje4miXD5YtbuAfihv33b_7ffeAP__zbtjXJsdcIla0OipmuVYdcxSK7mMG930M8p4UtHg'

#update tokenыукпун1989
def tockenRefresh():
    URL = "https://api.thetvdb.com/login"   
    HEADERS = {'Content-Type': 'application/json'}  
    DATA = {"apikey": "0AHRVCC9FPSYWACV", "userkey": "QOCM9N37ADVTQ42W", "username": "vlkootmni"}
    r = requests.post(url = URL, json = DATA, headers = HEADERS)
    data = r.json()
    global token
    if 'Error' in data:
        print('Error in token request')
        token = '0'
    if 'token' in data:
        print('the token has been got sussessfully')
        token = data['token']
 
def tvdbGetSerialInfo(filmID):
    #check we do not have such film in the list
    f = open('films.csv', mode="r", encoding="utf-8")
    recordList = list(f)
    f.close()
    for i in recordList:
        if i.split('\t')[1] == str(filmID):
            print('This film ID', str(filmID), 'is already in the DB')
            return
    #the last line + 1 is a new index
    myid = int(i.split('\t')[0]) + 1
    #myid = int((list(f)[-1]).split('\t')[0]) + 1

    URL = "https://api.thetvdb.com"    
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)} 
    URL1 = URL + '/series/' + str(filmID)
    r = requests.get(url = URL1, headers = HEADERS)  
    # extracting data in json format 
    data = r.json()
    if 'Error' in data:
        #there is an error
        if 'No results for your query' in data['Error']:
            return 'Error', 'Search error'
        if data['Error'] == 'Not authorized':
            #try update token
            tockenRefresh()
            print(token)
            if token == '0':
                return 'Error', 'Auth error and update token error'
            HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
            r = requests.get(url = URL1, headers = HEADERS)
            data = r.json()
            if 'Error' in data:
                return 'Error', 'Error token update'
    #collect Rus Name
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}
    r = requests.get(url = URL1, headers = HEADERS)
    dataru = r.json()
    #collect info about episodes summary
    URL2 = URL + '/series/' + str(filmID) + '/episodes/summary'
    r2 = requests.get(url = URL2, headers = HEADERS)
    data2 = r2.json()

    lastSeason = max(map(int, data2['data']['airedSeasons']))
    if data['data']['seriesId'] == "":
        seriesId = '999999'
    else:
        seriesId = data['data']['seriesId']
    if data['data']['status'] == 'Ended':
        #collect info about last episode name
        URL3 = URL + '/series/' + str(filmID) + '/episodes/query'
        HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}
        PARAMS = {'airedSeason':str(lastSeason),}
        r = requests.get(url = URL3, headers = HEADERS, params = PARAMS)
        data3 = r.json()
        maxEpnum = 1
        for episod in data3['data']:
            if int(episod['airedEpisodeNumber']) > maxEpnum:
                maxEpnum = int(episod['airedEpisodeNumber'])
                maxEp = episod
        if  maxEp['episodeName'] == None:
            #no rus name
            HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
            r = requests.get(url = URL3, headers = HEADERS, params = PARAMS)
            data3 = r.json()
            maxEpnum = 1
            for episod in data3['data']:
                if int(episod['airedEpisodeNumber']) > maxEpnum:
                    maxEpnum = int(episod['airedEpisodeNumber'])
                    maxEp = episod
        firstAired = maxEp['firstAired']
        airedEpisodeNumber = maxEp['airedEpisodeNumber']
        episodeName = maxEp['episodeName']
    else:
        firstAired = 'TBD'
        airedEpisodeNumber = 'TBD'
        episodeName = 'TBD'
    #
    # f = open('films.csv', mode="r", encoding="utf-8")
    # myid = int((list(f)[-1]).split('\t')[0]) + 1
    # f.close()
    #summ result in the finnal line
    fields = [str(myid),
        data['data']['id'],
        data['data']['imdbId'],
        seriesId,
        data['data']['seriesName'],
        dataru['data']['seriesName'],
        data['data']['status'],
        data['data']['firstAired'],
        data['data']['network'],
        str(lastSeason),
        data2['data']['airedEpisodes'],
        data['data']['siteRating'],
        firstAired,
        airedEpisodeNumber,
        episodeName,
        ]
    #add info into main csv file
    f = open('films.csv', mode="a", encoding="utf-8")
    csv_writer = csv.writer(f, lineterminator='\n', delimiter='\t')
    csv_writer.writerow(fields)
    f.close()
    #add alias into the NameVariations
    if dataru['data']['seriesName'] != None:
        feild1 = [str(myid),
            dataru['data']['seriesName'].lower()
        ]
    if data['data']['seriesName'] != None:
        feild2 = [str(myid),
            data['data']['seriesName'].lower()
        ]
    fa = open('NameVariations.csv', mode="a", encoding="utf-8")
    csv_writer = csv.writer(fa, lineterminator='\n', delimiter='\t')
    if 'feild1' in locals():
        csv_writer.writerow(feild1)
    if 'feild2' in locals():
        csv_writer.writerow(feild2)
    fa.close()
    print('The film ID', str(filmID), 'has been added successfully')

#test add series :)
#tvdbGetSerialInfo(273455)
#tvdbGetSerialInfo(269586)
#tvdbGetSerialInfo(321219)
#tvdbGetSerialInfo(281776)
#tvdbGetSerialInfo(312505)
#tvdbGetSerialInfo(295683)
#tvdbGetSerialInfo(295760)
"""
f = open('films2.csv', mode="r", encoding="utf-8")
recordList = list(f)
f.close()
for i in range(2,60):
    #print(recordList[i].split('\t')[1])
    tvdbGetSerialInfo(recordList[i].split('\t')[1])

series_id = open("series_id.txt", 'r')
for line in series_id.readlines():
    id = str.rstrip(line)
    tvdbGetSerialInfo(id)
    print(id + ' completed')

"""

def MyPostCommand(remote, command, i):
    if remote:
        URL = "https://kzaralisa.azurewebsites.net" 
    else:
        URL = "http://127.0.0.1:5000"
    if command == '':
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



#print(MyPostCommand(False, 'кяввм', 2))
n = datetime.now()
print(MyPostCommand(False, 'стрела', 2))
print(datetime.now() - n)
print(MyPostCommand(False, 'подробнее', 2))
print(datetime.now() - n)
print(MyPostCommand(False, 'сериал', 2))
print(datetime.now() - n)

n = datetime.now()
print(MyPostCommand(True, 'доктор хаус', 2))
print(datetime.now() - n)
print(MyPostCommand(True, 'подробнее', 2))
print(datetime.now() - n)
print(MyPostCommand(True, 'сериал', 2))
print(datetime.now() - n)
