import time
import logging
import pymysql
from pymysql.err import OperationalError
from pymysql.err import ProgrammingError
# from DBUtils.PooledDB import PooledDB
from dbutils.pooled_db import PooledDB, InvalidConnection
import os
from Config import MYSQL
# from common.utils import auto_retry

logger = logging.getLogger(__name__)

class MySQLWrapper():
    def __init__(self, host=MYSQL['host'], user=MYSQL['user'], password=MYSQL['password'], database=MYSQL['database'],port=MYSQL['port']):
        self.database = database
        self.host=host
        self.user=user
        self.password=password
        self.port = port
        self.connect()

    # # 当连接断开的时候就重新连接
    # @auto_retry(3, (InvalidConnection, OperationalError, ProgrammingError))
    def connect(self):
        poolDB = PooledDB(
            creator=pymysql,
            maxcached=5, #池中空闲连接的最大数量
            maxconnections=5, #被允许的最大连接数
            blocking=True, #连接数达到最大时，新连接是否可阻塞。
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.database,
            charset='utf8mb4',
            use_unicode=True,
            autocommit=True,
            port=self.port
        )
        self.mysql = poolDB.connection()


    # 只取一条记录
    def fetchOne(self, sql, *args, as_list=False):
        cursor=None if as_list else pymysql.cursors.DictCursor
        with self.mysql.cursor(cursor) as cursor:
            try:
                cursor.execute(sql, args)
                result = cursor.fetchone()
                return result
            except (OperationalError, ProgrammingError, InvalidConnection):
                logger.error("Lost connection from mysql, reconnect")
                self.connect()
                return self.fetchOne(sql, args, as_list=as_list)

    # 取所有的记录，返回结果的 list
    def fetchAll(self, sql, *args, as_list=False):
        cursor=None if as_list else pymysql.cursors.DictCursor
        # try:
        with self.mysql.cursor(cursor) as cursor:
            cursor.execute(sql, args)
            results = cursor.fetchall()
            return results
        # except (OperationalError, ProgrammingError, InvalidConnection):
        #     logger.error("Lost connection from mysql, reconnect")
        #     self.connect()
        #     return self.fetchAll(sql, *args, as_list=as_list)

    # 执行 insert 或者 update 语句, 没有返回值
    def execute(self, sql, *args, category=None):
        with self.mysql.cursor() as cursor:
            try:
                if category == "list":
                    nums = cursor.execute(sql, args[0])
                elif category == "many":
                    nums = cursor.executemany(sql, args[0])
                else:
                    nums = cursor.execute(sql, args)
                return (nums, cursor.lastrowid)
            except OperationalError:
                logger.error("Lost connection from mysql, reconnect")
                self.connect()
                return self.execute(sql, *args, category=category)

    def close(self):
        self.mysql.close()

if __name__ == '__main__':
    mysql = MySQLWrapper()