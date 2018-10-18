#Модуль работы с внутренней базой данных
import csv
import io
from datetime import datetime, timedelta
#Функиця поиска фильма или сериала по таблице, возвращает ID сериала или фильма.
#   -1  Нет сериала
#   X   ID фильма или сериала

class movie:
  def __init__(self, id="", IsSerial="", SerialId="", OriginalName="", RussianName="", Description="", DateOfIssue="", Kinopoisk="", IMDb=""):
    self.id = id
    self.IsSerial = IsSerial
    self.SerialId = SerialId
    self.OriginalName = OriginalName
    self.RussianName = RussianName
    self.Description = Description
    self.DateOfIssue = DateOfIssue
    self.Kinopoisk = Kinopoisk
    self.IMDb = IMDb

  def filmInfo(self):
    print(self.RussianName, "вышел в прокат", self.DateOfIssue)
  
  def wentIssue(self):
    if self.DateOfIssue == "":
        return "Простите, не удалось найти."
    d = datetime.strptime(self.DateOfIssue, '%d.%m.%Y')
    n = datetime.now()
    nowday = datetime(n.year, n.month, n.day)
    if d > nowday:
        #Is not issued
        return self.RussianName + " выйдет в прокат " + self.DateOfIssue
    elif d == nowday:
        #it is today
         return self.RussianName + " выходит в прокат сегодня!"
    else:
        #it was in a past
        return self.RussianName + " уже вышел в прокат " + self.DateOfIssue

  def getSerialId(self):
      return int(self.SerialId)

  def isSerial(self):
    if self.IsSerial == '1':
        return True
    else:
        return False

class episode(movie):
    def __init__(self, id, IsSerial, SerialId, OriginalName, RussianName, Description, DateOfIssue, Kinopoisk, IMDb, SeasonNumber, EpisodeNumber):
        movie.__init__(self, id, IsSerial, SerialId, OriginalName, RussianName, Description, DateOfIssue, Kinopoisk, IMDb)
        self.SeasonNumber = SeasonNumber
        self.EpisodeNumber = EpisodeNumber
    
    def wentIssue(self):
        if self.SeasonNumber == "":
            return "Простите, не удалось найти." 
        seasonName = ["", "первого", "второго", "третьего", "четвертого", "пятого", "шестого","седьмого","восьмого","девятого","десятого","одиннадцатого", "двенадцатого", "тринадцатого", "четырнадцатого", "пятнадцатого", "шестнадцатого"]
        if self.OriginalName == "TBD":
            return "Простите, дата выхода епизода " + self.EpisodeNumber + " " + seasonName[int(self.SeasonNumber)] + " cезона еще не анонсирована."
        
        d = datetime.strptime(self.DateOfIssue, '%d.%m.%Y')
        n = datetime.now()
        nowday = datetime(n.year, n.month, n.day)
        if d > nowday:
            #Is not issued
            return "Серия " + self.EpisodeNumber + " " + seasonName[int(self.SeasonNumber)] + ' cезона "' + self.RussianName + '" выйдет в прокат ' + self.DateOfIssue
        elif d == nowday:
            #it is today
            return "Серия " + self.EpisodeNumber + " " + seasonName[int(self.SeasonNumber)] + ' cезона "' + self.RussianName + '" выходит сегодня!'
        else:
            #it was in a past
            return "Серия " + self.EpisodeNumber + " " + seasonName[int(self.SeasonNumber)] + ' cезона "' + self.RussianName + '" уже вышла в прокат ' + self.DateOfIssue


def SearchName(text):
    text = text.lower()
    words = text.split(" ")
    wordList = []
    for word in words:
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

#Функция поиска ключевого слова в фразе, от него зависит дальнейшее действие. Возвращает ID действия
#   -1  Нет слова
#   0   когда
#   1   гда
#   2   сколько
def SearchAction(text):
    actions = ["когда","где","сколько",]
    text = text.lower()    
    WordList = text.split(" ")
    for word in WordList:
        word = word.strip(" ?!,;:")
        if word in actions:
            return actions.index(word)
    return -1

#Функция нужна для опеределении времени вопроса КОГДА, ищет ключевые слова относящиеся к будущему, прошлому и настоящему
#Возвращает int
# 0 - прошлое
# 1 - настоящее
# 2 - будущее
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
    return 2 

#print(SearchName("когда во все тяжкие большого взрыва"))
#print(SeachActionTimeDetection("ГДs сока сколь;в ы новый когда же ты где?"))
#print(SearchAction("ГДs сока сколь;в ы когда же ты где?"))

def filmSearch(id, action, time):
    print(id, action, time)
    f = open('films.csv', mode="r", encoding="utf-8")
    films = csv.reader(f, delimiter='\t')
    for row in films:
        if id == row[0]:
            MyMovie = movie(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
            break
    f.close()
    #MyMovie.filmInfo()
    #We done with film search and now lookig for an answer
    if (action == 0) and (time == 2):
        #looking for the next seies
        if MyMovie.isSerial():
            #this is serial, looking for the next episode in the different csv file
            movieid = MyMovie.SerialId
            #n = datetime.now()
            #nowday = datetime(n.year, n.month, n.day)
            f = open('episodes.csv', mode="r", encoding="utf-8")
            episodes = csv.reader(f, delimiter='\t')
            for row in episodes:
                #looking for in rows our movie
                if movieid == row[1]:
                    MyEpisode = episode("", "", "", row[4], row[5], "", row[6], "", "", row[2], row[3])

            f.close()
            return MyEpisode.wentIssue()
        else:
            #this is a move, return data of issue
            return MyMovie.wentIssue()
    return movie().wentIssue()
    
#Функция поиска по фразе сериала и ключевой фразы дейстия, например "КОГДА появится НОВАЯ серия ТЕОРИИ БОЛЬШОГО ВЗРЫВА 
def CoreSearch(text):
    #lookinc for a name (fist stage)
    filmId = SearchName(text)
    if filmId == -1:
        return "Простите, я не нашла такого фильма или сериала, попробуйте еще раз."
    #looking for an action, if we do not have an action return -2
    action = SearchAction(text)
    if action == -1:
        return "Простите, я не поняла что нужно сделать, уточните свой вопрос."
    #looking for advanced action in the phrase
    time = SeachActionTimeDetection(text)
    #core logic
    return filmSearch(filmId, action, time)
        
        #this is time, checking advanceAction and if not, assume we are looking for date of issue
        #if AdvanceAction 
#a = CoreSearch("Когда выйдет игра престолов?")
#print(a)
