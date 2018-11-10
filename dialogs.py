#----Dialog functions
import random
    
quotes = open('quotes.txt').read().split('\n')
facts = open('facts.txt').read().split('\n')


def getRandomQuote():
    return random.choice(quotes).replace('...', '\n')
    

def getRandomFact():
    return random.choice(facts).replace('...', '\n')
    
def getQuestionQuote():
    question = ['А ещё я знаю цитаты. Хочешь одну?', 'Хочешь расскажу цитату?', 'А хочешь интересную цитату?', 'Могу кинуть цитату в твою копилку', 'Эй, друг, цитату хочешь?', 'Могу сказать тебе цитату из какого-нибудь сериала', 'У меня большой цитатник. Одолжить одну?', 'Хочешь процитирую кого-нибудь?']
    return random.choice(question)
    

def getQuestionFact():
    question = ['Я знаю много фактов. Рассказать?', 'Обожаю читать про сериалы. Хочешь расскажу что прочла сегодня', 'Я сегодня узнала, что сериалы кадый год бьют много рекордов. Хочешь расскажу?', 'Хочешь что-то расскажу?', 'Знание - сила. Поделиться своим?', 'Хочешь поговорить с девушкой. Могу подсказать интересный факт', 'Мне нравится твой выбор. Хочешь расскажу что-то интересное?']
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
    
print(getRandomQuestion())