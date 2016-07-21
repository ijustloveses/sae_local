# encoding=utf-8

#######################
#
# 版本3 2015-07-19 21:27:01 分，共计 7307 条
# 其中，有效 7172 条，135 条被微博删除
# 共计 498 个 tag；9655 条 post - tag 关系；
#
# 版本2 2015-01-26 12:28:01 分，共计 6012 条
# 其中，有效 5891 条，121 条被微博删除
# 共计 444 个 tag；7709 条 post - tag 关系；
#
# 版本1 2015-01-09 12:22:23 分，共计 5841 条
# 其中，有效 5,721 条，120 条被微博删除
# 共计 439 个 tag；7413 条 post - tag 关系；
#
#######################

from bottle import Bottle, route, run, template, static_file, install, mako_view, request, get, post, response, default_app, view, debug, redirect
import time, json, base64, hashlib
import dbutils

_MIN_POST_ID = 3803238748759186  # 上次导入最大的ID，就是本次导入的最小起始ID

app = default_app()
debug(True)

@app.route('/')
@view('page.html')
def hello():
    startpos, page, last, num = pager(dbutils.getPostsCount())

    posts = dbutils.getPosts(startpos, num)
    if not posts:
        return {'posts': [], 'posts_tags': {}, 'tags': {}}

    pids = [post.id for post in posts]
    posts_tags, tags = dbutils.getPostsTags(pids)

    return {'posts': posts, 'posts_tags': posts_tags, 'tags': tags, 'page': page, 'last': last, 'num': num, 'cururl': '/'}


@app.route('/tag/:tid')
@view('page.html')
def hello(tid):
    startpos, page, last, num = pager(dbutils.getPostsCountByTag(tid))

    posts = dbutils.getPostsByTag(tid, startpos, num)
    if not posts:
        return {'posts': [], 'posts_tags': {}, 'tags': {}}

    pids = [post.id for post in posts]
    posts_tags, tags = dbutils.getPostsTags(pids)

    return {'posts': posts, 'posts_tags': posts_tags, 'tags': tags, 'page': page, 'last': last, 'num': num, 'cururl': '/tag/%s' % tid}


@app.route('/showlistresult')
@view('hello.html')
def hello():
    posts = dbutils.getRawPosts()
    if not posts:
        posts = []

    ids = {}
    mintime = 2420485364
    maxtime = 0
    for post in posts:
        fav = json.loads(post.content)

        id = fav['status']['id']
        ids[id] = 1

        favtime = time2timestamp(fav['favorited_time'])
        if favtime > maxtime:
            maxtime = favtime
        if favtime < mintime:
            mintime = favtime

    content = "post num: %d,  mintime: %s,  maxtime: %s" % (len(ids), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mintime)), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(maxtime)))

    return {'page_title': u'收藏微博展示', 'content': content}


# step 1. 获取原始内容，一个请求最多50条，故此很可能会重复；放到 raw_posts 表
@app.route('/getlist')
def hello():
    u = _check_cookie()
    if not u:
        redirect('/signin')

    client = _create_client()
    client.set_access_token(u.auth_token, u.expired_time)
    for i in range(1,40):
        favlist = client.favorites.get(count=40,page=i)
        dbutils.insertRawPosts(favlist.favorites)
        time.sleep(10)
    redirect('/showlistresult')


# step 2. 将 raw_posts 表中的数据唯一化，并放到 uniq_raw_posts 表中
@app.route('/uniq')
@view('hello.html')
def hello():
    posts = dbutils.getRawPosts()
    if not posts:
        posts = []

    ids = {}
    mintime = 2420485364
    maxtime = 0
    for post in posts:
        fav = json.loads(post.content)

        id = fav['status']['id']
        if int(id) <= _MIN_POST_ID:
            continue

        if not ids.has_key(id):
            ids[id] = post.content
        else:
            continue

        favtime = time2timestamp(fav['favorited_time'])
        if favtime > maxtime:
            maxtime = favtime
        if favtime < mintime:
            mintime = favtime

    # 入库
    dbutils.insertUniqRawPosts(ids)

    content = "post num: %d,  mintime: %s,  maxtime: %s" % (len(ids), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mintime)), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(maxtime)))

    return {'page_title': u'收藏微博展示', 'content': content}


# step 3. 从 uniq_raw_posts 表中获取数据，然后整理后放到 favorites 表中
@app.route('/extract')
def hello():
    posts = dbutils.getUniqRawPosts(['id > "%s"', _MIN_POST_ID])
    if not posts:
        posts = []

    favorites = []
    tags = {}
    posts_tags = {}
    deleted = 0
    for post in posts:
        if int(post.id) <= _MIN_POST_ID:
            continue

        fav_data = {'re_created_at':'0000-00-00 00:00:00', 're_post_text':'', 're_id':'', 're_pic_urls':'', 're_user_id':'', 're_profile_url':'', 're_profile_image_url':'', 're_screen_name':'', 're_url':''}

        fav = json.loads(post.content)
        # 处理微博被删的情况
        if fav['status'].has_key('deleted') and fav['status']['deleted'] == "1":
            deleted += 1
            continue

        fav_data['id'] = post.id
        favtime = time2timestamp(fav['favorited_time'])
        fav_data['favtime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(favtime))
        created_at = time2timestamp(fav['status']['created_at'])
        fav_data['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created_at))
        fav_data['post_text'] = fav['status']['text']
        fav_data['pic_urls'] = json.dumps(fav['status']['pic_urls']) if fav['status'].has_key('pic_urls') else json.dumps([])
        try:
            fav_data['user_id'] = fav['status']['user']['id']
        except Exception, e:
            deleted += 1
            continue
        # 个人微博主页
        fav_data['profile_url'] = "http://weibo.com/%s" % fav['status']['user']['profile_url']
        fav_data['profile_image_url'] = fav['status']['user']['profile_image_url']
        fav_data['screen_name'] = fav['status']['user']['screen_name']
        # 个人主页，即使没有也会返回 ""
        fav_data['url'] = fav['status']['user']['url'] if fav['status']['user']['url'] else fav_data['profile_url']

        if fav['status'].has_key('retweeted_status'):
            # 处理微博被删的情况
            if fav['status']['retweeted_status'].has_key('deleted') and fav['status']['retweeted_status']['deleted'] == "1":
                deleted += 1
                continue

            re_created_at = time2timestamp(fav['status']['retweeted_status']['created_at'])
            fav_data['re_created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(re_created_at))
            fav_data['re_post_text'] = fav['status']['retweeted_status']['text']
            fav_data['re_id'] = fav['status']['retweeted_status']['id']
            fav_data['re_pic_urls'] = json.dumps(fav['status']['retweeted_status']['pic_urls']) if fav['status']['retweeted_status'].has_key('pic_urls') else json.dumps([])
            fav_data['re_user_id'] = fav['status']['retweeted_status']['user']['id']
            fav_data['re_profile_url'] = "http://weibo.com/%s" % fav['status']['retweeted_status']['user']['profile_url']
            fav_data['re_profile_image_url'] = fav['status']['retweeted_status']['user']['profile_image_url']
            fav_data['re_screen_name'] = fav['status']['retweeted_status']['user']['screen_name']
            fav_data['re_url'] = fav['status']['retweeted_status']['user']['url'] if fav['status']['retweeted_status']['user']['url'] else fav_data['re_profile_image_url']

        favorites.append(fav_data)

        # like "tags": [ {'id': 23, 'tag': "good"}, ... ]
        if len(fav['tags']) > 0:
            for tag in fav['tags']:
                tags[tag['id']] = tag['tag']

                if not posts_tags.has_key(fav_data['id']):
                    posts_tags[fav_data['id']] = []
                posts_tags[fav_data['id']].append(tag['id'])

    content = json.dumps(tags)
    content += '</br></br>' + json.dumps(posts_tags)
    # 入库, posts & tags & posts_tags
    dbutils.insertPosts(favorites)
    dbutils.insertTags(tags)
    dbutils.insertPostsTags(posts_tags)

    redirect('/')


@app.route('/s/css/:filename')
def server_css(filename):
    return static_file(filename, root='assets/css')


@app.route('/s/js/:filename')
def server_js(filename):
    return static_file(filename, root='assets/js')


@app.route('/s/images/:filename')
def server_images(filename):
    return static_file(filename, root='assets/images')


@app.route('/signin')
def server_static():
    redirect('/callback')


@app.route('/callback')
def callback():
    uid = '1'
    access_token = 'access_token'
    expires_in = int(time.mktime(time.localtime())) + 3600

    user = {'id': uid, 'name': u'泡茶', 'auth_token': access_token, 'expired_time': expires_in}
    dbutils.insertOrUpdateUser(user, ['id'])

    _make_cookie(uid, access_token, expires_in)
    redirect('/getlist')


_COOKIE = 'authuser'
_SALT = 'A random string'

def _make_cookie(uid, token, expires_in):
    expires = int(expires_in)
    s = '%s:%s:%s:%s' % (str(uid), str(token), expires, _SALT)
    md5 = hashlib.md5(s).hexdigest()
    cookie = '%s:%s:%s' % (str(uid), expires, md5)
    response.set_cookie(_COOKIE, base64.b64encode(cookie).replace('=', '_'), expires=expires_in)


def _check_cookie():
    b64cookie = request.get_cookie(_COOKIE)
    if not b64cookie:
        return None
    cookie = base64.b64decode(b64cookie.replace('_', '='))
    uid, expires, md5 = cookie.split(':', 2)
    if int(expires) < time.time():
        return None
    user = dbutils.getUser(uid)
    if not user:
        return None
    s = '%s:%s:%s:%s' % (uid, user.auth_token, expires, _SALT)
    if md5 != hashlib.md5(s).hexdigest():
        return None
    return user


# intime like 'Tue Jan 06 03:16:04 +0800 2015'
def time2timestamp(intime):
    # like 'Tue Jan 06 03:16:04 2015'
    intime = intime[0:-10] + intime[-4:]
    return time.mktime(time.strptime(intime, "%a %b %d %H:%M:%S %Y"))


def pager(totalnum):
    page = int(request.params.get('page', '1'))
    if page < 1:
        page = 1
    num = int(request.params.get('num', '25'))
    if num < 10:
        num = 25

    last = (totalnum - 1) / num + 1
    if page > last:
        page = last
    startpos = (page - 1) * num

    return startpos, page, last, num


if __name__ == '__main__':
    run(host='0.0.0.0', port=80, reloader=False)
