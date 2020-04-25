#encoding=utf-8

from Sqlite3Obj import *


def insertOrUpdateUser(user_dict, keys):
    db =Sqlite3Obj("sae_mytips.db")
    db.insertOrUpdate('users', user_dict, keys)

def getUser(id):
    db =Sqlite3Obj("sae_mytips.db")
    return db.getOne('users', where=['id=?', [id]])


def insertTags(tags):
    db =Sqlite3Obj("sae_mytips.db")
    tagids = []
    for name in tags:
        try:
            cur = db.insert('tags', {'name': name})
            tagids.append(cur.lastrowid)
        except Exception, e:
            tagids.append(getTagIdByName(name))
    return tagids

def getTagIdByName(name):
    db =Sqlite3Obj("sae_mytips.db")
    tag = db.getOne('tags', where=['name=?', [name]])
    return tag.id

def getTags(tids):
    db =Sqlite3Obj("sae_mytips.db")
    if len(tids) == 0:
        return {}

    res = db.getAll('tags', where=["id in (%s)" % ','.join(['?' for i in range(0, len(tids))]), tids])
    tags = {}
    for row in res:
        tags[row.id] = row.name
    return tags

def insertPostsTags(posts_tags, uid):
    db =Sqlite3Obj("sae_mytips.db")
    for pid in posts_tags:
        for tid in posts_tags[pid]:
            db.insert('posts_tags', {'pid': pid, 'tid': tid, 'uid': uid})

def deletePostTags(postid):
    db =Sqlite3Obj("sae_mytips.db")
    db.delete('posts_tags', where=['pid=?', [postid]])

def getPostsTags(pids):
    db =Sqlite3Obj("sae_mytips.db")
    if len(pids) == 0:
        return {}, {}

    res = db.getAll('posts_tags', where=["pid in (%s)" % ','.join(['?' for i in range(0, len(pids))]), pids])
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
    db =Sqlite3Obj("sae_mytips.db")
    return db.insert('posts', post).lastrowid

def deletePost(postid):
    db =Sqlite3Obj("sae_mytips.db")
    db.delete('posts', where=['id=?', [postid]])

def getPosts(uid, startpos=0, num=25):
    db =Sqlite3Obj("sae_mytips.db")
    return db.getAll('posts', where=['uid=?', [uid]], order=['id', 'DESC'], limit=[startpos, num])

def getPostsCount(uid):
    db =Sqlite3Obj("sae_mytips.db")
    res = db.getOne('posts', fields=['count(*) as cnt'], where=['uid=?', [uid]])
    return res.cnt

def getPostsByIds(ids):
    db =Sqlite3Obj("sae_mytips.db")
    if len(ids) == 0:
        return []

    return db.getAll('posts', where=["id in (%s)" % ','.join(['?' for i in range(0, len(ids))]), ids])

def getPostsByTag(tid, uid, startpos=0, num=25):
    db =Sqlite3Obj("sae_mytips.db")
    posts_tags = db.getAll('posts_tags', where=['tid=? and uid=?', [tid, uid]], order=['pid', 'DESC'], limit=[startpos, num])
    return getPostsByIds([post_tag.pid for post_tag in posts_tags])

def getPostsCountByTag(tid, uid):
    db =Sqlite3Obj("sae_mytips.db")
    res = db.getOne('posts_tags', fields=['count(*) as cnt'], where=['tid=? and uid=?', [tid, uid]])
    return res.cnt

def getAllTagsCounts(uid):
    db =Sqlite3Obj("sae_mytips.db")
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
