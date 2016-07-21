# encoding=utf-8

from bottle import Bottle, route, run, template, static_file, install, mako_view, request, get, post, response, default_app, view, debug, redirect
import sae
from weibo import APIError, APIClient
import time, json, base64, hashlib, time
import dbutils
import datetime

app = default_app()
debug(True)


#### 宝宝吃药
"""
# 只运行一次，初始化开始的90天，每吃20天停10天
@app.route('/initmedicine')
def initmedicine():
    u = _check_cookie()
    if u:
        dbutils.initmedicine(u.id)
    redirect('/')
"""


@app.route('/')
@view('index.html')
def index():
    u = _check_cookie()
    logged_in = False
    records   = None
    today = time.strftime("%Y-%m-%d", time.localtime())
    
    if u:
        logged_in = True
        records = dbutils.getMedicine(u.id)
    
    return {'logged_in': logged_in, 'user': u, 'records': records, 'today': today}


@app.route('/medchg/:pstr')
def medchg(pstr):
    id, medicine = pstr.split('_')
    u = _check_cookie()
    if u:
        dbutils.changeMedicine(id, medicine)
    redirect('/#' + id)        


@app.post('/medadd')
def medadd():
    u = _check_cookie()
    nodate = 'FAILED_TO_FIND_DATE'
    if u:
        dt = request.forms.get('dt', default=nodate) 
        medicine = request.forms.get('medicine', default=0) 
        if dt != nodate: 
            dbutils.insertMedicine(u.id, dt, True, medicine)
    
    redirect('/')
    

    
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

    

#### Timeline
@app.route('/timeline')
def timeline():
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    redirect('/timeline/%s' % now)
    

@app.post('/actdate')    
def actdate():
    statdate = request.forms.get('statdate') 
    redirect('/timeline/%s' % statdate)


@app.route('/timeline/:statdate')
@view('timeline.html')
def timeline(statdate):
    u = _check_cookie()
    logged_in = False
    actions   = None
    
    if u:
        logged_in = True
        actions = dbutils.getAction(u.id, statdate)
    
    return {'logged_in': logged_in, 'user': u, 'actions': actions, 'statdate': statdate, 'action_str': {1:u'睡', 2:u'睡醒', 3:u'吃', 4:u'吃完', 5:u'玩', 6:u'大便'}}
    

@app.route('/timeadd/:pstr') 
def timeadd(pstr):
    u = _check_cookie()
    statdate, action = pstr.split('_')
    stattime = datetime.datetime.now().strftime("%H:%M:%S")
    if u:
        dbutils.insertAction(u.id, statdate, stattime, int(action))
            
    redirect('/timeline/%s' % statdate)
    

# Ajax
@app.post('/timeedit')    
def timeedit():
    id = request.POST.get('pk', -1)
    stattime = request.POST.get('value', '00:00:00')
    if len(stattime) == 5:
        stattime = stattime[:2] + ':' + stattime[3:5] + ':00'
    elif len(stattime) == 4 and stattime[1].isdigit():
        stattime = stattime[:2] + ':' + stattime[2:] + ':00'
    elif len(stattime) == 4 and (not stattime[1].isdigit()):
        stattime = '0' + stattime[0] + ':' + stattime[2:] + ':00'
    elif len(stattime) == 3:
        stattime = '0' + stattime[0] + ':' + stattime[1:] + ':00'
        
    dbutils.changeAction(id, stattime)
    
    
@app.route('/timedel/:pstr')
def timedel(pstr):
    u = _check_cookie()
    statdate, id = pstr.split('_')
    if u:
        dbutils.deleteAction(id)
        
    redirect('/timeline/%s' % statdate)


    
#### sleep
@app.route('/sleep')
def sleep():
    now = datetime.datetime.now()
    enddate   = (now - datetime.timedelta(1)).strftime("%Y-%m-%d")
    startdate = (now - datetime.timedelta(7)).strftime("%Y-%m-%d")
    
    redirect('/sleep/%s/%s' % (startdate, enddate))

    
@app.route('/sleep/:startdate/:enddate')
@view('sleep.html')
def sleep(startdate, enddate):
    u = _check_cookie()
    logged_in = False
    sleeps = None

    if u:
        logged_in = True
        for date in gendate(startdate, enddate):
            calsleep(u, date)
            
        sleeps = dbutils.getSleep(u.id, startdate, enddate)
    
    return {'logged_in': logged_in, 'user': u, 'sleeps': [] if sleeps == None else sleeps, 'startdate': startdate, 'enddate': enddate}

    
@app.post('/querysleep')
def sleep():
    startdate = request.forms.get('startdate') 
    enddate   = request.forms.get('enddate') 
    
    redirect('/sleep/%s/%s' % (startdate, enddate))    


def gendate(startdate, enddate):
    sdt = datetime.datetime.strptime(startdate, "%Y-%m-%d")
    edt = datetime.datetime.strptime(enddate, "%Y-%m-%d")
    if sdt > edt:
        tmp = sdt
        sdt = edt
        edt = tmp

    while sdt <= edt:
        yield sdt.strftime("%Y-%m-%d")
        sdt += datetime.timedelta(1)


def calsleep(u, date):
    sleep = dbutils.getSleep(u.id, date, date)
    if sleep == None:
        # 1 sleep / 2 wakeup / 3 eat / 4 finish eating / 5 play / 6 pupu
        actions = dbutils.getAction(u.id, date)
        # only handle normal days which have enough actions recorded
        if actions and len(actions) > 6:
            longmins = 0
            shortmins = 0
            # check the 1st action
            if actions[0].action == 2 or actions[0].action == 3 or actions[0].action == 5:
                mins = calcmins('00:00:00', str(actions[0].stattime))
                longmins += mins
                shortmins += mins
            
            begin_sleep = False
            bs_time = '00:00:00'
            for act in actions:
                if act.action == 1:
                    begin_sleep = True
                    bs_time = act.stattime
                elif begin_sleep and act.action == 2:
                    shortmins += calcmins(str(bs_time), str(act.stattime))
                    begin_sleep = False
            
            if begin_sleep:
                shortmins += calcmins(str(bs_time), '23:59:59')
            
            begin_sleep = False
            bs_time = '00:00:00'
            for act in actions:
                if act.action == 1 or act.action == 4:
                    begin_sleep = True
                    bs_time = act.stattime
                elif begin_sleep and (act.action == 2 or act.action == 3):
                    longmins += calcmins(str(bs_time), str(act.stattime))
                    begin_sleep = False
            
            if begin_sleep:
                longmins += calcmins(str(bs_time), '23:59:59')
    
            dbutils.insertSleep(u.id, date, longmins, shortmins)

            
def calcmins(time1, time2):
    # "7:53:8" ==> "07:53:08"
    time1 = ':'.join(["%02d" % int(i) for i in time1.split(':')])
    time2 = ':'.join(["%02d" % int(i) for i in time2.split(':')])
    tm1 = datetime.datetime.strptime("2015-01-01 %s:00" % time1[0:5], "%Y-%m-%d %H:%M:%S")
    tm2 = datetime.datetime.strptime("2015-01-01 %s:00" % time2[0:5], "%Y-%m-%d %H:%M:%S")
    secs = (tm2 - tm1).seconds if tm2 >= tm1 else (tm1 - tm2).seconds
    return secs / 60
    
    
        
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
    uid = '1'
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
    run(host='0.0.0.0', port=80, reloader=False)