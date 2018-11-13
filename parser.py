import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime


#--check tvdb (deprecated)
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


#--get info from tvguide.com
def getEpisodeInfoFromTvGuide(url):
    website = urllib.request.urlopen(url)
    content = website.read()
    soup = BeautifulSoup(content, 'html.parser')
    episode = {}
    episode['seriesName'] = soup.find(class_="tvobject-masthead-head-link").text.rstrip()
    episode['seasonNumber'], episode['episodeNumber'] = changeStringFormat(soup.find(class_="tvobject-episode-meta-info hidden-xs").find_all('p')[0].text, "tvguide")
    episode['date'] = changeDateFormat(soup.find(class_="tvobject-episode-meta-info hidden-xs").find_all('p')[1].text, "tvguide")
    return episode


#--change date format depending on source website
def changeDateFormat(date, source=""):
    if source == 'tvguide' or source == "":
         return datetime.strptime(date, '%B %d, %Y').strftime("%Y-%m-%d")


def changeStringFormat(string, source=""):
    if source == 'tvguide' or source == "":
        parsedNumber = string.split(", ")
        seasonNumber = parsedNumber[0].replace("Season ", "")
        episodeNumber = parsedNumber[1].replace("Episode ", "")
        return seasonNumber, episodeNumber


#November 7, 2018
#print(getEpisodeInfoFromTvGuide("https://www.tvguide.com/tvshows/south-park/episodes/100402/"))

n = datetime.now()
f = open('url.txt')
seriesList = f.read().split('\n')
for url in seriesList:
    if url != "":
        episode =  getEpisodeInfoFromTvGuide(url)
        print("%s серия %s сезона сериала %s выходит %s" % (str(episode['episodeNumber']), str(episode['seasonNumber']), episode['seriesName'], str(episode['date'])))
print(datetime.now() - n)