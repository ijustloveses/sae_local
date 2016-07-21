# encoding=utf-8

from bottle import Bottle, route, run, template, static_file, install, mako_view, request, get, post, response, default_app, view, debug, redirect
from weibo import APIClient
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


@app.route('/getauthinfo')
@view('hello.html')
def hello():
    u = _check_cookie()
    if not u:
        redirect('/signin')

    return {'page_title': u'Auth Information', 'token': u.auth_token, 'expired': u.expired_time}


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
    client = _create_client()
    redirect(client.get_authorize_url())


@app.route('/callback')
def callback():
    code = request.params['code'] # request.query.code is for ver 1.3
    client = _create_client()
    r = client.request_access_token(code)

    access_token, expires_in, uid = r.access_token, r.expires_in, r.uid
    client.set_access_token(access_token, expires_in)

    u = client.users.show.get(uid=uid)
    user = {'id': uid,'name': u.screen_name, 'auth_token': access_token, 'expired_time':expires_in}

    dbutils.insertOrUpdateUser(user, ['id'])

    _make_cookie(uid, access_token, expires_in)
    redirect('/getlist')


def _create_client():
    return APIClient(_APP_ID, _APP_SECRET, 'http://marked.sinaapp.com/callback')


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
