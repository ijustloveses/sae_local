# encoding=utf-8

from bottle import Bottle, route, run, template, static_file, install, mako_view, request, get, post, response, default_app, view, debug, redirect
import time, base64, hashlib
import dbutils

app = default_app()
debug(True)


@app.route('/')
@view('index.html')
def index():
    redirect('/tvlist')


#### 追剧
@app.route('/tvlist')
@view('tvlist.html')
def index():
    u = _check_cookie()
    logged_in = False
    tvshows   = None

    if u:
        logged_in = True
        tvshows = dbutils.getTvshow(u.id)

    return {'logged_in': logged_in, 'user': u, 'tvshows': tvshows}


@app.post('/addtvshow')
def addtvshow():
    u = _check_cookie()
    noname = 'FAILED_TO_FIND_NAME'
    noseason = -1
    if u:
        name = request.forms.get('name', default=noname)
        season = request.forms.get('season', default=noseason)
        episode = request.forms.get('episode', default=1)
        if name != noname and season != noseason:
            dbutils.insertTvshow(u.id, name, int(season), int(episode))

    redirect('/tvlist')


@app.route('/delete/:id')
def delete(id):
    u = _check_cookie()
    if u:
        dbutils.deleteTvshow(id)
    redirect('/tvlist')


@app.route('/done/:pstr')
def done(pstr):
    id, flag = pstr.split('_')
    u = _check_cookie()
    if u:
        dbutils.toggleDone(id, flag)
    redirect('/tvlist')


@app.route('/incr/:pstr')
def incr(pstr):
    id, episode, action = pstr.split('_')
    u = _check_cookie()
    if u:
        if action == 'incr':
            dbutils.changeEpisode(id, int(episode), 1)
        else:
            dbutils.changeEpisode(id, int(episode), -1)
    redirect('/tvlist')



#### 密码记录
@app.route('/pwlist')
@view('pwlist.html')
def pwlist():
    u = _check_cookie()
    logged_in = False
    passwds   = None

    if u:
        logged_in = True
        passwds = dbutils.getPasswd(u.id)

    return {'logged_in': logged_in, 'user': u, 'passwds': passwds}


@app.post('/pwadd')
def pwadd():
    u = _check_cookie()
    noproj = 'FAILED_TO_FIND_PROJ'
    noidno = 'FAILED_TO_FIND_IDNO'
    nopass = 'FAILED_TO_FIND_PASS'
    if u:
        project = request.forms.get('project', default=noproj)
        idno = request.forms.get('idno', default=noidno)
        passwd = request.forms.get('passwd', default=nopass)
        if project != noproj and idno != noidno and passwd != nopass:
            dbutils.insertPasswd(u.id, project, idno, passwd)

    redirect('/pwlist')


@app.route('/pwdel/:id')
def pwdel(id):
    u = _check_cookie()
    if u:
        dbutils.deletePasswd(id)
    redirect('/pwlist')


#### 登陆、账号
@app.route('/signin')
def server_static():
    redirect('/callback')


@app.route('/signout')
def server_static():
    _remove_cookie()
    redirect('/')


@app.route('/callback')
def callback():
    uid = '1653381791'
    access_token = 'access_token'
    expires_in = int(time.mktime(time.localtime())) + 3600

    user = {'id': uid, 'name': u'泡茶', 'auth_token': access_token, 'expired_time': expires_in}
    dbutils.insertOrUpdateUser(user, ['id'])

    _make_cookie(uid, access_token, expires_in)
    redirect('/')


#### 常规
@app.route('/:filename')
def server_static(filename):
    return static_file(filename, root='static')


@app.route('/css/:filename')
def server_static(filename):
    return static_file(filename, root='static/css')


@app.route('/js/:filename')
def server_static(filename):
    return static_file(filename, root='static/js')


_COOKIE = 'authuser'
_SALT = 'A random string'


def _make_cookie(uid, token, expires_in):
    expires = int(expires_in)
    s = '%s:%s:%s:%s' % (str(uid), str(token), expires, _SALT)
    md5 = hashlib.md5(s).hexdigest()
    cookie = '%s:%s:%s' % (str(uid), expires, md5)
    response.set_cookie(_COOKIE, base64.b64encode(cookie).replace('=', '_'), expires=expires_in)


def _remove_cookie():
    response.set_cookie(_COOKIE, '')


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


if __name__ == '__main__':
    run(host='0.0.0.0', port=8000, reloader=False)
