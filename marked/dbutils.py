#encoding=utf-8

from MysqlObj import *
import json

MYSQL_HOST = '127.0.0.1'
MYSQL_DB = 'sae_marked'
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

def insertRawPosts(favorites):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    for fav in favorites:
        db.insert('raw_posts', {'content': json.dumps(fav)})

def getFirstRawPost():
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getOne('raw_posts')

def getRawPosts():
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getAll('raw_posts')

def insertUniqRawPosts(favorites):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    for id in favorites:
        db.insert('uniq_raw_posts', {'id': id, 'content': favorites[id]})

def getUniqRawPosts(where=None):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getAll('uniq_raw_posts', where=where)

def insertTags(tags):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    for id in tags:
        try:
            db.insert('tags', {'id': id, 'name': tags[id]})
        except Exception, e:
            print "tag exists"


def getTags(tids):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    if len(tids) == 0:
        return {}

    res = db.getAll('tags', where=["id in (%s)" % ','.join(['%s' for i in range(0, len(tids))]), tids])
    tags = {}
    for row in res:
        tags[row.id] = row.name
    return tags

def insertPostsTags(posts_tags):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    for pid in posts_tags:
        for tid in posts_tags[pid]:
            db.insert('posts_tags', {'pid': pid, 'tid': tid})

def getPostsTags(pids):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    if len(pids) == 0:
        return {}, {}

    res = db.getAll('posts_tags', where=["pid in (%s)" % ','.join(['%s' for i in range(0, len(pids))]), pids])

    posts_tags = {}
    tagids = {}
    for row in res:
        if not posts_tags.has_key(row.pid):
            posts_tags[row.pid] = []
        posts_tags[row.pid].append(row.tid)
        tagids[row.tid] = 1

    return posts_tags, getTags(tagids.keys())

def  insertPosts(posts):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    for post in posts:
        db.insert('posts', post)

def getPosts(startpos=0, num=25):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getAll('posts', order=['id', 'DESC'], limit=[startpos, num])

def getPostsCount():
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    res = db.getOne('posts', fields=['count(*) as cnt'])
    return res.cnt

def getPostsByIds(ids):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    if len(ids) == 0:
        return []

    return db.getAll('posts', where=["id in (%s)" % ','.join(['%s' for i in range(0, len(ids))]), ids])

def getPostsByTag(tid, startpos=0, num=25):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    posts_tags = db.getAll('posts_tags', where=['tid=%s', [tid]], order=['pid', 'DESC'], limit=[startpos, num])
    return getPostsByIds([post_tag.pid for post_tag in posts_tags])

def getPostsCountByTag(tid):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    res = db.getOne('posts_tags', fields=['count(*) as cnt'], where=['tid=%s', [tid]])
    return res.cnt

