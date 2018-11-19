# coding: utf-8
# importing the requests library 
import csv
import io
import requests
from datetime import datetime, timedelta
import sqlite3
import datetime
from webparser import *


token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDE5MjgwNTUsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MTg0MTY1NSwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.ad5OITMlYUPviKc_tsM8OhlS77Ji52kDPZJTLezcGGfvdvHbfQv9lpa4yfOhqqSyyMsN7mXCy1VWZyNDxI5kvstnokV172xOlW66l-H-qNrbRbkS1r1bXN-KVl4rRHCVc4jy-COiMkSVNftdNxDDuFEiWF-exntIQVctJvE016tVOFpsYUg42xXOFINHy2uEJ3XrWUjBV5ciJnolWJ1V1Ru-B3lmFTYTpYOTNgFAiTZMqHBwKQs2km49pvG6bIW3naWxlK9srZs692jQqe73GyhZGN95ekt07JabQXrFPOF4pQ2ULd_Eph5U2Lm2_0RgDe594Qfy26ixw63P3Kb9jg'

#QUOTE this string for MySQL
def sqlquote(value):
    if value is None or value == 'None':
         return 'NULL'
    return "'{}'".format(str(value).replace("'", "''"))

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
#tvdbGetSerialInfo(288984)
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
'''
aliases = csv.reader(aliases_in_memory.splitlines(), delimiter='\t')
con.close()
con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cur = con.cursor()

for line in aliases:
    print(line[1])
    cur.execute("INSERT INTO aliases VALUES (?, ?)", line)

con.commit()
con.close()


'''
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

"""
n = datetime.datetime.now()
print(MyPostCommand(False, '', 1))
print(MyPostCommand(False, 'воронины', 2))
print(datetime.datetime.now() - n)
print(MyPostCommand(False, 'подробнее', 3))
print(datetime.datetime.now() - n)
print(MyPostCommand(False, '', 4))
print(datetime.datetime.now() - n)


print(MyPostCommand(True, 'как тебя зовут', 1))
print(MyPostCommand(True, '', 1))
print(MyPostCommand(True, 'воронины', 2))
print(MyPostCommand(False, 'молодежка', 2))
print(MyPostCommand(False, 'простоквашино', 2))
"""

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
def createSeriesTable(seriesNumber, airedSeason):
    #seriesNumber = 10
    # filmID = '296762'
    # airedSeason = 1
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    cmd = 'SELECT tvdbId FROM films WHERE rowid=' + str(seriesNumber)
    cur.execute(cmd)
    filmID = cur.fetchone()
    
    URL = "https://api.thetvdb.com"   
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}  
    PARAMS = {'airedSeason':str(airedSeason)} 
    #Create full request
    URL = URL + '/series/' + str(filmID[0]) + '/episodes/query'
    r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
    dataRu = r.json()
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
    r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
    dataEn = r.json()

    if int(airedSeason) == 1:
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

#films = films_in_memory.splitlines()
#films = csv.reader(films_in_memory.splitlines(), delimiter='\t')\




"""
for i in range(130,137):
    line = films[i].split('\t')
    print(line[0], line[4], line[9])
    for i in range(1,int(line[9])+1):
        createSeriesTable(int(line[0]), i)
"""

def filmdbLastEpisode(filmID):
    cmd = 'SELECT * FROM series_' + str(filmID) +  ' WHERE  firstAired >= date("' + datetime.datetime.today().strftime("%Y-%m-%d") + '")'
    cur.execute(cmd)
    episodeList = cur.fetchall()
    # We have a list of recors, next check the numbers.
    if len(episodeList) == 0:
        #all episodes ended, return the last record from the table
        cmd = 'SELECT * FROM series_' + str(filmID) + ' ORDER BY rowid DESC LIMIT 1'
        cur.execute(cmd)
        episode = cur.fetchone()
        if episode[3] != None:
            name = episode[3]
        else:
            name = episode[2]
        return episode[1], name, episode[4][0:episode[4].index(" ")]
    else:
        #return the first row from the list (couse this is the closest to data issue)
        if episodeList[0][3] != None:
            name = episodeList[0][3] 
        else:
            name = episodeList[0][2] 
        return episodeList[0][1], name, episodeList[0][4][0:episodeList[0][4].index(" ")]

"""
n = datetime.datetime.now()
for i in range(1,30):
    print(filmdbLastEpisode(i))
print(datetime.datetime.now() - n)
"""


"""
print(filmList[1], name, filmList[4])

#episode['airedEpisodeNumber'], episode['episodeName'], episode['firstAired']filmList
#print(MyPostCommand(False, 'кяввм', 2))
n = datetime.datetime.now()
print(MyPostCommand(False, 'ping', 1))
print(MyPostCommand(False, 'стрела', 2))
print(datetime.datetime.now() - n)
print(MyPostCommand(False, 'тбв', 3))
print(datetime.datetime.now() - n)
print(MyPostCommand(False, 'кяввм', 4))
print(MyPostCommand(False, 'атланта', 4))
print(MyPostCommand(False, 'Симпсоны', 4))
print(datetime.datetime.now() - n)


print(MyPostCommand(True, 'как тебя зовут', 1))
"""

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
#14 https://www.amediateka.ru/serial/ubivaya-evu
#15 
#18 http://www.lostfilm.tv/series/Billions/
#26 http://www.lostfilm.tv/series/Animal_Kingdom/seasons/
#27 http://www.lostfilm.tv/series/Gotham/seasons/




#--Input - dict object. 
def addEpisode(seriesNumber, episodeJson, nameEn):
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    sql = 'SELECT airedSeason, airedEpisodeNumber, episodeNameEn, episodeNameRu, firstAired, director, overviewRu, showUrl FROM series_%s WHERE airedSeason = %s AND airedEpisodeNumber = %s' % (str(seriesNumber), str(episodeJson['airedSeason']), str(episodeJson['airedEpisodeNumber']))
    #print(sql)
    #print(str(episodeJson))
    cur = con.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    #rint(row)    
    if row == None:  #No episode - add
        print(nameEn + ' NO EPISODE IN BASE , ADD---------')
        sql = 'INSERT INTO series_%s (airedSeason, airedEpisodeNumber, episodeNameEn, episodeNameRu, firstAired, overviewEn) VALUES (%s, %s, %s, %s, %s, %s)' % (seriesNumber, episodeJson.get('airedSeason'), episodeJson.get('airedEpisodeNumber'), sqlquote(episodeJson.get('episodeNameEn')), sqlquote(episodeJson.get('episodeNameRu')), sqlquote(episodeJson.get('firstAired')), sqlquote(episodeJson.get('overviewEn')))
        print(sql)
        print("\n\n\n")
        cur.execute(sql)
        con.commit()
        con.close()
    else:
        episodeBase = {}
        episodeBase['airedSeason'] = row[0]
        episodeBase['airedEpisodeNumber'] = row[1]
        episodeBase['episodeNameEn'] = row[2]
        episodeBase['episodeNameRu'] = row[3]
        episodeBase['firstAired'] = row[4]
        #print("----------OLD ROW:-----------------")
        #print(str(episodeBase) + ' ' + str(episodeJson))
        change = False
        for key, value in episodeBase.items():
            if (episodeJson.get(key) != None) and ((episodeBase.get(key) == None) or (str(episodeBase.get(key)).rstrip() == "")):
                episodeBase[key] = episodeJson[key]
                change = True
        if change == True:
            print(nameEn + ' CHANGE EXISTED EPISODE------------')
            sql = 'UPDATE series_%i SET episodeNameEn = %s, episodeNameRu = %s, firstAired = %s, overviewEn = %s  WHERE airedSeason = %i AND airedEpisodeNumber = %i' % (seriesNumber, sqlquote(str(episodeBase.get('episodeNameEn'))), sqlquote(str(episodeBase.get('episodeNameRu'))), sqlquote(str(episodeBase.get('firstAired'))), sqlquote(episodeJson.get('overviewEn')), episodeBase.get('airedSeason'), episodeBase.get('airedEpisodeNumber'))
            print(sql)
            print("\n\n\n")
            cur.execute(sql)
            con.commit()
            con.close()


#--Add episodes from dictionary
def addEpsiodesFromDict(seriesNumber, episodes, nameEn):
    print('-----------' + nameEn + '-------------')
    for episode in episodes:
        #print(episode)
        addEpisode(seriesNumber, episode, nameEn)


#add new episodes. withois series numbers - all series. if you need to add particular series - define it in seriesNumber list 
def addNewEpisodesFromURL(seriesNumbers = ""):
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()

    if seriesNumbers == "":
            sql = 'SELECT rowid, nameEn, info, showURL  FROM films WHERE showURL is not NULL AND showURL <> ""'
            cur.execute(sql)
            films = cur.fetchall()
            f = open('testadd.txt', 'w')
            for line in films:
                seriesNumber = line[0]
                nameEn = line[1]  #not neccessary, but please don't delete (for future tests)
                source = line[2]
                showURL = line[3]
                if source == "tvguide":
                    episodes = getEpisodesInfoFromTvGuide(showURL)
                    #print("-----------NEW SERIES-----------" + nameEn)
                    #print('-------------nameEn-------------')
                    f.write(nameEn + "\n")  
                    f.write(str(episodes)) 
                    f.write("\n")
                addEpsiodesFromDict(seriesNumber, episodes, nameEn)
                    
    else: 
        for seriesNumber in seriesNumbers:
            sql = 'SELECT rowid, nameEn, info, showURL  FROM films WHERE rowid = %i AND showURL is not NULL AND showURL <> ""' % seriesNumber
            cur.execute(sql)
            line = cur.fetchone()
            nameEn = line[1]
            source = line[2]
            showURL = line[3]
            
            if source == "tvguide":
                print(showURL)
                episodes = getEpisodesInfoFromTvGuide(showURL)
            addEpsiodesFromDict(seriesNumber, episodes, nameEn)

def getEpisodesInfoFromTvGuide():
    

print(getEpisodesInfoFromTvGuide("https://www.tvguide.com/tvshows/south-park/episodes/100402/"))
#{'episodeNameEn': 'Nobody Got Cereal?', 'airedSeason': '22', 'airedEpisodeNumber': '7', 'firstAired': '2018-11-14 00:00:00', 'overviewEn': 'The boys break out of jail but are on the run from the police and ManBearPig.'},

#addNewEpisodesFromURL()
#addNewEpisodesFromURL([1, 34])