# l = ['a', 'b', 'c', 'd']
# for i in range(10):
#     print(l[i%len(l)])
#from flask import Flask, request

# importing the requests library 
import csv
import io
import requests 

token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDA4NDIwNTIsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MDc1NTY1MiwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.IsZxHlgf1HxaBiizZ5M90nQtId5Cv6B1iiwkUIH-ivHdBx78_RJbzawHU_jYEVadtakZc0f6kiOVKK_D1TfxiQD82rNHCcyC4-kUUTbS8JrqQxU0GgUXS8Va0HAOA9J9kxsJKHu7iCYLYotQaWBQpkq5Z__dhScnfHtLBL9_GS9XYaixNZ3SVcq6T83lVcYMJU9-eNZ7YHkPf7Aji52S5rqAEedC4FRn1YkchbPdMlPaLaFRb8MKH56_wSINuQ5b5rJTJa6hevIQZpV8MJ2PtbSEyeiSkUjG3pQy78csy7nO3UiSOOmJHTh4CcQa_OSRQbx1Fes63vE6YIK3Yaxwmw'

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
    URL = "https://api.thetvdb.com"    
    #filmID = '80379'
    #seasonNumber = '12'
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)} 
    #HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}  
    #PARAMS = {'airedSeason':seasonNumber} 
    #Create full request
    #URL = URL + '/series/' + filmID + '/episodes/query'
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
    f = open('films.csv', mode="r", encoding="utf-8")
    myid = int((list(f)[-1]).split('\t')[0]) + 1
    f.close()
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
    f = open('films.csv', mode="a", encoding="utf-8")
    csv_writer = csv.writer(f, lineterminator='\n', delimiter='\t')
    csv_writer.writerow(fields)
    f.close()

#test add series :)
tvdbGetSerialInfo(281534)
tvdbGetSerialInfo(70533)
tvdbGetSerialInfo(323168)



"""

def getLastEpisodData(filmID, airedSeason): 
    # intId = 8   
    # f = open('films.csv', mode="r", encoding="utf-8")
    # films = csv.reader(f, delimiter='\t')
    # found = False
    # for row in films:
    #     if str(intId) == row[0]:
    #         #we found a film, close file and exit form the loop
    #         f.close()
    #         found = True
    #         break
    # filmID = row[1]
    # seasonNumber = row[9]
    # airedEpisode = row[10]

    URL = "https://api.thetvdb.com"
    #HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)} 
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}  
    #PARAMS = {'airedSeason':str(airedSeason), 'absoluteNumber':str(absoluteNumber)} 
    PARAMS = {'airedSeason':str(airedSeason),} 
    #Create full request
    URL = URL + '/series/' + str(filmID) + '/episodes/query'
    r = requests.get(url = URL, headers = HEADERS, params = PARAMS)  
    # extracting data in json format 
    data = r.json()
    if 'Error' in data:
        #there is an error
        if data['Error'] == 'Not authorized':
            return "Auth error"
        if 'No results for your query' in data['Error']:
            return "Search error"
        return "Unspecified error"
    maxEpnum = 1
    for episod in data['data']:
        if int(episod['airedEpisodeNumber']) > maxEpnum:
            maxEpnum = int(episod['airedEpisodeNumber'])
            masEp = episod
    if  episod['episodeName'] == None:
        #no rus name
        HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)}
        r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
        data = r.json()
        maxEpnum = 1
        for episod in data['data']:
            if int(episod['airedEpisodeNumber']) > maxEpnum:
                maxEpnum = int(episod['airedEpisodeNumber'])
                masEp = episod
    l = [episod['firstAired'], episod['airedEpisodeNumber'], episod['episodeName'],]
    return l


def updateCsv():
    with open('films.csv', mode="r", encoding="utf-8") as csvinput:
        with open('films2.csv', mode="w+", encoding="utf-8") as csvoutput:
            writer = csv.writer(csvoutput, lineterminator='\n', delimiter='\t')
            reader = csv.reader(csvinput, delimiter='\t')

            all = []
            row = next(reader)
            row.append('lastShow')
            row.append('airedEpisodeNumber')
            row.append('episodeName')
            all.append(row)

            for row in reader:
                if row[6] == 'Ended':
                    l = getLastEpisodData(row[1],row[9])
                    row.append(l[0])
                    row.append(l[1])
                    row.append(l[2])
                else:
                    row.append('TBD')
                    row.append('TBD')
                    row.append('TBD')
                all.append(row)

            writer.writerows(all)

"""
"""series_id = open("series_id.txt", 'r')
for line in series_id.readlines():
    id = str.rstrip(line)
    tvdbGetSerialInfo(id)
    print(id + ' completed')
"""
#getLastEpisodData(75760,9)
#updateCsv()