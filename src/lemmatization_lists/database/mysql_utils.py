# coding=utf-8
import MySQLdb
import time

class DBConnectionManager(object):

    def __init__(self, db_host, db_port, db_user, db_password, db_name):
        """
        Args:
            - db_host:
            - db_user:
            - db_password:
            - db_name:
        """
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.db_connection = None

    def get_connection(self):
        if self.db_connection == None or self.db_connection.open == 0:
            self.db_connection = MySQLdb.connect(host=self.db_host,
                                                 port=self.db_port,
                                                 user=self.db_user,
                                                 password=self.db_password,
                                                 db=self.db_name,
                                                 charset="utf8")
        elif not self._check_connection(self.db_connection):
            self.db_connection = MySQLdb.connect(host=self.db_host,
                                                 port=self.db_port,
                                                 user=self.db_user,
                                                 password=self.db_password,
                                                 db=self.db_name,
                                                 charset="utf8")
        return self.db_connection


    def _check_connection(self, db_connection):
        try:
            db_connection.cursor().execute("SELECT * FROM TypesOfProduct")
            return True
        except:
            return False

class DBConnectionManagerInitializer(DBConnectionManager):

    def __init__(self, config_parser):

        db_host = config_parser.get("DATABASE", "host")
        db_port = config_parser.getint("DATABASE", "port")
        db_user = config_parser.get("DATABASE", "user")
        db_password = config_parser.get("DATABASE", "password")
        db_name = config_parser.get("DATABASE", "name")

        super(DBConnectionManagerInitializer, self).__init__(db_host, db_port, db_user, db_password, db_name)

def get_sql_timestamp_format():
    return '%Y-%m-%d %H:%M:%S'

def give_sql_timestamp_now():
    return time.strftime(get_sql_timestamp_format(), time.localtime())

