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
# delw [����� �� ����] - ������� �� ���� ���������� ����� �� ����� ����������
# yatr [text] - Translate word (en-ru/ru-en)
# setautodelay - set parameter auto_delay(int)


# ��������� ��� ������������ � ������� ������� /settings ������� ��� ��������� 
# �������� ����� ����� ?
# �������� �� ������ �� ���� �������� ����� ������
# �������� ���� ��� �������� ������� ������� ������� ���� ������
# ������ �������� ����� ����� send_voice ogg, ������� �� ��������


# ���������

@bot.message_handler(commands=['setautodelay'])
def send_test_messages(message):	
    new_delay = message.text[(message.text.find(' ')+1):len(message.text)]
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    auto_delay, auto_starttime, auto_endtime, auto_enabled = db_worker.LoadSettings(message.chat.id)
    db_worker.SaveSettings(message.chat.id,new_delay,auto_starttime, auto_endtime, auto_enabled)
    db_worker.close()
    bot.send_message(message.chat.id, '#Settings: set auto_delay to ' + str(new_delay)) 

# ���������� �������� ������	
@bot.message_handler(commands=['sayit'])
def send_test_messages(message):
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    if Utils.count_rows(message.chat.id) == 0:
       bot.send_message(message.chat.id, '��� �� ����� ��������')
       db_worker.close()
       return
    rowid,colid= db_worker.get_last_rowid(message.chat.id)
    row = db_worker.select_single(rowid,message.chat.id)  # ���� ������ ���. ���������  
    Utils.GetVoice(row[1])
    voice = open('yasound.ogg', 'rb')
    bot.send_voice(message.chat.id, voice)
    # ������������� �� ��
    db_worker.close()

@bot.message_handler(commands=['help'])
def send_test_messages(message):
   helptext = ''' �������:
/n > ����� ��� ��������� ��������
/a > ���������� �����
/h > ���������
/auto > �������������� ���\����
/addmanual > �������� �������� �������. [text1 �����1]
/addya > �������� ����� ��������. [text1, �����1, ��������������1]
/delw > ������� �����. [text1]
/yatr > ��������� ������� �����
/setautodelay > ���������� ������� �������� �������������� � �������� [integer]
'''
   bot.send_message(message.chat.id,helptext)

@bot.message_handler(commands=['delw'])
def send_test_messages(message):
   db_worker = SQLighter(config.database_name)
   db_worker.TableExists(message.chat.id)
   sidea = message.text[6:len(message.text)] 
   if len(db_worker.FindSideA(sidea,message.chat.id)) == 0:
      bot.send_message(message.chat.id, '��������� �������� �� ����������.')
   else:
      db_worker.delete_from_DB(sidea.lower(),message.chat.id)
      bot.send_message(message.chat.id, sidea+' ������� �������.')
   db_worker.close()
										
@bot.message_handler(commands=['addmanual'])
def send_test_messages(message):
        db_worker = SQLighter(config.database_name)
        db_worker.TableExists(message.chat.id)
        sidea = message.text[11:(message.text.find(' ', 5))]
        sideb = message.text[((message.text.find(' ', 5))+1):len(message.text)]
        db_worker.AddCardstoDB(str(db_worker.getlastid(message.chat.id)+1),sidea.lower(),sideb.lower(),message.chat.id)
        Utils.count_rows(message.chat.id)
        bot.send_message(message.chat.id, '����� �������� ['+sidea+' - '+sideb+'] ������� ���������. ������� ���-�� ��������: '+str(Utils.count_rows(message.chat.id)))
        db_worker.close()

@bot.message_handler(commands=['addya']) # ����� ��� ����� ����� ������� ��� ����� �����
def send_test_messages(message):
        fullt = message.text[7:len(message.text)].split(',') # text1 text2 text3  #sidea = message.text[7:len(message.text)] 
        if len(fullt[0].strip(' ')) < 2:
           bot.send_message(message.chat.id, '������������ ��������� �������. /addya [��������]')
           return
        db_worker = SQLighter(config.database_name)
        db_worker.TableExists(message.chat.id)        
        for text in fullt:
           sidea = text.strip(' ')
           side, lang = Utils.yatranslate(sidea) #lang=1 eng, lang=0 ru sidea  ����� ������ ����
           if lang == 1:
                 sideb = side
           else:
                 sideb = sidea
                 sidea = side
           if sidea == sideb :
              bot.send_message(message.chat.id, '���������� ������� �� ������. �������� ������ � ���������: '+sidea+' <> '+sideb)
        # ����� ��������� ���� �� ������ � ����, ���� ��� �� ��������� sidea ������ ENG
           SideA_in_DB = db_worker.FindSideA(sidea,message.chat.id)
           if len(SideA_in_DB) == 0: # ���� �� ����� ������ � ����
                db_worker.AddCardstoDB(str(db_worker.getlastid(message.chat.id)+1),sidea.lower(),sideb.lower(),message.chat.id) # ������� ����� ������ id last+1
                Utils.count_rows(message.chat.id)
                bot.send_message(message.chat.id, '����� �������� ['+sidea+' - '+sideb+'] ������� ���������. ������� ���-�� ��������: '+str(Utils.count_rows(message.chat.id)))
           else:
                # ���� ����� �� �������� ������� � ��� ������������ (���� ��� ��� ������ ��������!!!!)
                SideA_in_DB = SideA_in_DB[0]
                if Utils.FindSideB(sideb,SideA_in_DB[2]) == 1:
                   bot.send_message(message.chat.id, '�������� ['+sidea+' - '+SideA_in_DB[2]+ '] ��� ����������')   
                else:    
                   db_worker.UpdateSideB(SideA_in_DB[0],(SideA_in_DB[2]+'; '+sideb.lower()),message.chat.id)
                   Utils.count_rows(message.chat.id)
                   bot.send_message(message.chat.id, '�������� ['+sidea+' - '+SideA_in_DB[2]+'; '+sideb+'] ������� ���������. ������� ���-�� ��������: '+str(Utils.count_rows(message.chat.id)))
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
       bot.send_message(message.chat.id, '��� �� ����� ��������')
       db_worker.close()
       return
    rowid,colid = db_worker.get_last_rowid(message.chat.id)
    row = db_worker.select_single(rowid,message.chat.id)  # ���� ������ ���. ���������   
    bot.send_message(message.chat.id, '���������� �����: '+row[Utils.reverse(colid)])
    # ������������� �� ��
    db_worker.close()
    if (auto_enabled == '0'):
       checkcard(message)

@bot.message_handler(commands=['h'])
def send_test_messages(message):
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    if Utils.count_rows(message.chat.id) == 0:
       bot.send_message(message.chat.id, '��� �� ����� ��������')
       db_worker.close()
       return
    rowid,colid= db_worker.get_last_rowid(message.chat.id)
    row = db_worker.select_single(rowid,message.chat.id)  # ���� ������ ���. ���������    
    help_answer = row[Utils.reverse(colid)]
    for a in help_answer:
       if random.randint(1,2) == 1:
          help_answer = help_answer.replace(a,'.')
    bot.send_message(message.chat.id, '���������: '+ help_answer)
    # ������������� �� ��
    db_worker.close()


@bot.message_handler(commands=['n'])
def checkcard(message):
    # ������������ � ��
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    # �������� ��������� ������ �� ��
    if Utils.count_rows(message.chat.id) == 0:
       bot.send_message(message.chat.id, '��� �� ����� ��������')
       db_worker.close()
       return
    colid = random.randint(1,2) # �������� ��������� ������� ����\��� (��������� ��� ������� � ����������)       
    row = db_worker.select_random(message.chat.id) # ����������� ���������� ��������� ������ �� ��
    #Utils.setrID(row[0],rrow) # ��������� ����� ������ � ������� ������������
    db_worker.set_last_rowid(message.chat.id, row[0],colid) # ���������� � ���� id ������ � �������
    if colid == 2: #���� ������� ������, � ������� ��������� �� ����� ���� �� ��������
        sideb_list = row[colid].split(';') # ������� ������ �� ; � ����
        bot.send_message(message.chat.id, '# '+sideb_list[random.randint(1,len(sideb_list))-1])
    else: 
        bot.send_message(message.chat.id, '# '+row[colid]) # ���������� sidea �������
    # ������������� �� ��
    db_worker.close()

@bot.message_handler(commands=['auto'])
def send_test_messages(message):
    global threads
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    auto_delay, auto_starttime, auto_endtime, auto_enabled = db_worker.LoadSettings(message.chat.id)
    print
    if str(auto_enabled) == '0':
       bot.send_message(message.chat.id, '�������������� �������� (������ '+str(auto_delay)+' ��� � '+str(auto_starttime)+' ����� �� '+ str(auto_endtime)+' �����)')
       db_worker.SaveSettings(message.chat.id,auto_delay,auto_starttime, auto_endtime, 1)
       go(message,1)
    #   threads.append([])
    #   t = threading.Timer(auto_delay, lambda: go(message)) # creating thread
    #   threads[len(threads)-1].append(message.chat.id)
    #   threads[len(threads)-1].append(t)
    #   t.start() 
    elif str(auto_enabled) == '1':
       bot.send_message(message.chat.id, '�������������� ���������')
       db_worker.SaveSettings(message.chat.id,auto_delay,auto_starttime, auto_endtime, 0)
       go(message,0)
    #   for thr in threads:
    #       if thr[0] == message.chat.id:
    #          thr[1].cancel()
    #          thr.remove
    db_worker.close()

# ��� ����� ��������� �����, ����� ������ ����� ����� ����� �������. �������� ��� ���� 1 �� 1 ��� force_reply � ������
@bot.message_handler(content_types=["text"])
def checkanswer(message): 
  # ������������ � ��
    Right = 0
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    auto_delay, auto_starttime, auto_endtime, auto_enabled = db_worker.LoadSettings(message.chat.id)
    if Utils.count_rows(message.chat.id) == 0:
       bot.send_message(message.chat.id, '��� �� ����� ��������')
       db_worker.close()
       return
    rowid,colid= db_worker.get_last_rowid(message.chat.id)
    row = db_worker.select_single(rowid,message.chat.id)  # ���� ������ ���. ���������
    # ������� ����� ������� �������� ���������
    if colid == 2: # ���� ������� B �� ���� ��������� ��� ���������
       for answ in row[colid].split(';'):
          if message.text.upper() == answ.upper().strip(' '):
              Right = 1 #�������� ���������
    else:
       if message.text.upper() == row[colid].upper(): # ��������� �����
          Right = 1
    # ������������� �� ��
    db_worker.close()
    if Right == 1:
       bot.send_message(message.chat.id, '���������!')
       if (auto_enabled == '0'):
          checkcard(message)
    else:
       bot.send_message(message.chat.id, '�����������!')

def go(message, enable):
    db_worker = SQLighter(config.database_name)
    db_worker.TableExists(message.chat.id)
    auto_delay, auto_starttime, auto_endtime, auto_enabled = db_worker.LoadSettings(message.chat.id)
    db_worker.close() 
    if (str(auto_enabled) == '1') and (datetime.now().hour > auto_starttime) and (datetime.now().hour < auto_endtime) : # try if thread isnot alive and /auto is ON 
        checkcard(message) # ��������� �-� /n � ��������� message (������ ����� message.chat.id)
    if enable == 1:
       threading.Timer(auto_delay, lambda: go(message,1)).start()

if __name__ == '__main__':
    random.seed()
    bot.polling(none_stop=True)