#encoding=utf-8

from MysqlObj import *
import time

MYSQL_HOST = '127.0.0.1'
MYSQL_DB = 'sae_loveses'
MYSQL_USER = 'root'
MYSQL_PASS = ''
MYSQL_PORT = '3306'


def insertOrUpdateUser(user_dict, keys):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    db.insertOrUpdate('users', user_dict, keys)
    db.commit()
    db.end()

def getUser(id):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getOne('users', where=['id=%s', [id]])

##########

def getTvshow(uid):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getAll('tvshow', where=['uid=%s', [uid]], order=['name'])

def insertTvshow(uid, name, season, episode):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    db.insert('tvshow', {'uid': uid, 'name': name, 'season': season, 'episode': episode})

def changeEpisode(id, episode, n):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    if episode + n <= 0:
        return -1
    else:
        return db.update('tvshow', {'episode': episode + n}, where=("id = %s", [id]))

def toggleDone(id, flag):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.update('tvshow', {'isdone': flag}, where=("id = %s", [id]))

def deleteTvshow(id):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.delete('tvshow', where=("id = %s", [id]))

##########

def getPasswd(uid):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getAll('passwd', where=['uid=%s', [uid]], order=['project'])

def insertPasswd(uid, project, idno, passwd):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    db.insert('passwd', {'uid': uid, 'project': project, 'idno': idno, 'passwd': passwd})

def changePasswd(id, passwd):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.update('passwd', {'passwd': passwd}, where=("id = %s", [id]))

def deletePasswd(id):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.delete('passwd', where=("id = %s", [id]))

##########

def getMedicine(uid):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getAll('medicine', where=['uid=%s', [uid]], order=['statdate', 'ASC'])

def insertMedicine(uid, statdate, stattype, medicine=0):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
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
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.update('medicine', {'medicine': medicine}, where=("id = %s", [id]))

##########

def getAction(uid, statdate):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getAll('action', where=['uid=%s and statdate=%s', (uid, statdate)], order=['stattime', 'ASC'])

def insertAction(uid, statdate, stattime, action):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    db.insert('action', {'uid': uid, 'statdate': statdate, 'stattime': stattime, 'action': action})

def deleteAction(id):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.delete('action', where=("id = %s", [id]))

def changeAction(id, stattime):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.update('action', {'stattime': stattime}, where=("id = %s", [id]))

##########

def getSleep(uid, startdate, enddate):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getAll('sleeps', where=['uid=%s and statdate>=%s and statdate<=%s', (uid, startdate, enddate)], order=['statdate', 'DESC'])

def insertSleep(uid, statdate, longmins, shortmins):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    db.insert('sleeps', {'uid': uid, 'statdate': statdate, 'longmins': longmins, 'shortmins': shortmins})
