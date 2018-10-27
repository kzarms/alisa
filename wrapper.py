# coding: utf=8

import json
import requests
from bs4 import BeautifulSoup
from BeautifulSoup import BeautifulSoup

URL = "https://www.lostfilm.tv"
URL = URL + '/series/?type=search&g=&s=1&t=2'
#token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDA2Njk5MjAsImlkIjoiYWxpc2EiLCJvcmlnX2lhdCI6MTU0MDU4MzUyMCwidXNlcmlkIjo1MTM1MDcsInVzZXJuYW1lIjoidmxrb290bW5pIn0.y1ewCP-UtgljD-sV0TVsWRcfCpdH0hBq_mYwXWgCjyMEa0ZLRvh6RjnobSMLk8ldbzYRtzdhOjoZ2HGk-T1x3xHXKJi_uqApI-FwCf7y5-qb-LWRLoey0rnkowlCSFS7HCam1UmjhpxSe7D1UMoQE7NmaMaOS1AJlkOy1Wo93wdiTHYp7SsA1Iy0pFEkCtR0bkGBHL1rgbcZjWjbbwzrXVGQ08xgEF7x0j8LnIMdQT36M9lIi9MCT9VStM9a0xDVNx65w0epS-vuwrTrb2XT0qGYwXEWrF_fZ5fZXX_c4_t_VtPPsN_KRPb27BByXkW90mjCEb9ibTuwKytUIQ80CQ'
#HEADERS = {'Content-Type': 'application/json',}  
HEADERS = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
#PARAMS = {'type':'search&g=&s=1&t=2'}

#r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
rs= requests.get(url = URL, headers = HEADERS)
rs.headers
rs.encoding = 'utf-8'
parsed_html = BeautifulSoup(rs.text)

print(parsed_html.body.find('div', attrs={'class':'row'}).text)


parsed_html.body.find


rs.text.index('<div class="row">')
rs.text[31984:33000]
grequests.map(rs)

for s in rs._content:
    print(reinterpret(s))

def reinterpret(string):
    byte_arr = bytearray(ord(char) for char in string)
    return byte_arr.decode('utf8')

a = '\xd0\xbd\xd0\xbe\xd0\xb2\xd1\x8b\xd0\xb5'
print(reinterpret(a))
#Create full request

#r = requests.get(url = URL, headers = HEADERS, params = PARAMS)    
try:
    r = requests.get(url = URL, headers = HEADERS, params = PARAMS)
except:
    return 'Error', 'Connection error'

# extracting data in json format 
data = r.json()