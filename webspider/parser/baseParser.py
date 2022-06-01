# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/08 11:31:56
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''
from threading import Thread
import datetime
from webspider.utils.log import log

class BaseParser(Thread):
    """
    线程解析器的接口类
    """
    def __init__(self) -> None:
        super(BaseParser, self).__init__()
        self.run_flag = True
        self.log_time = None

    def run(self):
        pass

    def stop(self):
        """结束线程"""
        self.run_flag = False
    
    def record_length(self, s="结果未保存"):
        next_time = (datetime.datetime.now() -self.spider.start_time).seconds//60
        if self.log_time is None or next_time>self.log_time:
            self.log_time = next_time
            log.info("还有%s个%s", self.queue.length, s)