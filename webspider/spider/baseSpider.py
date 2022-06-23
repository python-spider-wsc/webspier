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
from webspider.config import settings
from webspider.db.mysqlDB import BaseModel
from webspider.utils import tools
import uuid

def parse_cmdline_args():
    """解析命令行参数"""
    import argparse
    argparser = argparse.ArgumentParser(description="spider record manager")
    argparser.add_argument("--id", type=int, help="spider id")
    argparser.add_argument("--save", type=int, nargs='?', const=True, help="save response into mongodb")
    args = argparser.parse_args()
    return args.id, args.save

class BaseSpider():
    """爬虫的接口类"""
    def __init__(self, distribute_tasks="start_requests", thread_nums=1, **kwargs):
        self.thread_nums = thread_nums
        self.start_request_func = getattr(self, distribute_tasks)
        self.request_mysql = None
        self.task_mysql = None
        self.spider_id, self.save_response = parse_cmdline_args()
        self.task_id = str(uuid.uuid1())

    def call_end(self):
        """抓取结束后的回调函数"""
        pass

    def call_start(self):
        """抓取开始前的回调函数"""
        pass

    def start_requests(self):
        pass

    def before_request(self, request):
        """请求之前的hook函数"""
        pass

    def after_request(self, request, response):
        """请求之前的hook函数"""
        pass

    def before_save(self, data):
        """保存前的回调函数"""
        pass

    def after_save(self, data):
        """保存之后的回调函数"""
        pass

    def parse(self,request, response):
        """
        解析请求结果，并将得到的字段准备入库
        """
        pass

    def check_reponse(self, response):
        return True

    def run_task(self):
        for request in self.start_request_func(): # 初始请求
            self.response_queue.add(request)
        threads = []
        database_thread = DatabaseParser(self.database_queue, self)
        database_thread.start()
        for _ in range(self.thread_nums):
            download_thread = DownloadParser(self.response_queue, self.database_queue, self)
            download_thread.start()
            threads.append(download_thread)

        # 当两个队列全部为空时，认为线程结束了
        while not self.all_thread_is_done():
            time.sleep(3)
        
        for thread in threads:
            thread.stop()
            thread.join()
        database_thread.stop()
        database_thread.join()

    def run(self):
        self.record_before()
        with tools.SpiderContextManager(self.task_mysql, self.task_id):
            self.call_start()
            self.run_task()
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
        log.info("spider < %s > start running", self.name)
        self.start_time = datetime.datetime.now()
        if not self.spider_id:
            return
        if self.task_mysql is None:
            self.task_mysql = BaseModel(settings.TASK_TABLE, unique_key=["task_code"])
        self.task_mysql.save(task_code=self.task_id, spider_id = self.spider_id, service = tools.get_service_ip(), process_id = tools.get_process_id(), logfile = log.filename or "")

    def send_msg(self, cost_time):
        key = self.__dict__.get("wechat_key") or settings.WORKWECHATKEY
        if key:
            text = "爬虫{}运行完成, 共耗时{}".format(self.name, cost_time)
            tools.work_wechat_send_msg(text, key)

    def record_after(self):
        """任务保存到mysql"""
        spent_time = tools.formatSecond((datetime.datetime.now()-self.start_time).seconds)
        log.info("spider < %s > spent time: %s ", self.name, spent_time)
        self.send_msg(spent_time)
        if not self.spider_id:
            return
        self.task_mysql.save(task_code=self.task_id, request_nums=self.response_queue.nums, success_nums=self.response_queue.success_nums, 
                             save_nums = self.database_queue.success_nums, save_error_nums = self.database_queue.error_nums)
        log.info("spider < %s > finish", self.name)

    @property
    def name(self):
        return self.__class__.name
