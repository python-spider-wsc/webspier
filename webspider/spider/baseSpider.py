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
from webspider.db.memoryDB import MemoryDB  # 使用内置的queue作为队列
from webspider.utils.log import log
import datetime
from webspider.config import settings
from webspider.db.mysqlDB import BaseModel
from webspider.utils import tools


class BaseSpider():
    """爬虫的接口类"""
    def __init__(self, distribute_tasks="start_requests", thread_nums=1, **kwargs):
        self.response_queue = MemoryDB() # 待解析队列
        self.database_queue = MemoryDB() # 待存储队列
        self.thread_nums = thread_nums
        self.start_request_func = getattr(self, distribute_tasks)
        self.request_mysql = None
        self.task_mysql = None
        self.spider_id, self.save_response = tools.parse_cmdline_args()
        self.task_id = tools.get_task_code()
        self.start_time = datetime.datetime.now()
        self.test_flag = False

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

    def next_request(self, request):
        """解析完一个请求之后的请求
        """
        pass

    def check_reponse(self, response):
        return True

    def run_task(self):
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
        result = {}
        for thread in threads:
            for key in thread.error_collections:
                error = thread.error_collections[key]
                if key not in result:
                    result[key] = error
                else:
                    result[key]["nums"] += error['nums']
            thread.stop()
            thread.join()
        database_thread.stop()
        database_thread.join()
        return result

    def run(self):
        self.record_before()
        status = 1
        errors = {}
        try:
            self.call_start()
            for request in self.start_request_func(): # 初始请求
                self.response_queue.add(request)
            errors = self.run_task()
            self.call_end()
        except Exception as e:
            log.error(e)
            log.exception(e)
            text = "爬虫{}运行出错: {}".format(self.name, e)
            tools.work_wechat_send_msg(text, settings.WORKWECHATERRORKEY, mobile_list=settings.WORKWECHATPHONES)
            status = 2
        finally:
            self.record_after(status, errors)

    def all_thread_is_done(self):
        for i in range(20): # 多检测几次，防止误杀
            if self.response_queue.check_time<3 or self.database_queue.check_time<3:
                return False
            if not (self.response_queue.empty() and self.database_queue.empty()):
                return False
            # 计算失败和成功的比值，当失败率达到50%，强制停止
            if i%5==0 and self.response_queue.error_nums>self.response_queue.success_nums and self.response_queue.nums>100:
                log.error("失败次数多于成功次数，已停止爬虫")
                return True
            time.sleep(0.2)
            log.info("第%s次队列已空", i)
        return True

    def record_before(self):
        """任务保存到mysql之前的初始化工作"""
        log.info("spider < %s > start running", self.name)
        if not self.spider_id:
            return
        if self.task_mysql is None:
            self.task_mysql = BaseModel(settings.TASK_TABLE, unique_key=["task_code"])
        self.task_mysql.save(task_code=self.task_id, spider_id = self.spider_id or 0, service = tools.get_service_ip(), process_id = tools.get_process_id(), logfile = log.filename or "")

    def send_msg(self, cost_time, status, errors):
        errors = errors or {}
        status = "成功" if status==1 else "失败"
        key = self.__dict__.get("wechat_key") or settings.WORKWECHATKEY
        if key:
            text = "爬虫{}运行{}, 共耗时{}, 请求成功{}次,失败{}次,保存{}条数据".format(self.name, status, cost_time, self.response_queue.success_nums, self.response_queue.error_nums, self.database_queue.success_nums)
            tools.work_wechat_send_msg(text, key)
        text = []
        for key in errors:
            error = errors[key]
            text.append(f"{error['name']}发生错误:{key}， 共{error['nums']}次")
        if text:
            tools.work_wechat_send_msg(f"本次{self.name}抓取错误:\n"+"\n".join(text), settings.WORKWECHATERRORKEY, settings.WORKWECHATPHONES)

    def record_after(self, status=1, errors=None):
        """任务保存到mysql"""
        spent_time = tools.formatSecond((datetime.datetime.now()-self.start_time).seconds)
        log.info("spider < %s > spent time: %s ", self.name, spent_time)
        if not self.spider_id:
            return
        self.send_msg(spent_time, status, errors=errors)
        self.task_mysql.save(task_code=self.task_id, status=status, end_time=datetime.datetime.now(),
                             request_nums=self.response_queue.nums, success_nums=self.response_queue.success_nums, 
                             save_nums = self.database_queue.success_nums, save_error_nums = self.database_queue.error_nums)
        log.info("spider < %s > finish", self.name)
    
    def test(self, *args, **kwargs):
        self.test_flag = True
        for request in self.test_requests(*args, **kwargs):
            self.response_queue.add(request)
        self.run_task()
    
    def test_requests(self, *args, **kwargs):
        for request in self.start_request_func(): # 初始请求
            yield request

    @property
    def name(self):
        return self.__class__.name
