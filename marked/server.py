# encoding=utf-8

from bottle import Bottle, route, run, template, static_file, install, mako_view, request, get, post, response, default_app, view, debug, redirect
import time, base64, hashlib
import dbutils

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
