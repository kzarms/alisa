#Модуль работы с внутренней базой данных
import csv
import io
#Функиця поиска фильма или сериала по таблице, возвращает ID сериала или фильма.
#   -1  Нет сериала
#   X   ID фильма или сериала
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
        'следующий': 2, 'следующая': 2, 'новый': 2, 'новая': 2, 'очередной': 2, 'очередная': 2, 'очередные': 2, 'будет': 2, 'появится': 2, 'выйдет': 2,
        'идет': 1, 'проходит': 1, 'показывают': 1, 'крутят': 1,
        'была': 0, 'прошла': 0, 'показали': 0, 'крутили': 0, 'прошлая': 0, 'прошедшая': 0, 'предыдущий': 0, 'предыдущая': 0,
    }
    text = text.lower()    
    WordList = text.split(" ")
    for word in WordList:
        word = word.strip(" ?!,;:")
        if word in TimeWords.keys():
            return TimeWords[word]
    return -1 

#print(SearchName("когда во все тяжкие большого взрыва"))
#print(SeachActionTimeDetection("ГДs сока сколь;в ы новый когда же ты где?"))
#print(SearchAction("ГДs сока сколь;в ы когда же ты где?"))

def filmSearch(id, action, time):
    f = open('films.csv', mode="r", encoding="utf-8")
    films = csv.reader(f, delimiter='\t')
    for row in films:
        if id == row[0]:
            movie = row[:]
            break
    f.close()
    #We done with film search and now lookig for an answer
    if (action == 0) and (time == 2):
        #looking for the next seies
        if movie[1] == '1':
            #this is serial, looking for the next episode in the different csv file
            f = open('episodes.csv', mode="r", encoding="utf-8")
            episodes = csv.reader(f, delimiter='\t')
            episode = []
            for row in episodes:
                if movie[2] == row[1]:
                    episode = row[:]
            f.close()
            return episode
        else:
            #this is a move, return data of issue
            return movie
        
#Функция поиска по фразе сериала и ключевой фразы дейстия, например "КОГДА появится НОВАЯ серия ТЕОРИИ БОЛЬШОГО ВЗРЫВА 
def CoreSearch(text):
    #lookinc for a name (fist stage)
    filmId = SearchName(text)
    if filmId == -1:
        return -1
    #looking for an action, if we do not have an action return -2
    action = SearchAction(text)
    if action == -1:
        return -2
    #looking for advanced action in the phrase
    time = SeachActionTimeDetection(text)
    #core logic
    return filmSearch(filmId, action, time)
        
        #this is time, checking advanceAction and if not, assume we are looking for date of issue
        #if AdvanceAction 
#print(CoreSearch("Когда выйдет мстители война бесконечности?"))