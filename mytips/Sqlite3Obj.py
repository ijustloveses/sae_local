#!/usr/bin/env python
# view.encoding()=utf-8 with BOM

"""
    Mysql Wrapper Object for MySQLdb

    Methods:
        getOne() - get a single row
        getAll() - get all rows
        insert() - insert a row
        insertOrUpdate() - insert a row or udate it if exists
        update() - udpate rows
        delete() - delete rows
        query() - exec a query
"""

import sqlite3
from collections import namedtuple


class Sqlite3Obj:
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.dbfile)
            self.cur = self.conn.cursor()
        except:
            print("Sqlite3 connection failed")
            raise

    # sql could inlude %s and the other formats
    # return cur
    def query(self, sql, params=None):
        try:
            if params is None:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, params)
        except:
            print("Query Failed: {}".format(sql))
            raise

        return self.cur

    # return cur
    def _select(self, table=None, fields=(), where=None, order=None, limit=None):
        sql = "SELECT %s From `%s`" % (",".join(fields), table)

        if where and len(where) > 0:
            sql += " WHERE %s" % where[0]  # where[0] like "id=%s and name=%s"

        if order:
            sql += " ORDER BY %s" % order[0]  # order[0] like "ctime"

            if len(order) > 1:
                sql += " %s" % order[1]  # order[1] like ASC|DESC

        if limit:
            sql += " LIMIT %s" % limit[0]  # limit[0] is start postion

            if len(limit) > 1:
                sql += ", %s" % limit[1]  # limit[1] is number to fetch

        return self.query(sql, where[1] if where and len(where) > 1 else None)

    # return a named tuple keyed by field names
    def getOne(self, table=None, fields="*", where=None, order=None, limit=(0, 1)):
        """
            fields like: [f1, f2, ...]
            where  like: ("id=%s and name=%s", [myid, "myname"])
            order  like: [field, ASC|DESC]
            limit  like: [start, num]
        """

        cur = self._select(table, fields, where, order, limit)
        result = cur.fetchone()

        row = None
        if result:
            Row = namedtuple("Row", [f[0] for f in cur.description])
            row = Row(*result)

        return row

    def getAll(self, table=None, fields="*", where=None, order=None, limit=None):
        cur = self._select(table, fields, where, order, limit)
        result = cur.fetchall()

        rows = None
        if result:
            Row = namedtuple("Row", [f[0] for f in cur.description])
            rows = [Row(*r) for r in result]

        return rows

    # data is a dict
    def _insert_format(self, data):
        """
            data = {"k1":"v1", "k2":"v2"}
            return ['k2,k1', '?,?']
        """
        keys = ",".join(data.keys())
        vals = ",".join(["?" for k in data])

        return [keys, vals]

    # insert a single record
    # data is a dict
    # return effected row count
    def insert(self, table, data):
        query = self._insert_format(data)

        sql = "INSERT INTO `%s` (%s) VALUES(%s)" % (table, query[0], query[1])

        res = self.query(sql, data.values())
        self.commit()
        return res

    def replace(self, table, data):
        query = self._insert_format(data)

        sql = "REPLACE INTO `%s` (%s) VALUES(%s)" % (table, query[0], query[1])

        res = self.query(sql, data.values())
        self.commit()
        return res

    def _update_format(self, data):
        """
            data = {"k1":"v1", "k2":"v2"}
            return 'k2=?,k1=?'
        """
        return "=?,".join(data.keys()) + "=?"

    # where  like: ("id=? and name=?", [myid, "myname"])
    # data is a dict
    # return effected row count
    def update(self, table, data, where=None):
        query = self._update_format(data)

        sql = "UPDATE `%s` SET %s" % (table, query)

        if where and len(where) > 0:
            sql += " WHERE %s" % where[0]

        res = self.query(sql, data.values() + where[1] if where and len(where) > 1 else data.values()).rowcount
        self.commit()
        return res

    # keys are the fields to check Duplicat Keys on
    def insertOrUpdate(self, table, data, keys):
        insert_data = data.copy()
        insert = self._insert_format(insert_data)

        for k in keys:
            del data[k]

        update = self._update_format(data)
        dupkeys = ','.join(keys)

        sql = "INSERT INTO `%s` (%s) VALUES(%s) ON CONFLICT(%s) DO UPDATE SET %s" % (table, insert[0], insert[1], dupkeys, update)

        res = self.query(sql, insert_data.values() + data.values()).rowcount
        self.commit()
        return res

    def delete(self, table, where=None):
        sql = "DELETE from `%s`" % table

        if where and len(where) > 0:
            sql += " WHERE %s" % where[0]

        res = self.query(sql, where[1] if where and len(where) > 1 else None).rowcount
        self.commit()
        return res

    # commit must be called for inno-db table
    # or nothing will be actually done for that table
    def commit(self):
        return self.conn.commit()

    def end(self):
        self.cur.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.end()
