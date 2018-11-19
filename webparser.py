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
def getEpisodesInfoFromTvGuide(url):
    website = urllib.request.urlopen(url)
    content = website.read()
    soup = BeautifulSoup(content, 'html.parser')
    #names = episode['seriesName'] = soup.find_all(class_="tvobject-episode-title")
    allParsedEpisodes = soup.find_all(class_="tvobject-episode-col-info")
    #print(allParsedEpisodes)
    episodes = []
    for line in allParsedEpisodes:
        episode = {}
        episode['episodeNameEn'] = line.find(class_="tvobject-episode-title").text.rstrip()
        episode['airedSeason'], episode['airedEpisodeNumber'] = changeStringFormat(line.find(class_="tvobject-episode-meta-info hidden-xs").find_all('p')[0].text, "tvguide")
        episode['firstAired'] = changeDateFormat(line.find(class_="tvobject-episode-meta-info hidden-xs").find_all('p')[1].text, "tvguide")
        episode['overviewEn'] = line.find(class_="tvobject-episode-description hidden-xs").text
        episodes.append(episode)
    return episodes


#--change date format depending on source website
def changeDateFormat(date, source=""):
    if source == 'tvguide' or source == "":
         return datetime.strptime(date, '%B %d, %Y').strftime("%Y-%m-%d 00:00:00")


def changeStringFormat(string, source=""):
    if source == 'tvguide' or source == "":
        parsedNumber = string.split(", ")
        airedSeason = parsedNumber[0].replace("Season ", "")
        airedEpisodeNumber = parsedNumber[1].replace("Episode ", "")
        return airedSeason, airedEpisodeNumber


#November 7, 2018
print(getEpisodesInfoFromTvGuide("https://www.tvguide.com/tvshows/south-park/episodes/100402/"))
#{'episodeNameEn': 'Nobody Got Cereal?', 'airedSeason': '22', 'airedEpisodeNumber': '7', 'firstAired': '2018-11-14 00:00:00', 'overviewEn': 'The boys break out of jail but are on the run from the police and ManBearPig.'},
"""
n = datetime.now()
f = open('url.txt')
seriesList = f.read().split('\n')
for url in seriesList:
    if url != "":
        episode =  getEpisodeInfoFromTvGuide(url)
        print("%s серия %s сезона сериала %s выходит %s" % (str(episode['airedEpisodeNumber']), str(episode['airedSeason']), episode['seriesName'], str(episode['date'])))
print(datetime.now() - n)
"""

#url = "https://www.tvguide.com/tvshows/the-big-bang-theory/episodes/288041/"
#episodes =  getEpisodesInfoFromTvGuide(url)
#print(episodes)

#print(str(getEpisodesInfoFromTvGuide('https://www.tvguide.com/tvshows/the-big-bang-theory/episodes/288041')))