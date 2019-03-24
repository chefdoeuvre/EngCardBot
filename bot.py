# -*- coding: Windows-1251 -*-
from SQLighter import SQLighter
import random
import threading
import config
import telebot
import Utils
from datetime import datetime

global bot_enabled
bot_enabled = 0
global threads
threads = []
												
bot = telebot.TeleBot(config.token)										
		
# n - Start or Next card
# a - Right answer
# auto - Enable\disable repeat card every auto_delay sec
# addmanual [SideA SideB] - Add new card to db
# addya [Word1, Word2, The Phrase 3] - Add new card with yandex.translate
# delw [слово на англ] - удалить из базы английское слово со всеми переводами
# yatr [text] - Translate word (en-ru/ru-en)
# setautodelay - set parameter auto_delay(int)


# настройки все записываются в таблицу команда /settings выводит все настройки 
# добавить сразу текст ?
# проверка на дурака на всех моментах ввода команд
# написать хелп где опдробно описать принцип забития базы данных
# сделай отправку звука через send_voice ogg, проверь на телефоне


# Настройки

@bot.message_handler(commands=['setautodelay'])
def send_test_messages(message):	
    new_delay = message.text[(message.text.find(' ')+1):len(message.text)]
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    auto_delay, auto_starttime, auto_endtime, auto_enabled = db_worker.LoadSettings(message.chat.id)
    db_worker.SaveSettings(message.chat.id,new_delay,auto_starttime, auto_endtime, auto_enabled)
    db_worker.close()
    bot.send_message(message.chat.id, '#Settings: set auto_delay to ' + str(new_delay)) 

# обработчик основных команд	
@bot.message_handler(commands=['sayit'])
def send_test_messages(message):
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    if Utils.count_rows(message.chat.id) == 0:
       bot.send_message(message.chat.id, 'Нет ни одной карточки')
       db_worker.close()
       return
    rowid,colid= db_worker.get_last_rowid(message.chat.id)
    row = db_worker.select_single(rowid,message.chat.id)  # ищем строку исп. последней  
    Utils.GetVoice(row[1])
    voice = open('yasound.ogg', 'rb')
    bot.send_voice(message.chat.id, voice)
    # Отсоединяемся от БД
    db_worker.close()

@bot.message_handler(commands=['help'])
def send_test_messages(message):
   helptext = ''' Команды:
/n > Новая или следующая карточка
/a > правильный ответ
/h > подсказка
/auto > автоповторение вкл\выкл
/addmanual > добавить карточку вручную. [text1 слово1]
/addya > добавить новые карточки. [text1, слово1, словосочетание1]
/delw > удалить слово. [text1]
/yatr > проверить перевод слова
/setautodelay > установить зачение настроек автоповторения в секундах [integer]
'''
   bot.send_message(message.chat.id,helptext)

@bot.message_handler(commands=['delw'])
def send_test_messages(message):
   db_worker = SQLighter(config.database_name)
   db_worker.TableExists(message.chat.id)
   sidea = message.text[6:len(message.text)] 
   if len(db_worker.FindSideA(sidea,message.chat.id)) == 0:
      bot.send_message(message.chat.id, 'Указанной карточки не существует.')
   else:
      db_worker.delete_from_DB(sidea.lower(),message.chat.id)
      bot.send_message(message.chat.id, sidea+' успешно удалено.')
   db_worker.close()
										
@bot.message_handler(commands=['addmanual'])
def send_test_messages(message):
        db_worker = SQLighter(config.database_name)
        db_worker.TableExists(message.chat.id)
        sidea = message.text[11:(message.text.find(' ', 5))]
        sideb = message.text[((message.text.find(' ', 5))+1):len(message.text)]
        db_worker.AddCardstoDB(str(db_worker.getlastid(message.chat.id)+1),sidea.lower(),sideb.lower(),message.chat.id)
        Utils.count_rows(message.chat.id)
        bot.send_message(message.chat.id, 'Новая карточка ['+sidea+' - '+sideb+'] успешно добавлена. Текущее кол-во карточек: '+str(Utils.count_rows(message.chat.id)))
        db_worker.close()

@bot.message_handler(commands=['addya']) # слова или фразы через запятую или целый текст
def send_test_messages(message):
        fullt = message.text[7:len(message.text)].split(',') # text1 text2 text3  #sidea = message.text[7:len(message.text)] 
        if len(fullt[0].strip(' ')) < 2:
           bot.send_message(message.chat.id, 'Неправильный синтаксис команды. /addya [значение]')
           return
        db_worker = SQLighter(config.database_name)
        db_worker.TableExists(message.chat.id)        
        for text in fullt:
           sidea = text.strip(' ')
           side, lang = Utils.yatranslate(sidea) #lang=1 eng, lang=0 ru sidea  какой первый язык
           if lang == 1:
                 sideb = side
           else:
                 sideb = sidea
                 sidea = side
           if sidea == sideb :
              bot.send_message(message.chat.id, 'Корректный перевод не удался. Возможно ошибка в написании: '+sidea+' <> '+sideb)
        # здесь проверяем есть ли запись в базе, если нет то добавляем sidea всегда ENG
           SideA_in_DB = db_worker.FindSideA(sidea,message.chat.id)
           if len(SideA_in_DB) == 0: # если не нашел запись в базе
                db_worker.AddCardstoDB(str(db_worker.getlastid(message.chat.id)+1),sidea.lower(),sideb.lower(),message.chat.id) # создаем новую запись id last+1
                Utils.count_rows(message.chat.id)
                bot.send_message(message.chat.id, 'Новая карточка ['+sidea+' - '+sideb+'] успешно добавлена. Текущее кол-во карточек: '+str(Utils.count_rows(message.chat.id)))
           else:
                # если нашел то добавить перевод в уже существующую (если еще нет такого перевода!!!!)
                SideA_in_DB = SideA_in_DB[0]
                if Utils.FindSideB(sideb,SideA_in_DB[2]) == 1:
                   bot.send_message(message.chat.id, 'Карточка ['+sidea+' - '+SideA_in_DB[2]+ '] уже существует')   
                else:    
                   db_worker.UpdateSideB(SideA_in_DB[0],(SideA_in_DB[2]+'; '+sideb.lower()),message.chat.id)
                   Utils.count_rows(message.chat.id)
                   bot.send_message(message.chat.id, 'Карточка ['+sidea+' - '+SideA_in_DB[2]+'; '+sideb+'] успешно обновлена. Текущее кол-во карточек: '+str(Utils.count_rows(message.chat.id)))
        db_worker.close()

@bot.message_handler(commands=['yatr'])
def send_test_messages(message):
     word = message.text[5:len(message.text)] 
     answer = Utils.yatranslate(word)
     bot.send_message(message.chat.id,answer)

@bot.message_handler(commands=['a'])
def send_test_messages(message):
    global auto_start
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    auto_delay, auto_starttime, auto_endtime, auto_enabled = db_worker.LoadSettings(message.chat.id)
    if Utils.count_rows(message.chat.id) == 0:
       bot.send_message(message.chat.id, 'Нет ни одной карточки')
       db_worker.close()
       return
    rowid,colid = db_worker.get_last_rowid(message.chat.id)
    row = db_worker.select_single(rowid,message.chat.id)  # ищем строку исп. последней   
    bot.send_message(message.chat.id, 'Правильный ответ: '+row[Utils.reverse(colid)])
    # Отсоединяемся от БД
    db_worker.close()
    if (auto_enabled == '0'):
       checkcard(message)

@bot.message_handler(commands=['h'])
def send_test_messages(message):
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    if Utils.count_rows(message.chat.id) == 0:
       bot.send_message(message.chat.id, 'Нет ни одной карточки')
       db_worker.close()
       return
    rowid,colid= db_worker.get_last_rowid(message.chat.id)
    row = db_worker.select_single(rowid,message.chat.id)  # ищем строку исп. последней    
    help_answer = row[Utils.reverse(colid)]
    for a in help_answer:
       if random.randint(1,2) == 1:
          help_answer = help_answer.replace(a,'.')
    bot.send_message(message.chat.id, 'Подсказка: '+ help_answer)
    # Отсоединяемся от БД
    db_worker.close()


@bot.message_handler(commands=['n'])
def checkcard(message):
    # Подключаемся к БД
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    # Получаем случайную строку из БД
    if Utils.count_rows(message.chat.id) == 0:
       bot.send_message(message.chat.id, 'Нет ни одной карточки')
       db_worker.close()
       return
    colid = random.randint(1,2) # выбираем случайный столбец англ\рус (поставить тут условие в настройках)       
    row = db_worker.select_random(message.chat.id) # присваеваем переменной случайную строку из БД
    #Utils.setrID(row[0],rrow) # запиываем какую строку и сторону использовали
    db_worker.set_last_rowid(message.chat.id, row[0],colid) # записываем в базу id строки и колонку
    if colid == 2: #Если столбец второй, с русским переводом то берем одно из значений
        sideb_list = row[colid].split(';') # разбили строку по ; в лист
        bot.send_message(message.chat.id, '# '+sideb_list[random.randint(1,len(sideb_list))-1])
    else: 
        bot.send_message(message.chat.id, '# '+row[colid]) # отправляем sidea целиком
    # Отсоединяемся от БД
    db_worker.close()

@bot.message_handler(commands=['auto'])
def send_test_messages(message):
    global threads
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    auto_delay, auto_starttime, auto_endtime, auto_enabled = db_worker.LoadSettings(message.chat.id)
    print
    if str(auto_enabled) == '0':
       bot.send_message(message.chat.id, 'Автоповторение запущено (каждые '+str(auto_delay)+' сек с '+str(auto_starttime)+' часов до '+ str(auto_endtime)+' часов)')
       db_worker.SaveSettings(message.chat.id,auto_delay,auto_starttime, auto_endtime, 1)
       go(message,1)
    #   threads.append([])
    #   t = threading.Timer(auto_delay, lambda: go(message)) # creating thread
    #   threads[len(threads)-1].append(message.chat.id)
    #   threads[len(threads)-1].append(t)
    #   t.start() 
    elif str(auto_enabled) == '1':
       bot.send_message(message.chat.id, 'Автоповторение отключено')
       db_worker.SaveSettings(message.chat.id,auto_delay,auto_starttime, auto_endtime, 0)
       go(message,0)
    #   for thr in threads:
    #       if thr[0] == message.chat.id:
    #          thr[1].cancel()
    #          thr.remove
    db_worker.close()

# тут будем проверять ответ, когда пишешь любой текст кроме команды. Работает при чате 1 на 1 или force_reply в группе
@bot.message_handler(content_types=["text"])
def checkanswer(message): 
  # Подключаемся к БД
    Right = 0
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    auto_delay, auto_starttime, auto_endtime, auto_enabled = db_worker.LoadSettings(message.chat.id)
    if Utils.count_rows(message.chat.id) == 0:
       bot.send_message(message.chat.id, 'Нет ни одной карточки')
       db_worker.close()
       return
    rowid,colid= db_worker.get_last_rowid(message.chat.id)
    row = db_worker.select_single(rowid,message.chat.id)  # ищем строку исп. последней
    # смотрим какую сторону карточки проверяем
    if colid == 2: # если сторону B то надо проверять все вхождения
       for answ in row[colid].split(';'):
          if message.text.upper() == answ.upper().strip(' '):
              Right = 1 #ответили правильно
    else:
       if message.text.upper() == row[colid].upper(): # проверяем ответ
          Right = 1
    # Отсоединяемся от БД
    db_worker.close()
    if Right == 1:
       bot.send_message(message.chat.id, 'Правильно!')
       if (auto_enabled == '0'):
          checkcard(message)
    else:
       bot.send_message(message.chat.id, 'Неправильно!')

def go(message, enable):
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    auto_delay, auto_starttime, auto_endtime, auto_enabled = db_worker.LoadSettings(message.chat.id)
    db_worker.close() 
    if (str(auto_enabled) == '1') and (datetime.now().hour > auto_starttime) and (datetime.now().hour < auto_endtime) : # try if thread isnot alive and /auto is ON 
        checkcard(message) # запускаем ф-ю /n с последним message (оттуда берем message.chat.id)
    if enable == 1:
       threading.Timer(auto_delay, lambda: go(message,1)).start()

if __name__ == '__main__':
    random.seed()
    bot.polling(none_stop=True)
