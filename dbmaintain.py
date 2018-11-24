# coding: utf-8
import requests
import sqlite3
import datetime

token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDMxNDM1NzEsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MzA1NzE3MSwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.yPxza7OAS58U_ehnK5RrMSDTptJ6jt3XyAx_qTsLRNHA-Y_7yVdaMiy61qMMBBvQHj_KdXUk0iO_-W0DRHEd6gH9ODedjWa5eov3X3Tdg2x0fh8eslP2CuXecrJfipdRYxluHPfr0erJIZun14y6OJ9vR7CeriDD6tnVN68pQpRbvJm5RYd2uPCKdxiXy-VzmmASnCoo7JR3CXTP1WvTGMhNp5Z5coFgO5zbwjv0bs8sdU71wlC1JqPlTnPra-3pamoET4hgVvfGbEAHY-4HqspzK8UAUTr3UywVOfDSLTYe0ZCD02i9ncaTQ6ohtVtuskF7HoeKVX0_R8y1djsGtQ'
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

def addSerialIntoDB(filmID):
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    #check we do not have such film in the list
    resutl = (cur.execute('SELECT rowid FROM films WHERE tvdbid=?', (str(filmID),))).fetchone()
    con.close()
    if resutl != None:
        print('This film ID', str(filmID), 'is already in the DB. Exit.')
        return
    
    #Create a web-request
    URL = "https://api.thetvdb.com"    
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)} 
    URL1 = URL + '/series/' + str(filmID)
    r = requests.get(url = URL1, headers = HEADERS)  
    # extracting data in json format 
    dataEn = r.json()
    if 'Error' in dataEn:
        #there is an error
        if 'No results for your query' in dataEn['Error']:
            return 'Error', 'Search error'
        if dataEn['Error'] == 'Not authorized':
            #try update token
            tockenRefresh()
            print(token)
            if token == '0':
                return 'Error', 'Auth error and update token error'
            HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
            r = requests.get(url = URL1, headers = HEADERS)
            dataEn = r.json()
            if 'Error' in dataEn:
                return 'Error', 'Error token update'
    #collect Rus Name
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}
    r = requests.get(url = URL1, headers = HEADERS)
    dataRu = r.json()
    #find the last season number in Eng verson
    URL2 = URL + '/series/' + str(filmID) + '/episodes/summary'
    r = requests.get(url = URL2, headers = HEADERS)
    dataSum = r.json()

    lastSeason = max(map(int, dataSum['data']['airedSeasons']))    
    if dataEn['data']['firstAired'] != None and dataEn['data']['firstAired'] != '':
        firstAired = datetime.datetime.strptime(dataEn['data']['firstAired'], '%Y-%m-%d')
    else:
        firstAired = None
        print("!Update first arride in the DB manually")
    #summ result in the finnal line
    fields = [(dataEn['data']['id']),
        dataEn['data']['imdbId'],
        None,
        dataEn['data']['seriesName'],
        dataRu['data']['seriesName'],
        dataEn['data']['status'],
        firstAired,
        dataEn['data']['network'],
        int(lastSeason),
        int(dataSum['data']['airedEpisodes']),
        float(dataEn['data']['siteRating']),
        0,
        None,
        None,
        None,
        None,
        None,
        0,
        ]
    #add info into the database
    print("Record basic info into the film DB")
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    cur.execute("INSERT INTO films VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", fields)
    seriesNumber = cur.lastrowid
    #Add aliases info
    aliases = []
    if dataRu['data']['seriesName'] != None:
        cur.execute("INSERT INTO aliases VALUES (?, ?)", [str(seriesNumber), dataRu['data']['seriesName'].lower(),])
        print("Add alias", dataRu['data']['seriesName'])
    if dataEn['data']['seriesName'] != None:
        cur.execute("INSERT INTO aliases VALUES (?, ?)", [str(seriesNumber), dataEn['data']['seriesName'].lower(),])
        print("Add alias", dataEn['data']['seriesName'])
    #create a corresponding table for the serial
    
    print("Create a corresponding table", str(seriesNumber))
    for seasonNumber in range(1, int(lastSeason)+1):
        if int(seasonNumber) == 1:
            #clean up
            cmd = 'DROP TABLE IF EXISTS series_' + str(seriesNumber)
            cur.execute(cmd)
            cmd = '''CREATE TABLE series_''' + str(seriesNumber) + '''
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
        HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}  
        PARAMS = {'airedSeason':str(seasonNumber)} 
        #Create full request
        URL4 = URL + '/series/' + str(filmID) + '/episodes/query'
        r = requests.get(url = URL4, headers = HEADERS, params = PARAMS)
        dataRu = r.json()
        HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
        r = requests.get(url = URL4, headers = HEADERS, params = PARAMS)
        dataEn = r.json()

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
        print("Save result about season", str(seasonNumber))
        #sort results by series ID
        sorted_by_second = sorted(episodes, key=lambda tup: tup[1])
        cur.executemany("INSERT INTO series_" + str(seriesNumber) + " values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sorted_by_second)
    #save results
    con.commit()
    con.close()

def addQuote(text):
    if text == None or text == '':
        print("Nothing to add")
        return 0
    
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    cur.execute("INSERT INTO quotes VALUES (?)", (str(text),))
    rowId = cur.lastrowid
    con.commit()
    con.close()
    print ("Line number", rowId)

def addFact(text):
    if text == None or text == '':
        print("Nothing to add")
        return 0    
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    cur.execute("INSERT INTO facts VALUES (?)", (str(text),))
    rowId = cur.lastrowid
    con.commit()
    con.close()
    print ("Line number", rowId)

#Record serial into the db. Add into films, create a series table + add aliases
addSerialIntoDB(73739)
#addQuote('test')
#addFact('test')


