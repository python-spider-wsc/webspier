import pymysql
from pymysql.err import OperationalError
from pymysql.err import ProgrammingError
from dbutils.pooled_db import PooledDB, InvalidConnection
from webspider.db.baseMysql import MySQLWrapper
from webspider.config import settings
from webspider.utils.log import log


class MySQLWrapper():
    def __init__(self, host=None, user="root", password=None, database=None, port=3306):
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
    """docstring for baseModel"""

    def __init__(self, table, unique_key, database="default"):
        super(BaseModel, self).__init__(**settings.DATABASES[database])
        self.TABLENAME = table
        self.FIELD, self.DEFAULT = self.init_model(table)
        self.UNIQUE_KEY = unique_key
        for key in self.UNIQUE_KEY:
            if key not in self.FIELD:
                raise Exception("唯一索引不在表空间中")

    def insert(self, columns=None):
        result = self.get_field(columns)
        sql = self.make_insert_sql(result)
        self.execute(sql, self.get_value(result), category="list")

    def find(self, where=None, columns=["id"]):
        if where is None:
            where = self.UNIQUE_KEY
        sql = self.make_select_sql(where, columns)
        return self.fetchOne(sql, *self.get_value(where))

    def find_many(self, sql, *args):
        return self.fetchAll(sql, *args)

    def update(self, where, columns=None):
        result = self.get_field(columns)
        sql = self.make_update_sql(result, where)
        return self.execute(sql, self.get_value(result), category="list")

    def save(self):
        result = self.find(where=self.UNIQUE_KEY, columns=["id"])
        if result: #有更新
            self.update(where="`id`={}".format(result["id"]))
        else: #无插入
            self.insert()
        
    def get_field(self, columns):
        res = columns if columns else self.__dict__
        result = [column for column in res if column in self.FIELD]
        return result

    def get_value(self, data):
        if not data:
            return []
        result = [self.__dict__.get(column, self.DEFAULT[self.FIELD.index(column)])for column in data]
        return result

    def make_insert_sql(self, data):
        key = ','.join(["`"+item+"`" for item in data])
        sql = "INSERT INTO `{table}`({field})VALUES({values})".format(table=self.TABLENAME,field=key, values=','.join(['%s']*len(data)))
        return sql

    def make_select_sql(self, where, columns):
        if columns:
            data = self.get_field(columns)
            field = ','.join(["`"+item+"`" for item in data])
        else:
            field = '*'
        if where:
            sql = "SELECT {field} FROM `{table}` WHERE {where}".format(table=self.TABLENAME,field=field, where=' AND '.join(["`"+key+"`=%s"for key in where]))
        else:
            sql = "SELECT {field} FROM `{table}`".format(table=self.TABLENAME,field=field)
        return sql

    def make_update_sql(self, data, where):
        field = ','.join(["`"+item+"`=%s" for item in data])
        sql = "UPDATE `{table}` SET {field} WHERE {where}".format(table=self.TABLENAME,field=field, where=where)
        return sql

    def init_model(self, table):
        select_sql = "show columns from {}".format(table)
        result = self.mysql.fetchAll(select_sql)
        field = tuple((item["Field"] for item in result))
        default = tuple((item["Default"] for item in result))
        return field, default

    def clear(self):
        tmp = [key for key in self.__dict__ if key not in ("TABLENAME", "FIELD", "DEFAULT", "UNIQUE_KEY", "mysql")]
        for key in tmp:
            del self.__dict__[key]

    def __str__(self):
        return str({key:self.__dict__[key] for key in self.__dict__ if key not in ("TABLENAME", "FIELD", "DEFAULT", "UNIQUE_KEY", "mysql")})

