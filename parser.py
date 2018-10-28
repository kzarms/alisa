import urllib.request
from bs4 import BeautifulSoup

"""
Скрипт принимает файл с именами сериалов и в другой файл записывает их ИД в базе TVDB.
В именах пробелы менять на тире.
Названия русских сериалов писать транслитом. 
"""
#--Проверить ссылку сериала на thetvdb
def check_url_tvdb(series_name):
    try:
        url = "https://www.thetvdb.com/series/" + series_name
        website = urllib.request.urlopen(url)
        content = website.read()
        soup = BeautifulSoup(content, 'html.parser')
        if 'Invalid series' in str(content):
            print(series_name + ": false")
            return 0
        else:
            series_id = soup.find(id="series_basic_info").find_all(class_="list-group-item clearfix")[0].find('span').text
            print(series_name + ": " + series_id)
            return series_id
    except Exception:
        return 0


#----Берём все имена сериалов с файла и добавляем в новый файл.
series_input = open("series_input.txt", 'r')
series_output = open("series_output.txt", 'a')

for series_name in series_input:
    series_id = str(check_url_tvdb(str.rstrip(series_name)))
    #print(series_id)
    series_output.write(str.rstrip(series_name) + ";" + series_id + "\n")

print('....................done......................')



#print(series_file.read())


#checked = check_url_tvdb("the-expanse")
#print(checked)
