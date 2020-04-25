fdb = MySQLdb.connect(db="", host="", user="", passwd="", charset="utf8", port=3306)
fcur = fdb.cursor()
tdb = sqlite3.connect("")
tcur = tdb.cursor()
def p(tbl):
    sql = "select * from {}".format(tbl)
    fcur.execute(sql)
    while True:
            d = fcur.fetchone()
            if d is None:
                    break
            isql = "insert into {} values ({})".format(tbl, ",".join(["?"]*len(d)))
            tcur.execute(isql, transform_data(d))
    tdb.commit()

def clear():
    fcur.execute("show tables")
    tbls = fcur.fetchall()
    for tbl in tbls:
            tcur.execute("delete from {}".format(tbl[0]))
    tdb.commit()

def bp():
    fcur.execute("show tables")
    tbls = fcur.fetchall()
    for tbl in tbls:
            print(tbl[0])
            p(tbl[0])

def transform(item):
    if isinstance(item, datetime.date):
            return str(item)
    if isinstance(item, datetime.timedelta):
            return str(item)
    return item

def transform_data(data):
    return tuple(transform(item) for item in data)

