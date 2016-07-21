Move my personal website from SinaSae Platform to local.

Please Notes:

- sql scheme: add "DEFAULT CHARSET=utf8".
- MysqlObj.py: call self.commit() at the end of insert/update/delete functions.
- dbutils.py:
    + redefine MYSQL_HOST/MYSQL_DB/etc..
    + make the 2nd parameters of where list, such as where=['id=%s', [id]].
- index.wsgi rename to server.py
    + app = Bottle()  ==>  app = default_app()
    + don't connect Sina OpenAuth anymore, use my nickname always.
    + modify /sigin, /callback functions accordingly, and remove _create_client function
    + run server by: run(host='0.0.0.0', port=80, reloader=False) 
