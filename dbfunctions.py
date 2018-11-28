# coding: utf-8
# function module
import csv
import io
import requests
import random
import sqlite3
from datetime import datetime, timedelta, time
import pymorphy2
from difflib import SequenceMatcher
from dialogs import *
from webparser import *

#token var
token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDM0Mzc0MTQsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MzM1MTAxNCwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.sSkgZUo5FVMUUSpJ4soDv90FL2mSVCsZPg08V_tuyszojY_tWw1RULQlijeU4KW4F0Re5HAlJ1ratVekfCNupJyRdMcucYeoZlJXRBCUYxtE5Mm6AyzC-Q4RGg6ViE595mPQqDdnp-2r-e_XZee-NdPijT4rWtoZEZUY1G1Ja3FDrU5jCVMoJTLYC7qQa0INwkvodhBMKphfh1UPHRD1OT6a7Y-OPGX0vuNKQNGwWPQeuY3PPUIFZizc87yKLt1oHmsIQcO50Tucr4FZQzkcRGl2vlrlsbO_JfV3GXF9V_9_ngNbQ7RJ7CQTNQeypk0tA158r0R848Gu2XjJZdxAKQ'
ActionKeyWords = {
        'когда': 0, 'кагда': 0, 'when': 0, 'скоро': 0,
        'где': 1,
        'info': 2, 'инфо': 2, 'информация': 2, 'подробнее': 2, 'подробно': 2,
        'цитата': 3, 'цититу':3, 'цитируй':3, 'процитируй':3,
        'факт': 4, 'факты':4, 'фактик': 4, 'fuck':4,
        'посмотреть': 5, 'глянуть': 5,
    }
TimeKeyWords = {
        'следующий': 2, 'следующая': 2, 'новый': 2, 'новая': 2, 'очередной': 2, 'очередная': 2, 'очередные': 2, 'будет': 2, 'появится': 2, 'выйдет': 2, "выходит": 2,
        'идет': 1, 'проходит': 1, 'показывают': 1, 'крутят': 1,
        'была': 0, 'прошла': 0, 'показали': 0, 'крутили': 0, 'прошлая': 0, 'прошедшая': 0, 'предыдущий': 0, 'предыдущая': 0,
    }
OffensiveWords = (
    'хуй','пизда','пиздец','ссука','хуйло','хуило','заебал','нахуй','на хуй','пиздуй','блядь',
)

#storage for chash
cashRequests = {}
#read all aliases at start
con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cur = con.cursor()
#read all aliases into memory
cmd = 'SELECT * FROM aliases'
cur.execute(cmd)
aliases_in_memory = cur.fetchall()
#read all films into memory
cmd = 'SELECT * FROM films'
cur.execute(cmd)
films_in_memory = cur.fetchall()
#
con.close()
#
morph = pymorphy2.MorphAnalyzer()

#--SQL quote for SQL query
def sqlquote(value):
    if value is None or value == 'None':
         return 'NULL'
    return "'{}'".format(str(value).replace("'", "''"))

# Get Normalized name
def get_normalized_string(string):
    list_words = string.split()
    normal_list = []
    for word in list_words:
        normal_word = morph.parse(word)[0].normal_form
        normal_list.append(normal_word)
    return normal_list

# Check name with typo mistakes
def compare_strings_typo(string1, string2):
    similarity = SequenceMatcher(None, string1, string2)
    return similarity.ratio() * 100

# Compare two strings
def compare_names(name1, name2):
    set1 = set(get_normalized_string(name1))
    set2 = set(get_normalized_string(name2))
    overlap = set1 & set2

    percentage = round(compare_strings_typo(name1, name2))
    if percentage > 80:
        print('Вы сравнивали: ' + name1 + '|' + name2 + ', идентичность: ' + str(
            percentage) + '%(найдено через typo)')
    else:
        percentage = round((len(overlap) / max(len(set1), len(set2))) * 100)
        if percentage > 80:
            print('Вы сравнивали: ' + name1 + '|' + name2 + ', общее: ' + str(overlap) + ', идентичность: ' + str(
                percentage) + '%(найдено через normalized)')
    return round(percentage)

def SearchName(text):
    result = {'filmId':-1,'action':-1,'time':-1,}
    text = text.lower()
    words = text.split(" ")
    WordList = []
    SerialName = []
    for word in words:
        if len(word.strip(' ?!,;:.')) > 1:
            WordList.append(word.strip(' ?!,;:.'))
    #Check offenceive words
    for word in WordList:
        if word in OffensiveWords:
            #do not spend time for search, return nothing
            return result
    #Check Action KeyWord
    for word in WordList:
        if word in ActionKeyWords.keys():
            if result['action'] == -1:
                #record only first one
                result['action'] = ActionKeyWords[word]
        elif word in TimeKeyWords.keys():
            if result['time'] == -1:
                #record only first one
                result['time'] = TimeKeyWords[word]
        else:
            #save results in a separate list for further seach action
            SerialName.append(word)
    #Check aliases
    for alias in aliases_in_memory:
        #print(row)
        filmName = ""
        for word in SerialName:
            if word in alias[1]:
                filmName += word + " "
        if filmName[:-1] == alias[1]:
            #Remove last space and check for 100% consistency
            result['filmId'] = alias[0]
            return result

    #Failover to polimorhp check
    SerialNameText = ' '.join([str(e) for e in SerialName])
    for alias in aliases_in_memory:
        if compare_names(SerialNameText, alias[1]) > 80:
            result['filmId'] = alias[0]
            return result

    #Return null result
    return result


#update token
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

#seach function in the tbdb
def tvdbEpisodesFromLastSeason(filmID):
    # global cashRequests
    # if filmID in cashRequests:
    #      if cashRequests[filmID][0] > (datetime.now() - timedelta(hours=8)):
    #          #We have cash with less thatn 8 hours resutls, Return resutls from the chash
    #          return cashRequests[filmID][1], cashRequests[filmID][2], cashRequests[filmID][3]
    # #filmID = '80379'
    # #seasonNumber = '12'
    URL = "https://api.thetvdb.com"
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
    URL1 = URL + '/series/' + str(filmID) + '/episodes/summary'
    try:
        r = requests.get(url = URL1, headers = HEADERS)
    except:
        return 'Error', 'Connection error'

    dataSum = r.json()
    if 'Error' in dataSum:
        #there is an error
        if 'No results for your query' in dataSum['Error']:
            return 'Error', 'Search error'
        if dataSum['Error'] == 'Not authorized':
            #try update token
            tockenRefresh()
            print(token)
            if token == '0':
                return 'Error', 'Auth error and update token error'
            HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
            r = requests.get(url = URL1, headers = HEADERS)
            dataSum = r.json()
            if 'Error' in dataSum:
                return 'Error', 'Error token update'
    #Get the last season information.
    lastSeason = max(map(int, dataSum['data']['airedSeasons']))

    #Collect information about the last season
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}
    PARAMS = {'airedSeason':str(lastSeason)}
    #Create full request
    URL2 = URL + '/series/' + str(filmID) + '/episodes/query'
    r = requests.get(url = URL2, headers = HEADERS, params = PARAMS)
    dataRu = r.json()
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
    r = requests.get(url = URL2, headers = HEADERS, params = PARAMS)
    dataEn = r.json()
    #Genrate a new episodes list
    episodes = []
    for i in range(len(dataEn['data'])):
        if dataEn['data'][i]['firstAired'] != '':
            data = dataEn['data'][i]['firstAired'] + ' 00:00:00'
        elif dataRu['data'][i]['firstAired'] != '':
            data = dataRu['data'][i]['firstAired'] + ' 00:00:00'
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
    return sorted_by_second

#--Input - dict object.
def addEpisode(seriesNumber, episode):
    #print(seriesNumber)
    airedSeason = episode[0]
    airedEpisodeNumber = episode[1]
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    sql = 'SELECT * FROM series_%s WHERE airedSeason = %s AND airedEpisodeNumber = %s' % (str(seriesNumber), str(airedSeason), str(airedEpisodeNumber))
    cur.execute(sql)
    row = cur.fetchone()
    if row == episode:
        #they are equal, nothing to change
        return
    else:
        #There is difference
        if row == None:
            #No data in the DB, insert a new episode
            cur.execute("INSERT INTO series_" + str(seriesNumber) + " values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", episode)
            con.commit()
            print(seriesNumber, 'New line!')
        else:
            #it is not a none value, need to compare and update null values.
            episodeValues = []
            update = False
            for i in range(len(row)):
                #if not same
                if row[i] != episode[i]:
                    if row[i] == None or row[i] == '':
                        #If there is nothing, recorded into the feild.
                        episodeValues.append(episode[i])
                        update = True
                        #print('update', episode[i])
                    elif episode[i] == None or episode[i] == '':
                        #We have someghin in DB but the TVDB returns null
                        episodeValues.append(row[i])
                    else:
                        #There is something, and episode have someting. Manual check should be performed
                        episodeValues.append(episode[i])
                        print('old', row[i],)
                        print('new', episode[i],)
                        update = True
                else:
                    #Same values, append only data from DB
                    episodeValues.append(row[i])
            if update:
                #if we have something to update than update DB, if we have null values in update than skip these steps
                sql = '''UPDATE series_%i SET episodeNameEn = ?, episodeNameRu = ?, firstAired = ?, director = ?, overviewEn = ?, overviewRu = ?, showUrl = ?, info = ? WHERE airedSeason = %i AND airedEpisodeNumber = %i''' % (int(seriesNumber), airedSeason, row[1])
                cur.execute(sql, episodeValues[2:])
                con.commit()
                print(seriesNumber, 'update')
    con.close()


#add new episodes. withois series numbers - all series. if you need to add particular series - define it in seriesNumber list
def addNewEpisodesFromURL(seriesNumber):
    #--Get series from TVDB
    if seriesNumber == None or seriesNumber == 0:
        return 0, 'Nothing'
    #Collect tvdbID form the fims table
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    resutl = (cur.execute('SELECT tvdbid, status FROM films WHERE rowid=?', (str(seriesNumber),))).fetchone()
    #con.close()
    #Collect episodes about last
    if resutl[1] == 'Ended':
        return 0, 'Ended'
    #collect information form the TVdb in sorted man
    episodes = tvdbEpisodesFromLastSeason(resutl[0])
    for episode in episodes:
        addEpisode(seriesNumber, episode)

    #--Get series from other sources
    sql = 'SELECT rowid, nameEn, searchURL FROM films WHERE rowid = %i AND searchURL is not NULL AND searchURL <> ""' % seriesNumber
    cur.execute(sql)
    line = cur.fetchone()
    if line != None:
        nameEn = line[1]
        searchURL = line[2]
        if "tvguide.com" in searchURL:
            print(nameEn + ' ' + searchURL)
            episodes = getEpisodesInfoFromTvGuide(searchURL)
            for episode in episodes:
                addEpisodeFromDict(seriesNumber, episode, nameEn)
        return 1


def addEpisodeFromDict(seriesNumber, episodeJson, nameEn):
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    sql = 'SELECT airedSeason, airedEpisodeNumber, episodeNameEn, episodeNameRu, firstAired, director, overviewRu FROM series_%s WHERE airedSeason = %s AND airedEpisodeNumber = %s' % (str(seriesNumber), str(episodeJson['airedSeason']), str(episodeJson['airedEpisodeNumber']))
    #print(sql)
    #print(str(episodeJson))
    cur = con.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    #print(nameEn)
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
            print (("%s %i %i CHANGED WITH TVGUIDE INFO") % (nameEn, episodeBase.get('airedSeason'), episodeBase.get('airedEpisodeNumber')))
            sql = 'UPDATE series_%i SET episodeNameEn = %s, episodeNameRu = %s, firstAired = %s, overviewEn = %s  WHERE airedSeason = %i AND airedEpisodeNumber = %i' % (seriesNumber, sqlquote(str(episodeBase.get('episodeNameEn'))), sqlquote(str(episodeBase.get('episodeNameRu'))), sqlquote(str(episodeBase.get('firstAired'))), sqlquote(episodeJson.get('overviewEn')), episodeBase.get('airedSeason'), episodeBase.get('airedEpisodeNumber'))
            print(sql)
            print("\n\n\n")
            cur.execute(sql)
            con.commit()
            con.close()
        else:
            #print (('%s %i %i NO NEW INFO FROM TVGUIDE') % (nameEn, episodeBase.get('airedSeason'), episodeBase.get('airedEpisodeNumber')))
            pass


#get neccessary column from film table
def getInfoFromFilm(filmId, column="nameEn"):
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    cmd = 'SELECT %s FROM films WHERE rowid = %i' % (column, filmId)
    cur.execute(cmd)
    return cur.fetchone()[0]


def filmdbLastEpisode(filmID):
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    cmd = 'SELECT * FROM series_' + str(filmID) +  ' WHERE  firstAired >= date("' + datetime.today().strftime("%Y-%m-%d") + '")'
    cur.execute(cmd)
    episodeList = cur.fetchall()
    # We have a list of recors, next check the numbers.
    if len(episodeList) == 0:
        #all episodes ended, return the last record from the table
        cmd = 'SELECT * FROM series_' + str(filmID) + ' ORDER BY rowid DESC LIMIT 1'
        cur.execute(cmd)
        episode = cur.fetchone()
        #print(episode)
        if episode[3] != None:
            name = episode[3]
        else:
            name = episode[2]

        if episode[4] != None:
            arrival = episode[4][0:episode[4].index(" ")]
        else:
            arrival = None

        return episode[0], episode[1], name, arrival
    else:
        #return the first row from the list (couse this is the closest to data issue)
        if episodeList[0][3] != None:
            name = episodeList[0][3]
        else:
            name = episodeList[0][2]
        if episodeList[0][4] != None:
            arrival = episodeList[0][4][0:episodeList[0][4].index(" ")]
        else:
            arrival = None

        return episodeList[0][0], episodeList[0][1], name, arrival
    con.close()

#tvdbLastEpisode('80379','12')
#Return the URL to the offical site
def OfficialURL(intId):
    if (intId == None) or (intId < 1):
         return str('https://www.yandex.ru/')
    film = films_in_memory[intId - 1]
    if (film[14] != None) and (film[14].rstrip() != ""):
        return film[14]
    else:
        return str('https://yandex.ru/search/?text=сериал%20' + film[4].replace(" ","%20").strip(' ?!,;:.'))


#Return main info about serial
def getFilmInfoLocal(filmId):
    #all films are in memory. filmID will be -1 to the memory list becouse it starts form 0
    film = films_in_memory[filmId-1]
    #
    msg = 'Сериал "' + film[4] + '" (' + film[3] + ') впервые вышел в прокат ' + datetime.strftime(datetime.strptime(film[6], '%Y-%m-%d %H:%M:%S'), '%d.%m.%Y') + ' на канале ' + film[7] + '.'
    if film[8] == 1:
        msg += ' В сериале только 1 сезон и ' + str(film[9]) + ' серий.'
    elif film[8] < 5:
        msg += ' В сериале ' + str(film[8]) + ' сезонa и ' + str(film[9]) + ' серий.'
    else:
        msg += ' В сериале ' + str(film[8]) + ' сезонoв и ' + str(film[9]) + ' серий.'
    msg += ' IMDB рейтинг ' + str(film[10]) + '.'
    if film[5].lower() == 'continuing':
        variants = ['Продолжает сниматься.','Сьемки сериала продолжаются и по сей день.','Ждите новых серий.','Сьемочная группа работает над выпуском новых серий.']
        msg += ' ' + random.choice(variants)
    else:
        variants = ['Сьемки сериала завершены.','Серии более не выпускаются.','Сериал закончен.','Выпуск новых серий и сезонов не планируется.']
        msg += ' ' + random.choice(variants)
    return msg


#Return film location
def getFilmLocationLocal(filmId):
    return "Сериал можно посмотреть на сайте " + OfficialURL(filmId)


#Film Search function
def filmSearch(filmId, action, time):
    #print(id, action, time)
    #action
    #  0 - looking for a time period
    #  1 - looking for where
    #time
    #  0 - past
    #  1 - current
    #  2 - future
    seasonName = ["","первого","второго","третьего","четвертого","пятого","шестого","седьмого","восьмого","девятого","десятого",
        "одиннадцатого","двенадцатого","тринадцатого","четырнадцатого","пятнадцатого","шестнадцатого","семнадцатого","восемнадцатого","девятнадцатого","двадцатого",
        "двадцать первого","двадцать второго","двадцать третьего","двадцать четвертого","двадцать пятого","двадцать шестого",'двадцать седьмого','двадцать восьмого','двадцать девятого','тридцатого',
        'тридцать первого','тридцать второго','тридцать третьего','тридцать четвертого','тридцать пятого', 'тридцать шестого',]
    #seasonName2 = ['','первая','вторая','третья','четвертая','пятая','шестая','седьмая','восьмая','девятая','десятая',
    #    'одиннадцатая','двенадцатая','тринадцатая','четырнадцатая','пятнадцатая','шеснадцатая','семнадцатая','восемнадцатая','девятнадцатая','двадцатая',
    #    'двадцать первая','двадцать вторая','двадцать третья','двадцать четвертая','двадцать пятая','двадцать шестая','двадцать седьмая','двадцать восьмая','двадцать девятая', 'тридцатая'
    #    'тридцать первая','тридцать вторая','тридцать третья','тридцать четвертая','тридцать пятая','тридцать шестая','тридцать седьмая','тридцать восьмая','тридцать девятая', 'тридцатая',
    #    ]
    #all films are in memory. filmID will be -1 to the memory list becouse it starts form 0
    film = films_in_memory[filmId-1]
    if action == 1:
        #looking for information about location for watching
        return getFilmLocationLocal(filmId)
    if action == 2:
        #looking for additional info in local file
        return getFilmInfoLocal(filmId)
    if action == 3:
        #action to return quote
        return getRandomQuote()
    if action == 4:
        #action to return fact
        return getRandomFact()
    if action == 0 or action == -1:
        #question about time, looking for corresponding data, accept default action
        tvdbanswer = filmdbLastEpisode(filmId)
        if(film[5] == 'Ended'):
            #This serial is ended, return message with search ID
            variants = ['Этот сериал завершен.','К сожалению, этот сериал завершен.','Сериал более не выпускается.','Сериал закончен.']
            variants2 = ['Последняя серия под номером','Последняя серия с номером','Заключительная серия номер ','Завершающая серия под номером']
            return random.choice(variants) + ' ' +  random.choice(variants2) + ' ' + str(tvdbanswer[1]) + ' "' + tvdbanswer[2] + '" ' + seasonName[tvdbanswer[0]] + ' cезона вышла в прокат ' + datetime.strftime(datetime.strptime(tvdbanswer[3], '%Y-%m-%d'), '%d.%m.%Y')

        if tvdbanswer[3] == '2100-01-01' or tvdbanswer[3] == '' or tvdbanswer[3] == None:
            return "Съемки сериала ведутся, но дата выхода следующей серии еще не анонсирована. Попробуйте спросить позднее."

        d = datetime.strptime(tvdbanswer[3], '%Y-%m-%d')
        n = datetime.now()
        nowday = datetime(n.year, n.month, n.day)
        buzz = film[16]

        if d > nowday:
            if tvdbanswer[2] == None:
                return "Серия " + str(tvdbanswer[1]) + " " + seasonName[tvdbanswer[0]] + ' cезона ' + tellWillBeAired() + ' ' + datetime.strftime(d, '%d.%m.%Y')
            else:
                return "Серия " + str(tvdbanswer[1]) + " " + seasonName[tvdbanswer[0]] + ' cезона "' + tvdbanswer[2] + '" ' + tellWillBeAired() +' ' + datetime.strftime(d, '%d.%m.%Y')
            #return random.choice(variants), int(intId)
        elif d == nowday:
            #it is today
            if tvdbanswer[2] == None:
                return "Серия " + str(tvdbanswer[1]) + " " + seasonName[tvdbanswer[0]] + ' cезона ' + tellWillBeAired() + ' сегодня!'
            else:
                return "Серия " + str(tvdbanswer[1]) + " " + seasonName[tvdbanswer[0]] + ' cезона "' + tvdbanswer[2] + '" ' + tellWillBeAired() + ' сегодня!'
        else:
            if (buzz != None) and (buzz.rstrip() != ""):   #if buzz exist
                if tvdbanswer[2] == None:
                    return '%s серия %s сезона %s %s. %s' % (tellTheLast(), seasonName[tvdbanswer[0]], tellAlreadyAired(), datetime.strftime(d, '%d.%m.%Y'), buzz)
                else:
                    return '%s серия %s сезона %s %s %s. %s' % (tellTheLast(), seasonName[tvdbanswer[0]], tvdbanswer[2], tellAlreadyAired(), datetime.strftime(d, '%d.%m.%Y'), buzz)
            else:
                #it was in a past
                if tvdbanswer[2] == None:
                    return "Серия " + str(tvdbanswer[1]) + " " + seasonName[tvdbanswer[0]] + ' cезона ' + tellAlreadyAired() + ' ' + datetime.strftime(d, '%d.%m.%Y')
                else:
                    return "Серия " + str(tvdbanswer[1]) + " " + seasonName[tvdbanswer[0]] + ' cезона "' + tvdbanswer[2] + '" ' + tellAlreadyAired() + ' ' + datetime.strftime(d, '%d.%m.%Y')
    #final close return (if everythig esle bad)
    return tellIAmSorry() + ' ' + tellICantFindTheEpisode()
#main function, check for key words and finnaly execute a
def CoreSearch(text):
    result = {'responce':'','filmId':-1, 'img':''}
    #looking for a name (fist stage)
    SearchResult = SearchName(text)
    if SearchResult['filmId'] == -1:
        if SearchResult['action'] == 5:
            #No film but want to wathc, probably query what i can watch?
            result['responce'] = tellSuggestionToWathc()
            result['filmId'] = 0
        #we did not find a film, return default
        return result

    #Run the filmSearch function on top of film ID and rerutn text in result
    result['responce'] = filmSearch(SearchResult['filmId'], SearchResult['action'], SearchResult['time'])
    result['filmId'] = SearchResult['filmId']
    imgsRaw = films_in_memory[int(SearchResult['filmId'])-1][12]
    if not ((imgsRaw == '') or (imgsRaw == None)):
        imgs = imgsRaw.split(',')
        result['img'] = random.choice(imgs)
    return result



def addSerialIntoDB(filmID):
    responce = []
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    #check we do not have such film in the list
    resutl = (cur.execute('SELECT rowid FROM films WHERE tvdbid=?', (str(filmID),))).fetchone()
    con.close()
    if resutl != None:
        responce.append('This film ID ' + str(filmID) + ' is already in the DB. Exit.')
        return responce
    
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
                return responce.append('Error token update')
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
        responce.append("!Update first arride in the DB manually")
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
        ]
    #add info into the database
    print("Record basic info into the film DB")
    con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = con.cursor()
    cur.execute("INSERT INTO films VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", fields)
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
        responce.append("Season " + str(seasonNumber))
        #sort results by series ID
        sorted_by_second = sorted(episodes, key=lambda tup: tup[1])
        cur.executemany("INSERT INTO series_" + str(seriesNumber) + " values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sorted_by_second)
    #save results
    con.commit()
    con.close()
    return responce


#addNewEpisodesFromURL(7)
# for i in range(len(films_in_memory)+1):
#    addNewEpisodesFromURL(i)

#addNewEpisodesFromURL(1)

print(len(aliases_in_memory),'aliases and', len(films_in_memory), 'serials have been loaded successfully')


#print(SearchName("33 несчастья"))
# print(SeachActionTimeDetection("ГДs сока сколь;в ы новый когда же ты где?"))
# print(CoreSearch("ГДs сока сколь;в ы когда же ты где?"))
print(CoreSearch("Твин Пикс"))
print(CoreSearch("Теория большого взрыва"))
# print(CoreSearch("друзья"))
# print(CoreSearch("дай инфо о теории большого взрыва"))
# print(CoreSearch("где глянуть теорию большого взрыва"))
# print(CoreSearch("новая серия грифинов"))
#print(CoreSearch("свежая серия полицейского с рублевки"))
# print(CoreSearch("доктор хаус"))
# print(CoreSearch("кяввм"))
#print(CoreSearch("эртугрул"))
