# coding: utf-8
# function module
import csv
import io
import requests
import random
import sqlite3
from datetime import datetime, timedelta
import pymorphy2
from difflib import SequenceMatcher
#marker
token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDE5MjcwMzMsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MTg0MDYzMywidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.paXoQofY18DGeu-8AnzcPtxKWH0BMaG-VUFM5DEEXi_aEwqhhYYQbqk5_Mqrkw-elR8JNvQMjwmC0Fi78GsMWGfKIqb4Nqol-X1bLu9sLIkzU96NkuUnscj3FTTGrcMx_6-f9dMaxfli0aasqJX99FEOrDm2FwF1v8orcAaEDGn2hFbYeFY_5pLlKfeJbhwcdKalCCyuhTu9M5fSdOudCAraacH7eGgfPXO9Q9BxEzqPEbNSmoGeHxd4GX6lKB7cV7AKjX_9CecoyVCKaIOUgQK3ebARs6f2uyRh3yrA6NtNgLKt6OusjC9B91u_WupOfDoTFO-tIWS9aG2zjBKf4w'
#storage for chash
cashRequests = {}
#read files on start
with open('NameVariations.csv', mode="r", encoding="utf-8") as file:
    aliases_in_memory = file.read()

with open('films.csv', mode="r", encoding="utf-8") as file:
    films_in_memory = file.read()

morph = pymorphy2.MorphAnalyzer()

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
    text = text.lower()
    words = text.split(" ")
    wordList = []
    for word in words:
        if len(word.strip(' ?!,;:')) > 1:
            wordList.append(word.strip(' ?!,;:'))
    filmReader = csv.reader(aliases_in_memory.splitlines(), delimiter='\t')
    #Check aliases
    for row in filmReader:
        #print(row)
        filmName = ""
        for word in wordList:
            if word in row[1]:
                filmName += word + " "
        if filmName[:-1] == row[1]:
            #Remove last space and check for 100% consistency
            return row[0]
    
    #Failover to polimorhp check
    #f = open('NameVariations.csv', mode="r", encoding="utf-8")
    #filmReader = csv.reader(f, delimiter='\t')
    filmReader = csv.reader(aliases_in_memory.splitlines(), delimiter='\t')   
    for row in filmReader:
        if compare_names(text, row[1]) > 80:
            return row[0]
    #Return noting
    return -1

#get_normalized_string('воронины')
#compare_names(text, 'ворниной')

#Looking for key words related to action
#time 0, plase 1, info 2, else -1
def SearchAction(text):
    KeyWords = {
        'когда': 0, 'кагда': 0, 'when': 0, 'скоро': 0,
        'где': 1,
        'info': 2, 'инфо': 2, 'информация': 2, 'подробнее': 2, 'подробно': 2,
    }
    text = text.lower()    
    WordList = text.split(" ")
    for word in WordList:
        word = word.strip(" ?!,;:")
        if word in KeyWords.keys():
            return KeyWords[word]
    return -1
#Looking for key words related to time
#future 2, present 1 and past 0, else -1
def SeachActionTimeDetection(text):
    TimeWords = {
        'следующий': 2, 'следующая': 2, 'новый': 2, 'новая': 2, 'очередной': 2, 'очередная': 2, 'очередные': 2, 'будет': 2, 'появится': 2, 'выйдет': 2, "выходит": 2,
        'идет': 1, 'проходит': 1, 'показывают': 1, 'крутят': 1,
        'была': 0, 'прошла': 0, 'показали': 0, 'крутили': 0, 'прошлая': 0, 'прошедшая': 0, 'предыдущий': 0, 'предыдущая': 0,
    }
    text = text.lower()    
    WordList = text.split(" ")
    for word in WordList:
        word = word.strip(" ?!,;:")
        if word in TimeWords.keys():
            return TimeWords[word]
    return -1 
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
def tvdbLastEpisode(filmID, seasonNumber):
    global cashRequests
    if filmID in cashRequests:         
         if cashRequests[filmID][0] > (datetime.now() - timedelta(hours=8)):
             #We have cash with less thatn 8 hours resutls, Return resutls from the chash
             return cashRequests[filmID][1], cashRequests[filmID][2], cashRequests[filmID][3]
    #filmID = '80379'
    #seasonNumber = '12'
    URL = "https://api.thetvdb.com"   
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}  
    PARAMS = {'airedSeason':seasonNumber} 
    #Create full request
    URL = URL + '/series/' + filmID + '/episodes/query'
    #r = requests.get(url = URL, headers = HEADERS, params = PARAMS)    
    try:
        r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
    except:
        return 'Error', 'Connection error'

    # extracting data in json format 
    data = r.json()
    #print(data)
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
            HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}
            r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
            data = r.json()
            if 'Error' in data:
                return 'Error', 'Error token update'
    #looking for the last episod in the seies
    lastEpisode = 1
    for series in data['data']:
        if int(series['airedEpisodeNumber']) > lastEpisode:
            lastEpisode = int(series['airedEpisodeNumber'])
            episode = series

    if episode['episodeName'] == None:
        #if there is no Rus name, repeat in En
        HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
        r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
        data = r.json()
        #looking for the last episod in the seies
        lastEpisode = 1
        for series in data['data']:
            if int(series['airedEpisodeNumber']) > lastEpisode:
                lastEpisode = int(series['airedEpisodeNumber'])
                episode = series
    #save information into the cash
    
    cashRequests[filmID] = [datetime.now(), str(episode['airedEpisodeNumber']), episode['episodeName'], str(episode['firstAired']),]
    return episode['airedEpisodeNumber'], episode['episodeName'], episode['firstAired']


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
    con.close()


#tvdbLastEpisode('80379','12')
#Return the URL to the offical site 
def OfficialURL(intId):
    URLs = {
        'CBS': 'https://www.cbs.com',
        'CBS All Access': 'https://www.cbs.com',
        'Comedy Central (US)': 'https://www.cc.com',
        'Crackle': 'https://www.sonycrackle.com',
        'CW Seed': 'https://www.cwseed.com',
        'DC Universe': 'https://www.dcuniverse.com',
        'Disney Channel (US)': 'https://shows.disney.com',
        'Disney XD': 'https://shows.disney.com',
        'FOX (US)': 'https://www.fox.com',
        'FX (US)': 'https://www.fxnetworks.com',
        'FXX': 'https://www.fxnetworks.com',
        'HBO': 'https://www.hbogo.com',
        'History': 'https://www.history.com',
        'Hulu': 'https://www.hulu.com',
        'ITV Encore': 'https://www.itv.com',
        'NBC':  'https://www.nbc.com',
        'Netflix': 'https://www.netflix.com',             
        'Showtime': 'https://www.sho.com',
        'Sony Crackle': 'https://www.sonycrackle.com',
        'Starz!': 'https://www.starz.com',
        'Syfy': 'https://www.syfy.com',
        'The CW': 'http://www.cwtv.com',
        'TNT (US)': 'https://www.tntdrama.com/shows',
        'USA Network': 'http://www.usanetwork.com/shows',
        'Первый канал': 'https://www.1tv.ru',
        'Пятый канал': 'https://www.5-tv.ru',
        'ТНТ': 'https://tnt-online.ru/',
    }
    films = csv.reader(films_in_memory.splitlines(), delimiter='\t')
    for row in films:
        if intId == row[0]:
            break
    if row[8] in URLs:        
        return URLs[row[8]]
    else:
        return 'https://www.yandex.ru'
#Return main info about serial
def getFilmInfoLocal(intId):
    #intId = '1'
    #f = open('films.csv', mode="r", encoding="utf-8")
    #films = csv.reader(f, delimiter='\t')
    films = csv.reader(films_in_memory.splitlines(), delimiter='\t')
    for row in films:
        if intId == row[0]:
            #we found a film, close file and exit form the loop
            #f.close()
            break        
    msg = 'Сериал "' + row[5] + '" (' + row[4] + ') впервые вышел в прокат ' + datetime.strftime(datetime.strptime(row[7], '%Y-%m-%d'), '%d.%m.%Y') + ' на канале ' + row[8] + '.'
    if row[9] == '1':
        msg += ' В сериале только 1 сезон и ' + row[10] + ' серий.'
    elif int(row[9]) < 5:
        msg += ' В сериале ' + row[9] + ' сезонa и ' + row[10] + ' серий.'
    else:
        msg += ' В сериале ' + row[9] + ' сезонoв и ' + row[10] + ' серий.'
    msg += ' IMDB рейтинг ' + row[11] + '.'
    if row[6].lower() == 'continuing':
        variants = ['Продолжает сниматься.','Сьемки сериала продолжаются и по сей день.','Ждите новых серий.','Сьемочная группа работает над выпуском новых серий.']
        msg += ' ' + random.choice(variants)
    else:
        variants = ['Сьемки сериала завершены.','Серии более не выпускаются.','Сериал закончен.','Выпуск новых серий и сезонов не планируется.']
        msg += ' ' + random.choice(variants)
    return msg
#Return film location 
def getFilmLocationLocal(intId):
    #intId = '1'
    return "Сериал можно посмотреть на сайте " + OfficialURL(intId)
#Film Search function
def filmSearch(intId, action, time):
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
    seasonName2 = ['','первая','вторая','третья','четвертая','пятая','шестая','седьмая','восьмая','девятая','десятая',
        'одиннадцатая','двенадцатая','тринадцатая','четырнадцатая','пятнадцатая','шеснадцатая','семнадцатая','восемнадцатая','девятнадцатая','двадцатая',
        'двадцать первая','двадцать вторая','двадцать третья','двадцать четвертая','двадцать пятая','двадцать шестая','двадцать седьмая','двадцать восьмая','двадцать девятая', 'тридцатая'
        'тридцать первая','тридцать вторая','тридцать третья','тридцать четвертая','тридцать пятая','тридцать шестая','тридцать седьмая','тридцать восьмая','тридцать девятая', 'тридцатая',
        ]
    #intId = '1'
    #f = open('films.csv', mode="r", encoding="utf-8")
    #films = csv.reader(f, delimiter='\t')
    films = csv.reader(films_in_memory.splitlines(), delimiter='\t')
    found = False
    for row in films:
        if intId == row[0]:
            #we found a film, close file and exit form the loop        
            found = True
            break
    #f.close()
    if not found:
        return 'Простите, не удалось найти в нашей базе данных', 0
    #print(intId, action, time)
    if action == 1:
        #looking for information about location for watching
        return getFilmLocationLocal(intId), int(intId) 
    if action == 2:
        #loocing for additional info in local file
        return getFilmInfoLocal(intId), int(intId)
    if action == 0 or action == -1:
        #question about time, looking for corresponding data, accept default action
        if int(row[3]) > 0:
            #this is serial, looking for the serial
            if(row[6] == 'Ended'):
                #This serial is ended, return message with search ID
                variants = ['Этот сериал завершен.','К сожалению, этот сериал завершен.','Сериал более не выпускается.','Сериал закончен.']
                variants2 = ['Последняя серия под номером','Последняя серия с номером','Заключительная серия номер ','Завершающая серия под номером']
                return random.choice(variants) + ' ' +  random.choice(variants2) + ' ' + row[13] + ' "' + row[14] + '" ' + seasonName[int(row[9])] + ' cезона вышла в прокат ' + datetime.strftime(datetime.strptime(row[12], '%Y-%m-%d'), '%d.%m.%Y'), int(intId)
            
            try:
                tvdbanswer = filmdbLastEpisode(intId)
            except:
                tvdbanswer = tvdbLastEpisode(row[1], row[9])

            #print(tvdbanswer)
            if tvdbanswer[0] == 'Error':
                return 'Простите, не удалось найти', 0            
            #define time according todays date
            if tvdbanswer[2] == '':
                return 'Что то пошло не так, не удалось найти информацию о дате выхода серии. Попробуйте позже.', 0
            d = datetime.strptime(tvdbanswer[2], '%Y-%m-%d')
            n = datetime.now()
            nowday = datetime(n.year, n.month, n.day)
            #print(d)
            if d > nowday:
                #Is not issued
                # variants = [
                #     'Серия ' + str(tvdbanswer[0]) + ' ' + seasonName[int(row[9])] + ' cезона "' + tvdbanswer[1] + '" выйдет в прокат ' + datetime.strftime(d, '%d.%m.%Y'),
                #     'Эпизод ' + str(tvdbanswer[0]) + ' сезона номер ' + row[9] + ' "' + tvdbanswer[1] + '" появится в прокате ' + datetime.strftime(d, '%d.%m.%Y'),
                #     '"' + tvdbanswer[1] + '" выйдет как ' + seasonName2[int(tvdbanswer[0])] + ' cерия в ' + row[9] + '-ом сезоне ' + datetime.strftime(d, '%d.%m.%Y'),
                #     seasonName2[int(tvdbanswer[0])] + 'серия ' + seasonName[int(row[9])] + ' cезона "' + tvdbanswer[1] + '" выйдет в эфир ' datetime.strftime(d, '%d.%m.%Y')
                #     ]
                if tvdbanswer[1] == None:
                    return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона выйдет в прокат ' + datetime.strftime(d, '%d.%m.%Y'), int(intId)
                else:
                    return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона "' + tvdbanswer[1] + '" выйдет в прокат ' + datetime.strftime(d, '%d.%m.%Y'), int(intId)
                #return random.choice(variants), int(intId)
            elif d == nowday:
                #it is today
                if tvdbanswer[1] == None:
                    return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона "' + name + '" выходит сегодня!', int(intId)
                else:
                    return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона "' + tvdbanswer[1] + '" выходит сегодня!', int(intId)
            else:
                #it was in a past
                if tvdbanswer[1] == None:
                    return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона уже вышла в прокат ' + datetime.strftime(d, '%d.%m.%Y'), int(intId)
                else:
                    return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона "' + tvdbanswer[1] + '" уже вышла в прокат ' + datetime.strftime(d, '%d.%m.%Y'), int(intId)
    #final close return (if everythig esle bad)
    return 'Простите, не удалось найти в базе данных', 0
#main function, check for key words and finnaly execute a 
def CoreSearch(text):
    #looking for a name (fist stage)
    filmId = SearchName(text)
    if filmId == -1:
        #we did not find a film, return info message and None as ID
        return "Простите, я не нашла такого фильма или сериала, попробуйте еще раз.", 0
    #looking for an action, if we do not have an action return -2
    action = SearchAction(text)
    #looking for advanced action in the phrase
    time = SeachActionTimeDetection(text)
    #core logic
    return filmSearch(filmId, action, time)



#print(filmdbLastEpisode(1))

print(SearchName("теория большоо взрыва"))
# print(SeachActionTimeDetection("ГДs сока сколь;в ы новый когда же ты где?"))
# print(SearchAction("ГДs сока сколь;в ы когда же ты где?"))

# print(CoreSearch("атланта"))
# print(CoreSearch("стрела"))
# print(CoreSearch("молодежка"))
#print(CoreSearch("дай инфо о теории большого взрыва"))
# print(CoreSearch("где глянуть теорию большого взрыва"))
#print(CoreSearch("новая серия грифинов"))
#print(CoreSearch("свежая серия полицейского с рублевки"))
# print(CoreSearch("доктор хаус"))
# print(CoreSearch("кяввм"))
# print(CoreSearch("эртугрул"))

# print(tvdbLastEpisode('80379','12'))