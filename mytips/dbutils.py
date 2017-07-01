#encoding=utf-8

from MysqlObj import *

MYSQL_HOST = '127.0.0.1'
MYSQL_DB = 'sae_mytips'
MYSQL_USER = 'root'
MYSQL_PASS = '123456'
MYSQL_PORT = '3306'


def insertOrUpdateUser(user_dict, keys):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    db.insertOrUpdate('users', user_dict, keys)

def getUser(id):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getOne('users', where=['id=%s', [id]])


def insertTags(tags):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    tagids = []
    for name in tags:
        try:
            cur = db.insert('tags', {'name': name})
            tagids.append(cur.lastrowid)
        except Exception, e:
            tagids.append(getTagIdByName(name))
    return tagids

def getTagIdByName(name):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    tag = db.getOne('tags', where=['name=%s', [name]])
    return tag.id

def getTags(tids):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    if len(tids) == 0:
        return {}

    res = db.getAll('tags', where=["id in (%s)" % ','.join(['%s' for i in range(0, len(tids))]), tids])
    tags = {}
    for row in res:
        tags[row.id] = row.name
    return tags

def insertPostsTags(posts_tags, uid):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    for pid in posts_tags:
        for tid in posts_tags[pid]:
            db.insert('posts_tags', {'pid': pid, 'tid': tid, 'uid': uid})

def deletePostTags(postid):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    db.delete('posts_tags', where=['pid=%s', [postid]])

def getPostsTags(pids):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    if len(pids) == 0:
        return {}, {}

    res = db.getAll('posts_tags', where=["pid in (%s)" % ','.join(['%s' for i in range(0, len(pids))]), pids])
    if not res:
        return {}, {}

    posts_tags = {}
    tagids = {}
    for row in res:
        if not posts_tags.has_key(row.pid):
            posts_tags[row.pid] = []
        posts_tags[row.pid].append(row.tid)
        tagids[row.tid] = 1

    return posts_tags, getTags(tagids.keys())

def  insertPost(post):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.insert('posts', post).lastrowid

def deletePost(postid):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    db.delete('posts', where=['id=%s', [postid]])

def getPosts(uid, startpos=0, num=25):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    return db.getAll('posts', where=['uid=%s', [uid]], order=['id', 'DESC'], limit=[startpos, num])

def getPostsCount(uid):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    res = db.getOne('posts', fields=['count(*) as cnt'], where=['uid=%s', [uid]])
    return res.cnt

def getPostsByIds(ids):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    if len(ids) == 0:
        return []

    return db.getAll('posts', where=["id in (%s)" % ','.join(['%s' for i in range(0, len(ids))]), ids])

def getPostsByTag(tid, uid, startpos=0, num=25):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    posts_tags = db.getAll('posts_tags', where=['tid=%s and uid=%s', [tid, uid]], order=['pid', 'DESC'], limit=[startpos, num])
    return getPostsByIds([post_tag.pid for post_tag in posts_tags])

def getPostsCountByTag(tid, uid):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    res = db.getOne('posts_tags', fields=['count(*) as cnt'], where=['tid=%s and uid=%s', [tid, uid]])
    return res.cnt

def getAllTagsCounts(uid):
    db = MysqlObj(host=MYSQL_HOST, db=MYSQL_DB, user=MYSQL_USER, passwd=MYSQL_PASS, port=int(MYSQL_PORT))
    cur = db.query('select a.tid, a.cnt from (select tid, count(*) as cnt from posts_tags where uid = "%s" group by tid) a where a.cnt > 1' % uid)
    result = cur.fetchall()
    tcnt = {}
    for tid, cnt in result:
        tcnt[tid] = cnt

    tags = db.getAll('tags')
    res = []
    for tag in tags:
        if tag.id in tcnt:
            res.append([tag.id, tag.name, tcnt[tag.id]])

    return sorted(res, key=lambda x: x[2], reverse=True)
