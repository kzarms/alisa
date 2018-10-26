# function module
import csv
import io
import requests
from datetime import datetime, timedelta

#film search funtion in a csv file
def SearchName(text):
    #text = "дай инфо о теории большого взрывы"
    text = text.lower()
    words = text.split(" ")
    wordList = []
    for word in words:
        if len(word.strip(' ?!,;:')) > 1:
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
#seach function in the tbdb
def tvdbLastEpisode(filmID, seasonNumber):
    URL = "https://api.thetvdb.com"
    token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDA2Njk5MjAsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MDU4MzUyMCwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.y1ewCP-UtgljD-sV0TVsWRcfCpdH0hBq_mYwXWgCjyMEa0ZLRvh6RjnobSMLk8ldbzYRtzdhOjoZ2HGk-T1x3xHXKJi_uqApI-FwCf7y5-qb-LWRLoey0rnkowlCSFS7HCam1UmjhpxSe7D1UMoQE7NmaMaOS1AJlkOy1Wo93wdiTHYp7SsA1Iy0pFEkCtR0bkGBHL1rgbcZjWjbbwzrXVGQ08xgEF7x0j8LnIMdQT36M9lIi9MCT9VStM9a0xDVNx65w0epS-vuwrTrb2XT0qGYwXEWrF_fZ5fZXX_c4_t_VtPPsN_KRPb27BByXkW90mjCEb9ibTuwKytUIQ80CQ'
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
    #print(lastEpisode)
    #looking for particular data from the last episode
    for series in data['data']:
        if int(series['airedEpisodeNumber']) == lastEpisode:
            return series['airedEpisodeNumber'], series['episodeName'], series['firstAired']
#Return the URL to the offical site 
def OfficialURL(intId):
    URLs = {
        'CBS': 'https://www.cbs.com',
        'HBO': 'https://www.hbogo.com', 
        'Showtime': 'https://www.sho.com',
        'Netflix': 'https://www.netflix.com',
    }
    f = open('films.csv', mode="r", encoding="utf-8")
    films = csv.reader(f, delimiter='\t')
    for row in films:
        if intId == row[0]:
            #we found a film, close file and exit form the loop
            f.close()
            break
    return URLs[row[8]]
#Return main info about serial
def getFilmInfoLocal(intId):
    #intId = '1'
    f = open('films.csv', mode="r", encoding="utf-8")
    films = csv.reader(f, delimiter='\t')
    for row in films:
        if intId == row[0]:
            #we found a film, close file and exit form the loop
            f.close()
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
        msg += ' Продолжает сниматься.'
    else:
        msg += ' Cьемки завершены.'
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
        "двадцать первого","двадцать второго","двадцать третьего","двадцать четвертого","двадцать пятого","двадцать шестого",]

    f = open('films.csv', mode="r", encoding="utf-8")
    films = csv.reader(f, delimiter='\t')
    found = False
    for row in films:
        if intId == row[0]:
            #we found a film, close file and exit form the loop
            f.close()
            found = True
            break
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
            #print('enter to search')
            tvdbanswer = tvdbLastEpisode(row[1], row[9])
            #print(tvdbanswer)
            if tvdbanswer[0] == 'Error':
                return 'Простите, не удалось найти', 0
            #define time according todays date
            d = datetime.strptime(tvdbanswer[2], '%Y-%m-%d')
            n = datetime.now()
            nowday = datetime(n.year, n.month, n.day)
            print(d)
            if d > nowday:
                #Is not issued
                return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона "' + tvdbanswer[1] + '" выйдет в прокат ' + datetime.strftime(d, '%d.%m.%Y'), int(intId)
            elif d == nowday:
                #it is today
                return "Серия " + str(tvdbanswer[0]) + " " + seasonName[int(row[9])] + ' cезона "' + tvdbanswer[1] + '" выходит сегодня!', int(intId)
            else:
                #it was in a past
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

# print(SearchName("во все тяжкие большого взрыва"))
# print(SeachActionTimeDetection("ГДs сока сколь;в ы новый когда же ты где?"))
# print(SearchAction("ГДs сока сколь;в ы когда же ты где?"))

# print(CoreSearch("теория большого взрыва"))
# print(CoreSearch("Когда выйдет игра престолов?"))
# print(CoreSearch("дай инфо о теории большого взрыва"))
# print(CoreSearch("где глянуть теорию большого взрыва"))

# print(tvdbLastEpisode('80379','12'))