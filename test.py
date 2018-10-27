# l = ['a', 'b', 'c', 'd']
# for i in range(10):
#     print(l[i%len(l)])
#from flask import Flask, request

# importing the requests library 
import csv
import io
import requests 

token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDA3NTY5MjUsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MDY3MDUyNSwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.uNwbwGata1RgRbj_4uDJ4TgsPwfCb1ladYK0GYmYrr7hXWo50HYPxKnSqfGaspiNZEDtyXiAUH6CAmrFvNpfOFwgX1KfEhL5lfT-MHRJY7snRyZh9GOkY9LmvEy669a6xrhmMtAUfYx9NVC809ihAZAQ3xlYNlZ-xsayPvrgxA9FBth2-32QJY2fxh8SdF9RHBhRSr_w9SE993PjNpsVdu9dkKZZwAhHxcbsv3wTBBa7k70sqwyQkT4QMr9zF8MvkLBouBdVwzkOx9CtBJ_icTxIJHAZ8hsrNTVjztkDrDL2ybUORaEsKoZzcE9Jmc_TUfXb45gsh8mwYqaGjFG1Ww'

def tvdbGetSerialInfo(filmID):
    URL = "https://api.thetvdb.com"    
    #filmID = '80379'
    #seasonNumber = '12'
    HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token)} 
    #HEADERS = {'Content-Type': 'application/json','Authorization':('Bearer ' + token),'Accept-Language':'ru'}  
    #PARAMS = {'airedSeason':seasonNumber} 
    #Create full request
    #URL = URL + '/series/' + filmID + '/episodes/query'
    URL = URL + '/series/' + filmID
    r = requests.get(url = URL, headers = HEADERS)  
    # extracting data in json format 
    data = r.json()
    if 'Error' in data:
        #there is an error
        if data['Error'] == 'Not authorized':
            return "Auth error"
        if 'No results for your query' in data['Error']:
            return "Search error"
        return "Unspecified error"
    
    URL = URL + '/episodes/summary'
    r2 = requests.get(url = URL, headers = HEADERS)
    data2 = r2.json()

    if 'Error' in data:
        #there is an error
        if data2['Error'] == 'Not authorized':
            return "Auth error"
        if 'No results for your query' in data2['Error']:
            return "Search error"
        return "Unspecified error"
    
    if data['data']['seriesId'] == "":
        seriesId = '999999'
    else:
        seriesId = data['data']['seriesId']


    fields = ['',
        data['data']['id'],
        data['data']['imdbId'],
        seriesId,
        data['data']['seriesName'],
        '',
        data['data']['status'],
        data['data']['firstAired'],
        data['data']['network'],
        max(map(int, data2['data']['airedSeasons'])),
        data2['data']['airedEpisodes'],
        data['data']['siteRating']
        ]

    f = open('films.csv', mode="a", encoding="utf-8")
    csv_writer = csv.writer(f, delimiter='\t')
    csv_writer.writerow(fields)
    f.close()

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

#tvdbGetSerialInfo('293372')

#getLastEpisodData(75760,9)


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

updateCsv()