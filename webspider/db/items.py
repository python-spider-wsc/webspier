# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/11 11:00:53
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''

class Items():

    def save(self):
        if self.__class__.model.TABLENAME:
            self.__class__.model.save(**self.to_dict())
        else:
            print(self.__dict__)

    def to_dict(self):
        result = {}
        for key in self.__class__.model.FIELD:
            if key in self.__dict__:
                result[key] = self.__dict__[key]
        return result

    @property
    def mysql(self):
        return self.__class__.model

    def __str__(self):
        return str(self.to_dict())
