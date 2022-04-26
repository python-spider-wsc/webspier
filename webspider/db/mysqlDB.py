import pymysql
from pymysql.err import OperationalError
from pymysql.err import ProgrammingError
from dbutils.pooled_db import PooledDB, InvalidConnection
from webspider.config import settings
from webspider.utils.log import log


class MySQLWrapper():
    def __init__(self, host=None, user="root", password=None, database=None, port=3306, **kw):
        self.__database = database
        self.__host=host
        self.__user=user
        self.__password=password
        self.__port = port
        self.connect()

    # # 当连接断开的时候就重新连接
    def connect(self):
        poolDB = PooledDB(
            creator=pymysql,
            maxcached=5, #池中空闲连接的最大数量
            maxconnections=5, #被允许的最大连接数
            blocking=True, #连接数达到最大时，新连接是否可阻塞。
            host=self.__host,
            user=self.__user,
            password=self.__password,
            db=self.__database,
            charset='utf8mb4',
            use_unicode=True,
            autocommit=True,
            port=self.__port
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
                log.error("Lost connection from mysql, reconnect")
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
                log.error("Lost connection from mysql, reconnect")
                self.connect()
                return self.execute(sql, *args, category=category)

    def close(self):
        self.mysql.close()

class BaseModel(MySQLWrapper):
    """简单的ORM框架类"""

    def __init__(self, table, unique_key=None, database="default"):
        super(BaseModel, self).__init__(**settings.DATABASES[database])
        self.TABLENAME = table
        self.UNIQUE_KEY = unique_key or []
        self.init_model()
        for key in self.UNIQUE_KEY:
            if key not in self.FIELD:
                raise Exception("唯一索引不在表空间中")
        
    def find(self, data, columns=["id"]):
        sql = "SELECT {columns} FROM `{table}` WHERE {where}".format(columns=','.join(["`"+key+"`"for key in columns]),table=self.TABLENAME, where=' AND '.join(["`"+key+"`=%s"for key in self.UNIQUE_KEY]))
        return self.fetchOne(sql, *[data[key] for key in self.UNIQUE_KEY])

    def save(self, **kwargs):
        """根据指定的唯一ID, 存在就更新, 否则就插入"""
        if self.UNIQUE_KEY: # 唯一ID未指定，直接插入
            result = self.find(kwargs)
            if result: #有更新
                self.update(result["id"], kwargs)
                return result["id"]
        return self.insert(kwargs)

    def insert(self, data):
        keys = []
        value = []
        for key in data:
            if key in self.FIELD:
                keys.append("`"+key+"`")
                value.append(data[key])
        sql = "INSERT INTO `{table}`({field})VALUES({values})".format(table=self.TABLENAME, field=','.join(keys), values=','.join(['%s']*len(data)))
        _, idx = self.execute(sql, value, category="list")
        return idx

    def update(self, uid, data):
        keys = []
        value = []
        for key in data:
            if key in self.FIELD:
                keys.append("`"+key+"`=%s")
                value.append(data[key])
        value.append(uid)
        sql = "UPDATE `{table}` SET {field} WHERE `id`=%s".format(table=self.TABLENAME, field=','.join(keys))
        return self.execute(sql, value, category="list")

    def init_model(self):
        select_sql = "show columns from {}".format(self.TABLENAME)
        result = self.fetchAll(select_sql)
        self.FIELD = tuple((item["Field"] for item in result))
        self.DEFAULT = tuple((item["Default"] for item in result))
