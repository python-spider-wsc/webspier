# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/22 14:50:01
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''
from webspider.utils.log import log
import time
import sys, os
import argparse
import traceback

class TimerContextManager():
    """
    用上下文管理器计时，可对代码片段计时
    """
    def __init__(self,  flag=None):
        self.flag = flag

    def __enter__(self):
        self.time_start = time.time()
        self._line = sys._getframe().f_back.f_lineno  # 调用此方法的代码的函数
        self._file_name = sys._getframe(1).f_code.co_filename  # 哪个文件调了用此方法
        _, self._file_name = os.path.split(self._file_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.info("[file: %s] [line: %s] spent time : %s", self._file_name, self._line, time.time() - self.time_start)
        if exc_type:
            log.error(exc_val)
            log.exception(exc_tb)


class SpiderRecordManager():
    """
    开启爬虫记录的管理器
    """
    def __init__(self, name=""):
        self.name = name

    def __enter__(self):
        argparser = argparse.ArgumentParser(description="spider record manager")
        argparser.add_argument("--id", type=int, help="spider id")
        results = argparser.parse_args()
        self.spider_id = results.id
        self.start_time = time.time()
        return self.spider_id

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.info("spider < %s > run time: %s s", self.name, time.time()-self.start_time)
        if exc_type:
            exc_str = str(exc_type) + '  :  ' + str(exc_val)
            error = ''.join(traceback.format_tb(exc_tb))+ exc_str
            log.error(error)