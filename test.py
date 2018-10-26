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
    token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDA2Njk5MjAsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MDU4MzUyMCwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.y1ewCP-UtgljD-sV0TVsWRcfCpdH0hBq_mYwXWgCjyMEa0ZLRvh6RjnobSMLk8ldbzYRtzdhOjoZ2HGk-T1x3xHXKJi_uqApI-FwCf7y5-qb-LWRLoey0rnkowlCSFS7HCam1UmjhpxSe7D1UMoQE7NmaMaOS1AJlkOy1Wo93wdiTHYp7SsA1Iy0pFEkCtR0bkGBHL1rgbcZjWjbbwzrXVGQ08xgEF7x0j8LnIMdQT36M9lIi9MCT9VStM9a0xDVNx65w0epS-vuwrTrb2XT0qGYwXEWrF_fZ5fZXX_c4_t_VtPPsN_KRPb27BByXkW90mjCEb9ibTuwKytUIQ80CQ'
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

tvdbGetSerialInfo('338946')