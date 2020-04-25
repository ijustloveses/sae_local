#encoding=utf-8

from Sqlite3Obj import *
import time


def insertOrUpdateUser(user_dict, keys):
    db =Sqlite3Obj("sae_loveses.db")
    db.insertOrUpdate('users', user_dict, keys)
    db.commit()
    db.end()

def getUser(id):
    db =Sqlite3Obj("sae_loveses.db")
    return db.getOne('users', where=['id=?', [id]])

##########

def getTvshow(uid):
    db =Sqlite3Obj("sae_loveses.db")
    return db.getAll('tvshow', where=['uid=?', [uid]], order=['name'])

def insertTvshow(uid, name, season, episode):
    db =Sqlite3Obj("sae_loveses.db")
    db.insert('tvshow', {'uid': uid, 'name': name, 'season': season, 'episode': episode})

def changeEpisode(id, episode, n):
    db =Sqlite3Obj("sae_loveses.db")
    if episode + n <= 0:
        return -1
    else:
        return db.update('tvshow', {'episode': episode + n}, where=("id = ?", [id]))

def toggleDone(id, flag):
    db =Sqlite3Obj("sae_loveses.db")
    return db.update('tvshow', {'isdone': flag}, where=("id = ?", [id]))

def deleteTvshow(id):
    db =Sqlite3Obj("sae_loveses.db")
    return db.delete('tvshow', where=("id = ?", [id]))

##########

def getPasswd(uid):
    db =Sqlite3Obj("sae_loveses.db")
    return db.getAll('passwd', where=['uid=?', [uid]], order=['project'])

def insertPasswd(uid, project, idno, passwd):
    db =Sqlite3Obj("sae_loveses.db")
    db.insert('passwd', {'uid': uid, 'project': project, 'idno': idno, 'passwd': passwd})

def changePasswd(id, passwd):
    db =Sqlite3Obj("sae_loveses.db")
    return db.update('passwd', {'passwd': passwd}, where=("id = ?", [id]))

def deletePasswd(id):
    db =Sqlite3Obj("sae_loveses.db")
    return db.delete('passwd', where=("id = ?", [id]))

##########

def getMedicine(uid):
    db =Sqlite3Obj("sae_loveses.db")
    return db.getAll('medicine', where=['uid=?', [uid]], order=['statdate', 'ASC'])

def insertMedicine(uid, statdate, stattype, medicine=0):
    db =Sqlite3Obj("sae_loveses.db")
    db.insert('medicine', {'uid': uid, 'statdate': statdate, 'stattype': stattype, 'medicine': medicine})

def initmedicine(uid):
    ts = time.mktime(time.localtime())
    for i in range(90):
        dt = time.strftime("%Y-%m-%d", time.localtime(ts + i * 86400))
        # 前90天，20天吃10天停
        if i % 30 < 20:
            insertMedicine(uid, dt, True, 0)
        else:
            insertMedicine(uid, dt, False, 0)

def changeMedicine(id, medicine):
    db =Sqlite3Obj("sae_loveses.db")
    return db.update('medicine', {'medicine': medicine}, where=("id = ?", [id]))

##########

def getAction(uid, statdate):
    db =Sqlite3Obj("sae_loveses.db")
    return db.getAll('action', where=['uid=? and statdate=?', (uid, statdate)], order=['stattime', 'ASC'])

def insertAction(uid, statdate, stattime, action):
    db =Sqlite3Obj("sae_loveses.db")
    db.insert('action', {'uid': uid, 'statdate': statdate, 'stattime': stattime, 'action': action})

def deleteAction(id):
    db =Sqlite3Obj("sae_loveses.db")
    return db.delete('action', where=("id = ?", [id]))

def changeAction(id, stattime):
    db =Sqlite3Obj("sae_loveses.db")
    return db.update('action', {'stattime': stattime}, where=("id = ?", [id]))

##########

def getSleep(uid, startdate, enddate):
    db =Sqlite3Obj("sae_loveses.db")
    return db.getAll('sleeps', where=['uid=? and statdate>=? and statdate<=?', (uid, startdate, enddate)], order=['statdate', 'DESC'])

def insertSleep(uid, statdate, longmins, shortmins):
    db =Sqlite3Obj("sae_loveses.db")
    db.insert('sleeps', {'uid': uid, 'statdate': statdate, 'longmins': longmins, 'shortmins': shortmins})
