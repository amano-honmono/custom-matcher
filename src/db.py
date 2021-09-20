import MySQLdb
from src.config import config


class DB:
    connection = None

    def connect(self):
        self.connection = MySQLdb.connect(
                user=config['mysql']['user'],
                passwd=config['mysql']['passwd'],
                host=config['mysql']['host'],
                db=config['mysql']['db_dev'] if config['debug'] else
                config['mysql']['db']
        )

    def query(self, sql, values = ()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, values)
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(sql, values)
        return cursor
