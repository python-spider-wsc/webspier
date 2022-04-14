# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/08 11:31:56
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''
from threading import Thread

class BaseParser(Thread):
    """
    线程解析器的接口类
    """
    def __init__(self) -> None:
        super(BaseParser, self).__init__()
        self.run_flag = True

    def run(self):
        pass

    def stop(self):
        """结束线程"""
        self.run_flag = False