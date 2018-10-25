# l = ['a', 'b', 'c', 'd']
# for i in range(10):
#     print(l[i%len(l)])
#from flask import Flask, request

# importing the requests library 
import csv
import io
import requests 
  
def tvdbGetSerialInfo(filmID):
    URL = "https://api.thetvdb.com"
    token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDA1ODMyMjAsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MDQ5NjgyMCwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.0TKJhRZ7-sVGaPonMOrSWYz2DIWkpKo1hHAbap01Fu6sYRVwK0_LYbrvDy_yilQXCG2wcIKtI6DdPDEJ9ZBhMkP2ZOLJSidqYfevJoo3l49rLBGNRbzCJEN8atFNGQHdpcu9iHe8I6U7MnCOPgwSijTxlJFCoOdeQrrgBaPHq_aRlxgtIUiqNvzt19jIlF2X_kUp_zrQw-XUgOJkGTC72LFGJPQA_5EIV00mPg0L3UuRFtvN1c9Gapu8Ku00mnRblfOUAgPG0mo76_UmnfYjq6va939B767S690sLorfWiO_qPECnFV5ByCoXXwSamZ3arISJK27qkX-l3VUq4oRdg'
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

    fields = ['',
        data['data']['id'],
        data['data']['imdbId'],
        data['data']['seriesId'],
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

#tvdbGetSerialInfo('121361')