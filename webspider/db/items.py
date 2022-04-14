# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/11 11:00:53
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''

from webspider.db.tableModel import BaseModel

class Items(BaseModel):

    def __init__(self, table="", unique_key=[]):
        self.__table = table
        self.__unique_key = unique_key

    def save(self):
        if self.__table:
            super(Items, self).save()
        else:
            print(self.__dict__)