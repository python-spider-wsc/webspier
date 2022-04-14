
from webspider.db.baseMysql import MySQLWrapper

class BaseModel():
    """docstring for baseModel"""
    mysql = MySQLWrapper()

    def __init__(self, table, unique_key):
        self.TABLENAME = table
        self.FIELD, self.DEFAULT = self.init_model(table)
        self.UNIQUE_KEY = unique_key
        for key in self.UNIQUE_KEY:
            if key not in self.FIELD:
                raise Exception("唯一索引不在表空间中")

    def insert(self, columns=None):
        result = self.get_field(columns)
        sql = self.make_insert_sql(result)
        self.__class__.mysql.execute(sql, self.get_value(result), category="list")

    def find(self, where=None, columns=None):
        sql = self.make_select_sql(where, columns)
        return self.__class__.mysql.fetchOne(sql, *self.get_value(where))

    def update(self, where, columns=None):
        result = self.get_field(columns)
        sql = self.make_update_sql(result, where)
        return self.__class__.mysql.execute(sql, self.get_value(result), category="list")

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

    @classmethod
    def init_model(cls, table):
        select_sql = "show columns from {}".format(table)
        result = cls.mysql.fetchAll(select_sql)
        field = tuple((item["Field"] for item in result))
        default = tuple((item["Default"] for item in result))
        return field, default

    def clear(self):
        tmp = [key for key in self.__dict__ if key not in ("TABLENAME", "FIELD", "DEFAULT", "UNIQUE_KEY")]
        for key in tmp:
            del self.__dict__[key]

    def __str__(self):
        return str({key:self.__dict__[key] for key in self.__dict__ if key not in ("TABLENAME", "FIELD", "DEFAULT", "UNIQUE_KEY")})


if __name__ == '__main__':
    bm = BaseModel("zkt_task")
    bm.sid=1
    bm.status = 2
    bm.insert(columns=['sid', 'service', 'pid', 'status'])
