# coding: utf-8
# importing the requests library 
import csv
import io
import requests
from datetime import datetime, timedelta
import sqlite3
import datetime


token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDE2MjU4NDEsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MTUzOTQ0MSwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.LZhqi1Gpo7Bj-Eycuz9T7i3nByC4sZ-2tbgX3xE1Rk0gBvP0jv2vcjY0Df2bTEyDSl63rIrIHCUsVaRZPtMzskcKAa2vRd0QthN1x7meA10OXUvbF2qBPYir-dUlWGc4lQN5eJMcSHmS5cgzHpykooy15BoH4Ef4xXbMC0l3Jwt-r14DKW3eZ8rpx3lNQgz39o1m8whJARhkTfuQYFWdw_gsZMtoSkTJxFCvWWD09rn6ybqBQDjVr-4V-vBR25SMXT3-t6Z3wigVYYUUf2f66u9E0nh8FUoHeWUNlDt5gbhyexnZKJylARHfYr5fRvyzJ0dd6Zq8CDZXU1tu0YIsFw'

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
        #URL = "https://kzaralisa.azurewebsites.net" 
        URL = "https://alisa.ikot.eu"
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

#Connect and created films in the main DB
# con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
# cur = con.cursor()
# cur.execute("drop table films")
# cur.execute('''create table films
#     (tvdbId int,
#     imdbId varchar,
#     kinoId varchar,
#     nameEn varchar,
#     nameRu varchar,
#     status varchar,
#     firstAired data,
#     network varchar,
#     seazons int,
#     lastEpisode int,
#     ratingImbd double,
#     ratingKino double,
#     info text
#     )''')
# films = csv.reader(films_in_memory.splitlines(), delimiter='\t')
# header = next(films)
# for row in films:   
#     film = (row[1],
#         row[2],
#         None,
#         row[4],
#         row[5],
#         row[6],
#         datetime.datetime.strptime(row[7], '%Y-%m-%d'),
#         row[8],
#         int(row[9]),
#         int(row[10]),
#         float(row[11]),
#         0,
#         None,)
#     print(film)
#     cur.execute("insert into films values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", film)
# con.commit()
# con.close()

#stop films DB creation

#create serial table series
def createSeriesTable(seriesNumber, seasonNumber):
    #seriesNumber = 10
    # filmID = '296762'
    # seasonNumber = 1
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    cmd = 'SELECT tvdbId FROM films WHERE rowid=' + str(seriesNumber)
    cur.execute(cmd)
    filmID = cur.fetchone()
    
    URL = "https://api.thetvdb.com"   
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}  
    PARAMS = {'airedSeason':str(seasonNumber)} 
    #Create full request
    URL = URL + '/series/' + str(filmID[0]) + '/episodes/query'
    r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
    dataRu = r.json()
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
    r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
    dataEn = r.json()

    if int(seasonNumber) == 1:
        cmd = 'drop table if exists series_' + str(seriesNumber)
        cur.execute(cmd)
        #create a new one
        cmd = '''create table series_''' + str(seriesNumber) + '''
            (airedSeason int,
            airedEpisodeNumber int,
            episodeNameEn varchar,
            episodeNameRu varchar,
            firstAired data,
            director varchar,
            overviewEn text,
            overviewRu text,
            showUrl varchar,
            info text
            )'''
        cur.execute(cmd)
    episodes = []
    for i in range(len(dataEn['data'])):
        if dataEn['data'][i]['firstAired'] != '': 
            data = datetime.datetime.strptime(dataEn['data'][i]['firstAired'], '%Y-%m-%d')
        elif dataRu['data'][i]['firstAired'] != '':
            data = datetime.datetime.strptime(dataRu['data'][i]['firstAired'], '%Y-%m-%d')
        else:
            data = None
        episode = (int(dataEn['data'][i]['airedSeason']),
            int(dataEn['data'][i]['airedEpisodeNumber']),
            dataEn['data'][i]['episodeName'],
            dataRu['data'][i]['episodeName'],
            data,
            dataEn['data'][i]['director'],
            dataEn['data'][i]['overview'],
            dataRu['data'][i]['overview'],
            dataEn['data'][i]['showUrl'],
            None,)
        episodes.append(episode)
    
    sorted_by_second = sorted(episodes, key=lambda tup: tup[1])
    
    cur.executemany("insert into series_" + str(seriesNumber) + " values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sorted_by_second)
    con.commit()
    con.close()

#for i in range(1,9+1):
#    createSeriesTable(10, i)


#print(MyPostCommand(False, 'кяввм', 2))
# n = datetime.now()
# print(MyPostCommand(False, '', 1))
# print(MyPostCommand(False, 'стрела', 2))
# print(datetime.now() - n)
# print(MyPostCommand(False, 'подробнее', 3))
# print(datetime.now() - n)
# print(MyPostCommand(False, 'сериал', 4))
# print(datetime.now() - n)

# n = datetime.now()
# print(MyPostCommand(True, '', 1))
# print(MyPostCommand(True, 'твин пикс', 2))
# print(datetime.now() - n)
# print(MyPostCommand(True, 'подробнее', 3))
# print(datetime.now() - n)
# print(MyPostCommand(True, 'сериал', 4))
# print(datetime.now() - n)


#shameless info about episode https://serialium.ru/tv-series/shameless/s8/ https://serialium.ru/tv-series/shameless/s9/
#wild wild country https://en.myshows.me/view/56783/
#Walking dead https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%8D%D0%BF%D0%B8%D0%B7%D0%BE%D0%B4%D0%BE%D0%B2_%D1%82%D0%B5%D0%BB%D0%B5%D1%81%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%B0_%C2%AB%D0%A5%D0%BE%D0%B4%D1%8F%D1%87%D0%B8%D0%B5_%D0%BC%D0%B5%D1%80%D1%82%D0%B2%D0%B5%D1%86%D1%8B%C2%BB

