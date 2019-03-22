# -*- coding:  Windows-1251 -*-
import config
import sqlite3
import shelve
import requests
import urllib3
import subprocess
from config import shelve_name, database_name
from SQLighter import SQLighter
from tqdm import tqdm
from pydub import AudioSegment

API_KEY = 'trnsl.1.1.20160525T095111Z.10b0e8e1060fde2f.61d59129754acbc4104754f5a4e7b045c32ef1a5' # api key for ya translate
API_KEY_VOICE = '3f874a4e-723d-48cd-a791-7401169035a0' #api for voice

def reverse(colid):
    if colid == 1:
       row = 2
    else:
       row = 1
    return row

def count_rows(tname):
    db = SQLighter(database_name)
    rowsnum = db.count_rows(tname)
    with shelve.open(shelve_name) as storage:
        storage['rows_count'] = rowsnum
    return rowsnum

def get_rows_count():
    with shelve.open(shelve_name) as storage:
        rowsnum = storage['rows_count']
    return rowsnum

def FindSideB(newB,sideb):
    result = 0
    for t in sideb.split(';'):
       if t.upper().strip(' ') == newB.upper():
          result = 1
    return result

def GetVoice(word):  # https://tts.voicetech.yandex.net/generate?text=text&key=3f874a4e-723d-48cd-a791-7401169035a0&format=mp3&speaker=zahar&emotion=good
    req =('https://tts.voicetech.yandex.net/generate?ie=UTF-8&text='+word+'&key='+API_KEY_VOICE+'&format=mp3&speaker=ermil&emotion=neutral')
    response = requests.get(req, stream=True) 
    with open("yasound.mp3", "wb") as handle:
       for data in tqdm(response.iter_content()):
          handle.write(data)
    AudioSegment.from_file('yasound.mp3').export("yasound.ogg", format="ogg")



def yatranslate(word):
    req =('https://translate.yandex.net/api/v1.5/tr.json/translate?lang=ru&options=1&key='+API_KEY+'&text='+word)
    yaanswer = requests.get(req) #
    lang = 1 # if ENG
    if (yaanswer.text.find('ru-ru') > 0):
       req =('https://translate.yandex.net/api/v1.5/tr.json/translate?lang=en&options=1&key='+API_KEY+'&text='+word)
       yaanswer = requests.get(req)   
       lang = 0 # if RU  
    result = yaanswer.text[(yaanswer.text.find('[')+2):(len(yaanswer.text)-3)]
    return result, lang
    
