# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/11 11:00:53
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''
from webspider.db.mysqlDB import BaseModel

class Items():

    def __init__(self, table="", unique_key=[]):
        self.__model = BaseModel(table, unique_key)

    def save(self):
        if self.__model.TABLENAME:
            self.__model.save(**self.to_dict())
        else:
            print(self.__dict__)

    def to_dict(self):
        result = {}
        for key in self.__model.FIELD:
            if key in self.__dict__:
                result[key] = self.__dict__[key]
        return result

    def get_mysql(self):
        return self.__model

    def __str__(self):
        return str(self.to_dict())
