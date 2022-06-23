# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/11 11:00:53
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''

from webspider.db.mysqlDB import BaseModel

class ItemsInterface():

    def __init__(self, save_callback="save"):
        self.callback = getattr(self, save_callback) # 指定保存的回调函数

    def to_dict(self):
        """抓取到的数据对象变为字典"""
        pass

    def save(self):
        """保存数据"""
        pass

    def __str__(self):
        return str(self.to_dict())

    def update(self, **kwargs):
        self.__dict__.update(kwargs)


class Items(ItemsInterface):

    _model = None

    @classmethod
    def model(cls):
        if cls._model is None:
            cls._model = BaseModel(cls._table_name, unique_key=getattr(cls, "_unique_key", None))
        return cls._model

    def save(self):
        if self.__class__.model():
            self.__class__.model().save(**self.to_dict())
        else:
            print(self)

    def to_dict(self):
        result = {}
        for key in self.__class__.model().FIELD:
            if key in self.__dict__:
                result[key] = self.__dict__[key]
        return result

    @property
    def mysql(self):
        return self.__class__.model()

