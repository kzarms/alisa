# coding: utf-8
#
from __future__ import unicode_literals

import json
import logging
import random
from dbfunctions import *
from dialogs import *
import time

from flask import Flask, request
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Session storage
sessionStorage = {}

# Start flask with POST method listening
@app.route("/", methods=['POST'])

#main function
def main():
    # Hanle dialog
    def handle_dialog(req, res):
        #questionType = ''
        user_id = req['session']['user_id']
        if (req['session']['new']) and (req['request']['command'].lower() == ''):
            #New session and nothing in command, return welcome message
            res['response']['text'] = getIntoduce()
            res['response']['buttons'] = getExampleButtons()     
            return
        # Take user text
        #text = "Когда выходит теория большого взрыва?"
        text = req['request']['command'].lower()
        text = text.strip(' ?!,;:.')
        #Eto chto za pizdec?! :)
        #text = text.replace(",","").replace(".","").replace("?","").replace(":","")
                    
        #check for key words
        keywords = ['ping','пинг',
            '477b0c56-3dc5-4b69-ae85-a2eec9e378cd',
            'как тебя зовут','помощь','что ты умеешь',
            'привет','здравствуй','здравствуйте','хай','hi',
            'спасибо','благодарю',
            'все','выход','конец','завешить','стоп',
            'добавить сериал','подробнее','сериал','сайт']
        if text in keywords:
            #textKey = text.replace(",","").replace(",","")
            if (text == 'ping') or (text == 'пинг'):
                #res['response']['text'] = getAnswerForPing() + '\n' + '\n' + getIntroduceAfterAnswer()
                res['response']['text'] = 'Reply from new episod: bytes=32 time=46ms TTL=52'
                return 
            if text == '477b0c56-3dc5-4b69-ae85-a2eec9e378cd':
                for i in range(142):
                    addNewEpisodesFromURL(i)
                res['response']['text'] = 'End update'  
                return
            if (text == 'как тебя зовут'):
                res['response']['text'] = getAnswerForWhatIsYourName()
                return
            if (text == 'помощь'):
                res['response']['text'] = getAnswerForHelp()
                res['response']['buttons'] = getExampleButtons()
                return
            if (text == 'что ты умеешь'):
                res['response']['text'] = getAnswerForHelp()
                res['response']['buttons'] = getExampleButtons()                    
                return            
            if (text == 'привет' or text == 'здравствуй' or text == 'здравствуйте' or text == 'хай' or text == 'hi'):
                res['response']['text'] = getIntoduce()
                res['response']['buttons'] = getExampleButtons()
                return
            if (text == 'спасибо' or text == 'благодарю'):
                res['response']['text'] = getAnswerForEnd()
                res['response']['end_session'] = True
                return
            if (text == 'все' or text == 'выход' or text == 'конец' or text == 'завешить' or text == 'стоп'):
                res['response']['text'] = getAnswerForEnd()
                res['response']['end_session'] = True
                return
            if user_id not in sessionStorage:
                res['response']['text'] = tellIAmSorry() + ' ' + tellIAmLost()
                return            
            if (text == 'добавить сериал') and (sessionStorage[user_id] == 0):
                res['response']['text'] = getAnswerForAddSeries()
                return
            if text == 'подробнее':
                if sessionStorage[user_id] != 0:
                    res['response']['text'] = tellICantDoThis() + ' ' + tellAskMeLater()            
                else:
                    res['response']['text'] = tellIAmSorry() + ' ' + tellIAmLost()
                return
            if text == 'сериал':
                if sessionStorage[user_id] != 0:
                    res['response']['text'] = getFilmInfoLocal(sessionStorage[user_id])
                    res['response']['buttons'] = getSiteButtons(OfficialURL(sessionStorage[user_id]))
                else:
                    res['response']['text'] = tellIAmSorry() + ' ' + tellIAmLost()
                return
            if text == 'сайт':
                if sessionStorage[user_id] != 0:
                    res['response']['text'] = 'Желаю приятного просмотра.'
                    res['response']['end_session'] = True
                else:
                    res['response']['text'] = tellIAmSorry() + ' ' + tellIAmLost()
                return


        """        
        #---Check if user wants to listen to fact or quote
        questionJSON = getRandomQuestion()
        if (sessionStorage.get(user_id + '_q') != None) and (text in ['давай', 'расскажи', 'хочу', 'цитату', 'факт', 'конечно', 'ещё', 'еще']):
            if sessionStorage.get(user_id + '_q') == 'quote':
                if questionJSON['question'] == 'quote':
                    res['response']['text'] = getRandomQuote() + '\n' + 'Хочешь ещё одну?'
                else:
                    res['response']['text'] = getRandomQuote() + '\n' + questionJSON['question']
            if sessionStorage.get(user_id + '_q') == 'fact':
                if questionJSON['question'] == 'fact':
                    res['response']['text'] = getRandomFact() + '\n' + 'Хочешь ещё что-то узнать?'
                else:
                    res['response']['text'] = getRandomFact() + '\n' + questionJSON['question']
            
            sessionStorage[user_id + '_q'] = questionJSON['type']
            return
        sessionStorage[user_id + '_q'] = questionJSON['type']
        """
        #no more key works, execute seach function on top of this text
        result = CoreSearch(text)
        #tempLogFile:
        f = open('logs.txt', mode="a+", encoding="utf-8")
        csv_writer = csv.writer(f, lineterminator='\n', delimiter='\t')
        #
        if result['filmId'] == -1:
            res['response']['text'] =  tellIAmSorry() + ' ' + tellICantFindTheEpisode() + ' ' + tellInstruction()
            res['response']['buttons'] = getExampleButtons()
            csv_writer.writerow([False, user_id, text, req['meta']['client_id'], req['meta']['locale']],)
        else:            
            #save intId into dictionary
            sessionStorage[user_id] = result['filmId']
            res['response']['text'] = result['responce'] #+ '\n' + '\n' + questionJSON['question']
            res['response']['buttons'] = getAddinitonaInfoButtons(OfficialURL(result['filmId']))
            csv_writer.writerow([True, user_id, text, req['meta']['client_id'], req['meta']['locale']],)
        #Close file 
        f.close()        
        
    #logging.info('Request: %r', request.json)
    
    print('-------------------------------')
    print(request.json)
    print('-------------------------------')

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {}        
    }
    print(response)
    
    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

if __name__ == "__main__":
    app.debug = True
    app.run(host = '0.0.0.0')    
