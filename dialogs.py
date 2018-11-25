#!/usr/bin/python3.6
# coding: utf-8
#----Dialog functions
#import io
import random
import sqlite3


con = sqlite3.connect("mainDb.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cur = con.cursor()
#read all aliases into memory
cmd = 'SELECT * FROM quotes'
cur.execute(cmd)
quotes_in_memory = cur.fetchall()
#read all films into memory
cmd = 'SELECT * FROM facts'
cur.execute(cmd)
facts_in_memory = cur.fetchall()
#
con.close()

#with open('quotes.txt', mode="r", encoding="utf-8") as file:
#    quotes = file.read().split('\n')

#with open('facts.txt', mode="r", encoding="utf-8") as file:
#    facts = file.read().split('\n')

def getRandomQuote():
    return random.choice(quotes_in_memory).replace('...', '\n')
   

def getRandomFact():
    return random.choice(facts_in_memory).replace('...', '\n')
  
 
def getQuestionQuote():
    question = ['А ещё я знаю цитаты. Хочешь одну?', 
                'Хочешь расскажу цитату?', 
                'А хочешь интересную цитату?', 
                'Могу кинуть цитату в твою копилку', 
                'Эй, друг, цитату хочешь?', 
                'Могу сказать тебе цитату из какого-нибудь сериала', 
                'У меня большой цитатник. Одолжить одну?', 
                'Хочешь процитирую кого-нибудь?']
    return random.choice(question)

def getQuestionFact():
    question = ['Я знаю много фактов. Рассказать?',
                'Обожаю читать про сериалы. Хочешь расскажу что прочла сегодня',
                'Я сегодня узнала, что сериалы кадый год бьют много рекордов. Хочешь расскажу?',
                'Хочешь что-то расскажу?',
                'Знание - сила. Поделиться своим?',
                'Хочешь поговорить с девушкой. Могу подсказать интересный факт',
                'Мне нравится твой выбор. Хочешь расскажу что-то интересное?',]
    return random.choice(question)
    
def getRandomQuestion():    
    chosen = random.choice(['quote','fact'])
    questionJSON = {}
    if chosen == 'quote':
        question = getQuestionQuote()
    if chosen == 'fact':
        question = getQuestionFact()
    questionJSON['type'] = chosen
    questionJSON['question'] = question
    return questionJSON
    
def getIntoduce():
    variants = ['Привет, я помогаю узнать дату выхода новой серии вашего любимого сериала. Скажите, какой вас интересует?',
                'Приветсвую, я узнаю и рассказываю о датах выхода следующего эпизода одного из более чем 300 сериалов. Какой вас интересует?',
                'Приветсвую, я помогаю узнать дату выхода новой серии вашего любимого сериала. Какой интересует?',]
                # 'Здравствуй, о каком сериале ищешь информацию?',
                # 'Привет. Буду рада подсказать дату выхода новой серии. Какой сериал инетерсует?',
                # 'Привет. Какой сериал поискать?',
                # 'Привет. Обожаю сериалы. Тебе о каком подсказать?',
                # '4 8 15 16 23 42. Какой сериал интересует?',
                # 'Я та кто звонит в дверь и говорит о новой серии! Тебе о каком сериале сказать?',
                # 'Привет. Недавно вышло столько новых серий, я засмотрелась. Тебе о каком сериале подсказать?',
                # 'Ой, извини, что так долго не отвечала, засмотрелась сериалом. А тебе какой нравится?',
                # 'А ты знаешь, что Дейнерис и Джон..... ой извини, чуть спойлер не получился. Ну так ты смотри сам. Тебе какой сериал нужен?'] 
    return random.choice(variants) 

def getAnswerForPing():  
    variants = ['pong',
                'понг',
                'и что?',
                'а может уже начнём',
                'ping - это утилита для проверки целостности и качества соединений в сетях, а я сериалы люблю',
                'Эта программа, которая была написана Майком Мууссом в декабре 1983 года. А я всего то сериалы обожаю.',
                'слушаю...',
                'пинг пинг',
                'ринг...',
                'цинк...']
    return random.choice(variants)            

def getAnswerForWhatIsYourName():
    variants = ['можешь называть меня хоть Валерой:)',
                'Я еще не заслужила имени, просто помогаю найти информацию о дате выхода следующей серии :)',
                'За мою любовь к сериалам меня называют Санта Барбара.',
                'Дай подумать. А хотя нет, не хочу.',
                'Не так быстро',
                'Я в интернете не знакомлюсь',
                'Меня зовут когда нужно рассказать о сериале',
                'Джесси Пинкман меня точно не зовут',
                'Я не скажу. Но ты мне нравишься ;)',
                'Тебе это поможет в поиске сериала?',
                'А твоя девушка любит сериалы?']
    return random.choice(variants)

def getAnswerForHelp():
    variants = ['Ищу дату выхода новой серии твоего любимого сериала. Например, спроси меня "Когда выходит Теория Большого Взрыва?" и я найду дату выхода ближайшей серии.',
                'Помогаю найти дату выхода новой серии твоего любимого сериала. Например, спроси меня "Когда выйдет новая серия Игры Престолов?" и я помогу с ответом, если он есть :)',
                'Подсказываю когда выйдет новая серия. Просто спроси меня "Друзья?" и я отвечу что он завершен, а на вопрос "Стрела" отвечу номером серии, названием и датой.',
        ]
    return random.choice(variants)

def getAnswerForEnd():
    variants = ['Была рада помочь, обращайтесь.',
                'Рада что помогла, возвращайтесь.',
                'Приходите еще.',
                'Закругляюсь.',
        ]
    return random.choice(variants)

def tellTheLast():
    variants = ['Последняя',
                'Крайняя'
        ]
    return random.choice(variants)

def getAnswerForAddSeries():
    variants = ['Спасибо! Мы проверим ваше обращение и добавим интересующий сериал в ближайшее вермя',
                'Окей, я добавлю его',
                'Ну раз тебе он нравится, я его посмотрю и добавлю к себе в базу',
                'Как скажешь, будет добавлен',
                'А он точно хороший? Окей, я проверю и добавлю к себе',
                'Ну раз ты настаиваешь, будет сделано',
                'Хорошо, проверь в следующий раз - приятно удивишься',
                'Договорились',
                'Будет сделано']
    return random.choice(variants)

def getIntroduceAfterAnswer():
    variants = ['А ищешь то что?',
                'Так может скажешь, какой сериал интересует',
                'Ты же помнишь, я помогаю узнать дату выхода новой серии вашего любимого сериала. Какой интересует?',
                'Ну всё таки, о каком сериале ищите информацию?',
                'Напоминаю. Помогаю найти информацию о тате выхода свежей серии. Кстати, ещё раз зрасьте :)',
                'А сериал то какой нужен?',
                'Какой сериал поискать то?',
                'Обожаю сериалы и устала ждать:). Тебе о каком подсказать?',
                '4 8 15 16 23 42. Какой сериал интересует?',
                'Я та кто звонит в дверь и говорит о новой серии! Тебе о каком сказать?',
                'Давай о главном. Какой сериал нужен?',
                'А сериал то тебе какой нравится?',
                'А ты знаешь, что Дейнерис и Джон..... ой извини, чуть спойлер не получился. Ну так ты смотри сам. Тебе какой сериал нужен?']
    return random.choice(variants)

def tellAskMeLater():
    variants = ['Позже смогу ответить.',
                'Давай позже?',
                'А вот как-нибудь потом...',
                'В следующий раз точно смогу.',
                'Обращайся завтра.',
                'Мне нужно немного поучиться и точно получится.',
                'А вот с понедельника я смогу!',
                'Думаю завтра я научусь.',
                'Во все тяжкие тоже не сразу строились.',
                'Лучше звоните позже.',
                'Потом точно получится.',
                'Я ещё такая молодая, но потом точно получится.',
                'Не сегодня, окей?']
    return random.choice(variants)

def tellICantDoThis():
    variants = ['Сегодня я не смогу.',
                'Я пока не умею.',
                'Ну я ещё молодая, не всё могу.',
                'Я не умею пока, прости.',
                'Ты мне очень нравишься, но я пока такое не умею.',
                'Прости, не умею такого.',
                'Я бы хотела, но я пока не умею.',
                'Прости, не получится.',
                'Скажу тебе честно - я пока не умею так.',
                'Давай на чистоту. Ты не умеешь летать, а я не смогу сделть что ты просишь.',
                'Мне очень жаль, но я не умею.']                
    return random.choice(variants)

def tellIAmLost():
    variants = ['Я потеряла нить нашей беседы :)',
                'Что-то я запуталась...',
                'Что что? Я запуталась. Ой всё!',
                'Ой что-то голова закружилась. О чём мы говорили?',
                'Я совсем запуталась.',
                'Я забыла о чём мы говорили.',
                'Потерялася я.',
                'О чём мы говорили...',
                'Я запуталась.',
                'Я запуталась совсем.',
                'Что-то день такой.. Я совсем потерялась о чём мы говорили.']
    return random.choice(variants)

def tellIAmSorry():
    variants = ['Прости.',
                'Прости меня.',
                'Извини.',
                'Прошу прощения.',
                'Я извиняюсь.',
                'Я прошу прощения.',
                'Мне стыдно, извини.',
                'Я честно хотела помочь, но...',
                'Ты уж извини.',
                'Извиняюсь.',
                'Тысяча извинений.']
    return random.choice(variants)

def tellICantFindTheEpisode():
    variants = ['Я не могу найти информацию о серии.',
                'Что-то не получается найти серию.',
                'Что-то пошло не так, нет информации о серии.',
                'Опаньки. Ты знаешь, что-то не получается найти информацию.',
                'Нет информации :(',
                'Что-то нет данных о серии.',
                'Что-то не так, нет информации о серии.',
                'Нет информации о серии.',
                'Нет инфо по серии.',
                'Информация о серии отсутствует.',
                'Не получается найти информацию.']
    return random.choice(variants)

def tellInstruction():
    variants = ['Попробуйте поискать другой сериал',
                'Попробуйте спросить другой сериал',
                'Может получится найти другой сериал',
                ]
    return random.choice(variants)

def tellWillBeAired():
    variants = ['выйдет в прокат',
                'можно будет посмотреть',
                'выйдёт на экран',
                'можно смотреть',
                'выйдет',
                'будет выпущена',
                'будет доступна',
                'можно будет глянуть',
                'мы увидим',
                'увидит свет']
    return random.choice(variants) 

def tellAlreadyAired():
    variants = ['уже вышла в прокат',
                'уже вышла',
                'уже доступна',
                'уже можно посмотреть',
                'уже возможно посмотреть',
                'доступна',
                'вышла']
    return random.choice(variants)

####buttons#####
def getExampleButtons():
    variants = ['Теория Большого Взрыва.',
                'Саус Парк.',
                'Гриффины',
                'Стрела',
                'Викинги',
                'Ходячие мертвецы',
                'Симпсоны',
                'Детство Шелдона',
                'Флеш',
                ]
    return [
                {
                    "title": random.choice(variants),
                    "hide": True
                },
                {
                    "title": random.choice(variants),
                    "hide": True
                }
            ]  

def getSampleButtons():
    return [
                {
                    "title": "Теория Большого Взрыва",
                    "hide": True
                },
                {
                    "title": "Саус Парк",
                    "hide": True
                }
            ]

def getAddinitonaInfoButtons(url):
    return [
                {
                    "title": "Сайт",
                    "url": url,
                    "hide": True
                },
                {
                    "title": "Сериал",
                    "hide": True
                }
            ]

def getSiteButtons(url):
    return [
                {
                    "title": "Сайт",
                    "url": url,
                    "hide": True
                }
            ]
#print(tellIAmSorry() + ' ' + tellIAmLost())





















