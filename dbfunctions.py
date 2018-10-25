# function module
import csv
import io
import requests
from datetime import datetime, timedelta
#film search funtion in a csv file
def SearchName(text):
    text = text.lower()
    words = text.split(" ")
    wordList = []
    for word in words:
        wordList.append(word.strip(' ?!,;:'))
    f = open('NameVariations.csv', mode="r", encoding="utf-8")
    filmReader = csv.reader(f, delimiter='\t')
    for row in filmReader:        
        filmName = ""
        for word in wordList:
            if word in row[1]:
                filmName += word + " "
        if filmName[:-1] == row[1]:
            #Убираем последний пробел и проверям полное соответсвие названию
            f.close()
            return row[0]
    f.close()
    return -1

#Looking for key words related to action
#time 0, plase 1, else -1
def SearchAction(text):
    KeyWords = {
        'когда': 0, 'кагда': 0, 'when': 0, 'скоро': 0,
        'где': 1,
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

#print(SearchName("во все тяжкие большого взрыва"))
#print(SeachActionTimeDetection("ГДs сока сколь;в ы новый когда же ты где?"))
#print(SearchAction("ГДs сока сколь;в ы когда же ты где?"))
#seach function in the tbdb
def tvdbLastEpisode(filmID, seasonNumber):
    URL = "https://api.thetvdb.com"
    token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDA1ODMyMjAsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MDQ5NjgyMCwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.0TKJhRZ7-sVGaPonMOrSWYz2DIWkpKo1hHAbap01Fu6sYRVwK0_LYbrvDy_yilQXCG2wcIKtI6DdPDEJ9ZBhMkP2ZOLJSidqYfevJoo3l49rLBGNRbzCJEN8atFNGQHdpcu9iHe8I6U7MnCOPgwSijTxlJFCoOdeQrrgBaPHq_aRlxgtIUiqNvzt19jIlF2X_kUp_zrQw-XUgOJkGTC72LFGJPQA_5EIV00mPg0L3UuRFtvN1c9Gapu8Ku00mnRblfOUAgPG0mo76_UmnfYjq6va939B767S690sLorfWiO_qPECnFV5ByCoXXwSamZ3arISJK27qkX-l3VUq4oRdg'
    #filmID = '296762'
    #seasonNumber = '2'
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}  
    PARAMS = {'airedSeason':seasonNumber} 
    #Create full request
    URL = URL + '/series/' + filmID + '/episodes/query'
    r = requests.get(url = URL, headers = HEADERS, params = PARAMS)  
    # extracting data in json format 
    data = r.json()
    if 'Error' in data:
        #there is an error
        if data['Error'] == 'Not authorized':
            return 'Error', 'Auth error'
        if 'No results for your query' in data['Error']:
            return 'Error', 'Search error'
        return 'Error', 'Unspecified error'
    if data['data'][-1]['episodeName'] == None:
        #if there is no Rus name, repeat in En
        HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
        r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
        data = r.json()
    #looking for the last episod in the seies
    lastEpisode = 1
    for series in data['data']:
        if int(series['airedEpisodeNumber']) > lastEpisode:
            lastEpisode = int(series['airedEpisodeNumber'])
    print(lastEpisode)
    #looking for particular data from the last episode
    for series in data['data']:
        if int(series['airedEpisodeNumber']) == lastEpisode:
            return series['airedEpisodeNumber'], series['episodeName'], series['firstAired']

#tvdbanswer = tvdbLastEpisode('80379','12')

def filmSearch(id, action, time):
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
        "двадцать первого","двадцать второго","двадцать третьего","двадцать четвертого","двадцать пятого","двадцать шестого",]

    f = open('films.csv', mode="r", encoding="utf-8")
    films = csv.reader(f, delimiter='\t')
    for row in films:
        if id == row[0]:
            #we found a film, close file and exit form the loop
            f.close()
            break
    if int(row[3]) > 0:
        #this is serial, looking for the serial
        tvdbanswer = tvdbLastEpisode(row[1], row[9])
        print(tvdbanswer)
        if tvdbanswer[0] == 'Error':
            return 'Простите, не удалось найти', ''
        #define time according todays date
        d = datetime.strptime(tvdbanswer[2], '%Y-%m-%d')
        n = datetime.now()
        nowday = datetime(n.year, n.month, n.day)
        if d > nowday:
            #Is not issued
            return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона "' + tvdbanswer[1] + '" выйдет в прокат ' + datetime.strftime(d, '%d.%m.%Y'), id
        elif d == nowday:
            #it is today
            return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона "' + tvdbanswer[1] + '" выходит сегодня!', id
        else:
            #it was in a past
            return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона "' + tvdbanswer[1] + '" уже вышла в прокат ' + datetime.strftime(d, '%d.%m.%Y'), id

#main function, check for key words and finnaly execute a 
def CoreSearch(text):
    #lookinc for a name (fist stage)
    filmId = SearchName(text)
    if filmId == -1:
        #we did not find a film
        return "Простите, я не нашла такого фильма или сериала, попробуйте еще раз.", None
    #looking for an action, if we do not have an action return -2
    action = SearchAction(text)
    #looking for advanced action in the phrase
    time = SeachActionTimeDetection(text)
    #core logic
    return filmSearch(filmId, action, time)
#a = CoreSearch("Когда выйдет игра престолов?")
#print(a)
