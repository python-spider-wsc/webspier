# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/11 09:27:20
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''

import time
from webspider.parser.databaseParser import DatabaseParser
from webspider.parser.downloadParser import DownloadParser
from webspider.utils.log import log
import datetime
from webspider.db.mysqlDB import BaseModel
from webspider.config import settings

class BaseSpider():

    def __init__(self, distribute_tasks, thread_nums=1, **kwargs):
        self.thread_nums = thread_nums
        self.start_request = distribute_tasks
        self.task_mysql =None

    def call_end(self):
        """
        抓取结束后的回调函数
        """
        pass

    def call_start(self):
        """
        抓取开始前的回调函数
        """
        pass

    def before_request(self, request):
        """请求之前的hook函数"""
        pass

    def after_request(self, request, response):
        """请求之前的hook函数"""
        pass

    def parse(self,request, response):
        """
        解析请求结果，并将得到的字段准备入库
        """
        pass

    def check_reponse(self, response):
        return True

    def run(self):
        self.record_before()
        for request in self.start_request(): # 初始请求
            self.response_queue.add(request)
        self.call_start()
        threads = []
        for _ in range(self.thread_nums):
            database_thread = DatabaseParser(self.database_queue)
            database_thread.start()
            download_thread = DownloadParser(self.response_queue, self.database_queue, self)
            download_thread.start()
            threads.append(database_thread)
            threads.append(download_thread)

        # 当两个队列全部为空时，认为线程结束了
        while not self.all_thread_is_done():
            time.sleep(2)
        
        for thread in threads:
            thread.stop()
            thread.join()
        self.call_end()
        self.record_after()

    def all_thread_is_done(self):
        for _ in range(3): # 多检测几次，防止误杀
            if not (self.response_queue.empty() and self.database_queue.empty()):
                return False
            # 计算失败和成功的比值，当失败率达到50%，强制停止
            if self.response_queue.error_nums>self.response_queue.success_nums and self.response_queue.nums>100:
                log.error("失败次数多于成功次数，已停止爬虫")
                return False
            time.sleep(1)
        return True

    def record_before(self):
        """任务保存到mysql之前的初始化工作"""
        if not self.spider_id:
            return
        self.start_time = datetime.datetime.now()
        if self.task_mysql is None:
            self.task_mysql = BaseModel(settings.task_TABEL, ["id"])
        self.__class__.name

    def record_after(self):
        """任务保存到mysql"""
        if not self.spider_id:
            return

