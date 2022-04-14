# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/08 11:24:57
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
@Desc    :   使用内置的queue作为消息队列
'''

import queue

class MemoryDB:
    def __init__(self):
        self.queue = queue.Queue()
        self.nums = 0
        self.success_nums = 0
        self.error_nums = 0

    def add(self, item):
        self.nums += 1
        self.queue.put(item)

    def get(self):
        try:
            item = self.queue.get_nowait()
            return item
        except:
            return

    def empty(self):
        return self.queue.empty()
