# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/08 11:24:57
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
@Desc    :   消息队列接口类
'''
import time

class BaseMQ():
    """消息队列接口类：主要记录队列的数量"""
    def __init__(self) -> None:
        self.nums = 0
        self.success_nums = 0
        self.error_nums = 0
        self.click_time()

    def click_time(self):
        self.add_time = time.time()

    @property
    def check_time(self):
        return time.time() - self.add_time

    def add(self):
        self.click_time()

    def get(self, **kwargs):
        pass
