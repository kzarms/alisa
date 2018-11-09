import pymysql.cursors
import csv
import io
import requests
from datetime import datetime, timedelta
import sqlite3
import datetime


def connectToDB():
    connection = pymysql.connect(host='127.0.0.1', user='flask', password='FFF123mysql', db='filmsdb', charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    return connection

connection = connectToDB()
cursor = connection.cursor()


#QUOTE this string for MySQL
def sqlquote(value):
    if value is None:
         return 'NULL'
    return "'{}'".format(str(value).replace("'", "''"))


#check if film exists in base
def check_movie(film_id = '', name_original = "", name_russian = ""):
    sql = "SELECT * FROM films WHERE "
    if film_id:
        sql = sql + "id = " + str(film_id) + " OR "
    if name_original:
        sql = sql + "name_original = \"" + name_original + "\" OR "
    if name_russian:
        sql = sql + "name_russian = \"" + name_russian + "\" OR "    
    sql = sql + "id = -9999"
    
    cursor.execute(sql)
   
    if cursor.rownumber == 0:
        return 0
    else:
        for row in cursor:
            print(str(row['film_id']) + ' ' + str(row['name_original']))
            return row['film_id']

            
       
#add film to base
def add_movie(f):
    sql = "INSERT INTO films (id, tvdbId, imdbId, seriesId, nameEn, nameRu, status, firstAired, network, seasons, lastEpisode, rating, lastShow, airedEpisodeNumber, episodeName) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (sqlquote(f.get('id')), sqlquote(f.get('tvdbId')), sqlquote(f.get('imdbId')), sqlquote(f.get('seriesId')), sqlquote(f.get('nameEn')), sqlquote(f.get('nameRu')), sqlquote(f.get('status')), sqlquote(f.get('firstAired')), sqlquote(f.get('network')), sqlquote(f.get('seasons')), sqlquote(f.get('lastEpisode')), sqlquote(f.get('rating')), sqlquote(f.get('lastShow')), sqlquote(f.get('airedEpisodeNumber')), sqlquote(f.get('episodeName'))) + ";"
    cursor.execute(sql)
    connection.commit()
    for row in cursor:
        print(row)
        
#add all films from csv
def add_movies_from_csv():
    f = open('films.csv', mode="r", encoding="utf-8")
    recordList = list(f)
    f.close()
    i = 1
    for (index, item) in list(enumerate(recordList))[1:]:
        #put csv string to JSON
        filmJSON = {}
        filmJSON['id'] = item.split('\t')[0]
        filmJSON['tvdbId'] = item.split('\t')[1]
        filmJSON['imdbId'] = item.split('\t')[2]
        filmJSON['seriesId'] = item.split('\t')[3]
        filmJSON['nameEn'] = item.split('\t')[4]
        filmJSON['nameRu'] = item.split('\t')[5]
        filmJSON['status'] = item.split('\t')[6]
        filmJSON['firstAired'] = item.split('\t')[7]
        filmJSON['network'] = item.split('\t')[8]
        filmJSON['seasons'] = item.split('\t')[9]
        filmJSON['rating'] = item.split('\t')[10]
        filmJSON['lastShow'] = item.split('\t')[11]
        filmJSON['airedEpisodeNumber'] = item.split('\t')[12]
        filmJSON['episodeName'] = item.split('\t')[13].rstrip()
        #if no film in base - add it
        if check_movie(filmJSON['id']) == 0:
            print('add ' + str(filmJSON.get('id')) + ' ' + str(filmJSON.get('nameEn')) + ' to the base')
            add_movie(filmJSON)
        else:
            print(str(filmJSON['nameEn']) + ' already exists, id = ' + str(filmJSON.get('id')))

#get film id by name (russian or english)
def get_film_id_from_name(name):
    sql = 'SELECT id FROM films WHERE nameEn = ' + sqlquote(name) + ' or nameRu = ' + sqlquote(name) + ';'
    cursor.execute(sql)
    for row in cursor:
        return row['id']

        
#get film name by id (use ru or en)
def getFilmNameById(id, language = 'en'):
    if language == 'ru':
        nameAdd = 'nameRu'
    if language == 'en':
        nameAdd = 'nameEn'
    sql = 'SELECT ' + nameAdd + ' FROM films WHERE id = ' + sqlquote(id)
    cursor.execute(sql)
    for row in cursor:
        return row[nameAdd] 

def getFilmIdByTvdbId (tvdbId):
    sql = 'SELECT id FROM films WHERE tvdbId = ' + sqlquote(tvdbId)
    rowcount = cursor.execute(sql)
    if rowcount == 0:
        return 0
    else:
        for row in cursor:
            return row['id']     

#add new episode
def addEpisode(e):
    filmName = getFilmNameById(e.get('filmId'), 'ru')
    if checkEpisode(e.get('filmId'), e.get('episodeNumber')) == 0:
        sql = "INSERT INTO episodes (filmId, episodeNumber, firstAired, nameEn, nameRu, director, overviewEn, overviewRu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" % (sqlquote(e.get('filmId')), sqlquote(e.get('episodeNumber')), sqlquote(e.get('firstAired')), sqlquote(e.get('nameEn')), sqlquote(e.get('nameRu')), sqlquote(e.get('director')), sqlquote(e.get('overviewEn')), sqlquote(e.get('overviewRu')))
        cursor.execute(sql)
        connection.commit()
        for row in cursor:
            return row['id']
        print(filmName + " " + str(e.get('episodeNumber')) + ' has been added')
    else:
        print(filmName + " " + str(e.get('episodeNumber')) + ' already exists')
        

#check if there is episode in base
def checkEpisode(filmId, episodeNumber, nameEn="", nameRu=""):
    sql_add = "";
    if episodeNumber:
        sql_add = "episodeNumber = " + str(episodeNumber)
    if nameEn:
        sql_add = "nameEn = " + str(nameEn)
    if nameRu:
        sql_add = "nameRu = " + str(nameRu)
    
    sql = "SELECT * FROM episodes WHERE filmId = %s AND %s;" % (str(filmId), sql_add)
    rownumber = cursor.execute(sql)   
   
    if rownumber == 0:
        return 0
    else:
        for row in cursor:
            return row['id']

#add alias to table
def add_alias(filmId, alias):
    sql = "INSERT INTO aliases (filmId, alias) VALUES (%s, %s)" % (sqlquote(filmId), sqlquote(alias))
    cursor.execute(sql)
    connection.commit()

#add a lot of aliases from csv file
def addAliasFromCSV():
    f = open('NameVariationsBack.csv', mode="r", encoding="utf-8")
    recordList = list(f)
    f.close()
    for (index, item) in list(enumerate(recordList))[1:]:
        filmId = str(item.split('\t')[0]).rstrip()
        alias = str(item.split('\t')[1]).rstrip()
        if getFilmByAlias(alias) == 0:
            add_alias(filmId, alias)
            print("alias " + filmId + " " + alias + " added")
        else:
            print("alias " + filmId + " " + alias + " exists")
    

#find filmId by it's alias
def getFilmByAlias(alias):
    sql = "SELECT filmId FROM aliases WHERE alias = %s " % (sqlquote(alias))
    rownumber = cursor.execute(sql)
    if rownumber == 0:
        return 0
    else:
        for row in cursor:
            return row['filmId']    
 
#episodeJSON = {"filmId":"2", "number":"1", "nameRu":"вторая серия"}


#print(getFilmByAlias('шучу'))


token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDE4MjE2MDMsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MTczNTIwMywidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.0FtDgPu3YQqOrxV9U3aH9GG0P64avUUxg9ETU15r-B2Yjt1m8zagcZ8iwmNazfOHjBiKgQPBducRE9mg6lrg14EhNVPfvfwxVkFSqU5QINhQRCw_7VXawHPQ4WrAhF7HSiLuHbIRZY5AkWUhvw4ZpbXY3MpfqLVK2yCBhrRPwOE0dT7p-yGTuguqQwF2pE_82n0dd6ToBWHmFCmme8wkWtbDRsr4lZsBQKwG95DWmnA3So9dvS3MbCY82yikwbNH6bmDbcA5Up7iWIbJiGHuRS3EaE1Jm6aotL1juvlWCwuZQKpbmpxjPY9KmZdZ6CneI7n6FKhtxHcLT8FwKzjjKg' 
   

def addSeasonFromTVDBToBase(tvdbId, seasonNumber):
    filmId = getFilmIdByTvdbId(tvdbId)
    URL = "https://api.thetvdb.com"   
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}  
    PARAMS = {'airedSeason':str(seasonNumber)} 
    
    URL = URL + '/series/' + str(tvdbId) + '/episodes/query'
    r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
    dataRu = r.json()
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
    r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
    dataEn = r.json()


    for i in range(len(dataEn['data'])):
        if dataEn['data'][i]['firstAired'] != '':
            data = datetime.datetime.strptime(dataEn['data'][i]['firstAired'], '%Y-%m-%d')
        elif dataRu['data'][i]['firstAired'] != '':
            data = datetime.datetime.strptime(dataRu['data'][i]['firstAired'], '%Y-%m-%d')
        else:
            data = None
        episodeJSON = {}
        episodeJSON['filmId'] = filmId
        episodeJSON['episodeNumber'] = int(seasonNumber) * 1000 + int(dataEn['data'][i]['airedEpisodeNumber'])
        episodeJSON['firstAired'] = data
        episodeJSON['nameEn'] = dataEn['data'][i]['episodeName']
        episodeJSON['nameRu'] = dataRu['data'][i]['episodeName']
        episodeJSON['director'] = dataEn['data'][i]['director']
        episodeJSON['overviewEn'] = dataEn['data'][i]['overview']
        episodeJSON['overviewRu'] = dataRu['data'][i]['overview']
        episodeJSON['showURL'] = dataEn['data'][i]['showUrl']
        addEpisode(episodeJSON)


def addEpisodesFromCsv():
    f = open('seasons.csv', mode="r", encoding="utf-8")
    recordList = list(f)
    f.close()
    for (index, item) in list(enumerate(recordList))[1:]:
        tvdbId = str(item.split('\t')[0]).rstrip()
        season = str(item.split('\t')[1]).rstrip()
        addSeasonFromTVDBToBase(tvdbId, season)
        

#--Get the last episode
def getTheLastEpisode(filmId):
    sql = "SELECT nameEn, nameRu, episodeNumber, firstAired FROM episodes WHERE filmiD = %s and firstAired >= %s ORDER BY firstAired ASC LIMIT 1;" % (sqlquote(filmId), sqlquote(datetime.datetime.today().strftime("%Y-%m-%d 00:00:00")))
    rownumber = cursor.execute(sql)
    lastEpisode = cursor.fetchone()
    episode = {}
    #episode['filmName'] = getFilmNameById(filmId)
    
    episode['status'] = 'progress'
    if rownumber == 0:
        #--if series is ended - show the last series. 
        sql = "SELECT nameEn, nameRu, MAX(episodeNumber) as episodeNumber, firstAired FROM episodes WHERE filmId = %s" % (filmId)
        cursor.execute(sql)
        episode['status'] = 'finished' #--marker that shows if series is finished or not
        lastEpisode = cursor.fetchone()
     
    if lastEpisode.get('nameRu') != None:
        name = lastEpisode['nameRu']
    else:
        name = lastEpisode['nameEn']
    
    episodeNumber = int(lastEpisode.get('episodeNumber'))
    season = round(round(episodeNumber / 1000))
    #number = season * 1000 - episodeNumber
    episode['season'] = season
    episode['episodeNumber'] = episodeNumber - season * 1000
    episode['name'] = name
    episode['firstAired'] = lastEpisode['firstAired']
    return episode
        
            
#print(getTheLastEpisode(44))

n = datetime.datetime.now()
for i in range(1,30):
    episode = getTheLastEpisode(i)
    print(str(episode['episodeNumber']) + ' ' + str(episode['name']) + ' ' + str(episode['firstAired']))
print(datetime.datetime.now() - n)



#shameless info about episode https://serialium.ru/tv-series/shameless/s8/ https://serialium.ru/tv-series/shameless/s9/
#wild wild country https://en.myshows.me/view/56783/
#Walking dead https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%8D%D0%BF%D0%B8%D0%B7%D0%BE%D0%B4%D0%BE%D0%B2_%D1%82%D0%B5%D0%BB%D0%B5%D1%81%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%B0_%C2%AB%D0%A5%D0%BE%D0%B4%D1%8F%D1%87%D0%B8%D0%B5_%D0%BC%D0%B5%D1%80%D1%82%D0%B2%D0%B5%D1%86%D1%8B%C2%BB
#14 https://www.amediateka.ru/serial/ubivaya-evu
#15 
#18 http://www.lostfilm.tv/series/Billions/
#26 http://www.lostfilm.tv/series/Animal_Kingdom/seasons/
#27 http://www.lostfilm.tv/series/Gotham/seasons/



