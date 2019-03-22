# -*- coding:  utf-8 -*-
import sqlite3

class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def NewUser(self,tname): # создаем две таблицы дл€ каждого id чата дл€ карт и дл€ настроек
        with self.connection:
           command = 'CREATE TABLE if not exists "'+str(tname)+'" ("id" INTEGER, "SideA" TEXT, "SideB" TEXT)'
           self.cursor.execute(command).fetchall()
           command = 'CREATE TABLE if not exists "S'+str(tname)+'" ("Key" TEXT, "Value" INTEGER)'
           self.cursor.execute(command).fetchall()
           # заполн€ем таблицу с настройками стандартными значени€ми
           result = self.cursor.execute('SELECT * FROM "S'+str(tname)+'"').fetchall()
           if len(result) == 0:
              command = 'INSERT INTO "S'+str(tname)+'" (`key`,`Value`) VALUES ("auto_delay","300")'
              self.cursor.execute(command).fetchall()
              command = 'INSERT INTO "S'+str(tname)+'" (`key`,`Value`) VALUES ("auto_starttime","8")'
              self.cursor.execute(command).fetchall()
              command = 'INSERT INTO "S'+str(tname)+'" (`key`,`Value`) VALUES ("auto_endtime","22")'
              self.cursor.execute(command).fetchall()
              command = 'INSERT INTO "S'+str(tname)+'" (`key`,`Value`) VALUES ("lastrowid","1")'
              self.cursor.execute(command).fetchall()
              command = 'INSERT INTO "S'+str(tname)+'" (`key`,`Value`) VALUES ("lastcolid","1")'
              self.cursor.execute(command).fetchall()
              command = 'INSERT INTO "S'+str(tname)+'" (`key`,`Value`) VALUES ("auto_enabled","0")'
              self.cursor.execute(command).fetchall()

    def TableExists(self,tname): # существует ли таблица
        with self.connection:
           command = 'SELECT * FROM sqlite_master WHERE name = "' +str(tname)+'" and type="table"'
           result = self.cursor.execute(command).fetchall()
        if len(result) == 0:
           self.NewUser(tname)
        return len(result)

    def select_all(self,tname):
    #    """ ѕолучаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM "'+str(tname)+'"').fetchall()

    def select_single(self, rownum,tname):
      #  """ ѕолучаем одну строку с номером rownum """
        with self.connection:
            return self.cursor.execute('SELECT * FROM "'+str(tname)+'" WHERE id = ?', (rownum,)).fetchall()[0]

    def select_random(self,tname):
        with self.connection:
            return self.cursor.execute('SELECT * FROM "'+str(tname)+'" ORDER BY RANDOM() LIMIT 1').fetchall()[0]

    def count_rows(self,tname):
        #""" —читаем количество строк """
        with self.connection:
            result = self.cursor.execute('SELECT * FROM "'+str(tname)+'"').fetchall()
            return len(result)

    def AddCardstoDB(self,crows,sidea,sideb,tname):
        with self.connection:
            command = 'INSERT INTO "'+str(tname)+'" (`id`,`SideA`,`SideB`) VALUES ('+crows+',"'+sidea+'","'+sideb+'");'
            result = self.cursor.execute(command).fetchall()
            return len(result)

    def FindSideA (self, sidea,tname):  # ищем текст в sidea
        with self.connection:
            command = 'select * from "'+str(tname)+'" WHERE `SideA` LIKE "'+sidea+'"'
            result = self.cursor.execute(command).fetchall()
            return result

    def getlastid(self,tname):
        command = 'SELECT * FROM "'+str(tname)+'" ORDER BY id DESC LIMIT 1'
        result = self.cursor.execute(command).fetchall()
        if str(result) == '[]' :
           return 0
        else:
           return result[0][0]

    def delete_from_DB(self,sidea,tname):
        with self.connection:
           command = 'DELETE FROM "'+str(tname)+'" WHERE "SideA" = "'+sidea+'"'
           self.cursor.execute(command).fetchall()

    def UpdateSideB (self, idt, newtext,tname):
        with self.connection:
            command = 'UPDATE "'+str(tname)+'" SET `SideB`="'+newtext+'" WHERE "id" = "'+str(idt)+'"'
            self.cursor.execute(command).fetchall()

    def LoadSettings (self, tname):
        with self.connection:
            command = 'select * from "S'+str(tname)+'" WHERE `Key` = "auto_delay"'
            auto_delay = self.cursor.execute(command).fetchall()[0]
            command = 'select * from "S'+str(tname)+'" WHERE `Key` = "auto_starttime"'
            auto_starttime = self.cursor.execute(command).fetchall()[0]
            command = 'select * from "S'+str(tname)+'" WHERE `Key` = "auto_endtime"'
            auto_endtime = self.cursor.execute(command).fetchall()[0]
            command = 'select * from "S'+str(tname)+'" WHERE `Key` = "auto_enabled"'
            auto_enabled = self.cursor.execute(command).fetchall()[0]
            return auto_delay[1], auto_starttime[1], auto_endtime[1], auto_enabled[1]

    def get_last_rowid (self, tname):
        with self.connection:
            command = 'select * from "S'+str(tname)+'" WHERE `Key` = "lastrowid"'
            rowid = self.cursor.execute(command).fetchall()[0]
            command = 'select * from "S'+str(tname)+'" WHERE `Key` = "lastcolid"'
            colid = self.cursor.execute(command).fetchall()[0]
            return rowid[1],colid[1]

    def set_last_rowid (self, tname, lastrowid,lastcolid):
        with self.connection:
            command = 'UPDATE "S'+str(tname)+'" SET `Value`="'+str(lastrowid)+'" WHERE "Key" = "lastrowid"'
            self.cursor.execute(command).fetchall()
            command = 'UPDATE "S'+str(tname)+'" SET `Value`="'+str(lastcolid)+'" WHERE "Key" = "lastcolid"'
            self.cursor.execute(command).fetchall()

    def SaveSettings (self, tname, auto_delay, auto_starttime, auto_endtime, auto_enabled):
        with self.connection:
            command = 'UPDATE "S'+str(tname)+'" SET `Value`="'+str(auto_delay)+'" WHERE "Key" = "auto_delay"'
            self.cursor.execute(command).fetchall()
            command = 'UPDATE "S'+str(tname)+'" SET `Value`="'+str(auto_starttime)+'" WHERE "Key" = "auto_starttime"'
            self.cursor.execute(command).fetchall()
            command = 'UPDATE "S'+str(tname)+'" SET `Value`="'+str(auto_endtime)+'" WHERE "Key" = "auto_endtime"'
            self.cursor.execute(command).fetchall()
            command = 'UPDATE "S'+str(tname)+'" SET `Value`="'+str(auto_enabled)+'" WHERE "Key" = "auto_enabled"'
            self.cursor.execute(command).fetchall()
            
 
    def close(self):
        #""" «акрываем текущее соединение с Ѕƒ """
        self.connection.close()