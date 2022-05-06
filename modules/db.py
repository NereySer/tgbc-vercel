import os
import psycopg2

class Db(object):
    _db_conn = None
    _db_cur = None

    @classmethod
    def _initCursor(self):
        if self._db_conn is None:
            self._db_cur = None

            DATABASE_URL = os.getenv('DATABASE_URL')

            self._db_conn = psycopg2.connect(DATABASE_URL) #, sslmode='require')
            self._db_conn.set_session(autocommit=True)

        if self._db_cur is None:
            self._db_cur = self._db_conn.cursor()

        self.initDB()

        return self._db_cur

    @classmethod
    def initDB(self, forced = False):
        if not forced:
            self._db_cur.execute("SELECT COUNT(table_name) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'public';")
            tables_count = self._db_cur.fetchone()[0]

        if forced or tables_count == 0:
            sql = open('tools/init.sql').read()

            self._db_cur.execute(sql)

    @classmethod
    def closeDB(self):
        if self._db_cur is not None:
            self._db_cur.close()

            self._db_cur = None

        if self._db_conn is not None:
            self._db_conn.close()

            self._db_conn = None

    def __del__(self):
        type(self).closeDB()

class DbConfig(Db):
    def getConfig(self):
        cur = self._initCursor()

        cur.execute("SELECT * FROM config;")

        retval = {}

        for row in self._db_cur:
            retval[row[0]] = row[1]

        return retval

    def setConfigValue(self, key, value):
        cur = self._initCursor()

        cur.execute("UPDATE config SET value=%(value)s WHERE key=%(key)s;", {'key': key, 'value': value})
