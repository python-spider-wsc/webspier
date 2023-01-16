# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/08 11:30:31
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
@Desc    :   url解析器
'''

from webspider.db.mongoDB import ResponseRecordMongo
import webspider.config.settings as setting
from webspider.db.items import ItemsInterface
from webspider.parser import baseParser
from webspider.core.request import Request
from webspider.utils.log import log
import traceback
import time
import sys

class DownloadParser(baseParser.BaseParser):
    """
    url解析器, 获得response
    """
    def __init__(self, queue, item_queue, spider) -> None:
        super(DownloadParser, self).__init__()
        self.queue = queue
        self.item_queue = item_queue
        self.response_mongo = None
        self.spider = spider
        # self.foot = [] # 请求脚印
        self.error_collections={}
        
    def run(self):
        while self.run_flag:
            if not self.queue.empty():
                request = self.queue.get()
                if request:
                    self.deal_request(request)
            else:
                time.sleep(0.5) # 队列为空，暂时休眠0.5s

    def next_request(self, request):
        next = self.spider.next_request(request)
        if isinstance(next, Request):
            self.queue.add(next)
    
    def deal_request(self, request):
        status = 1
        try:
            res = self.before_request(request)
            if res is False:
                log.debug("跳过该请求：%s", request.url)
                self.queue.nums -= 1
                self.next_request(request)
                return
            response = request.get_response()
        except Exception as e:
            log.error("request error:")
            log.exception(e)
            self.retry_request(request, None)
            self.save_request_track(0)
            return
        verify_flag = self.verify_reponse(request, response)
        if verify_flag == "continue": # 验证失败继续下次请求
            log.error("check response failed, continue next request")
            self.next_request(request)
            return
        elif not verify_flag: # 返回结果验证失败，结束请求
            log.error("check response failed, stop request")
            self.save_request_track(0)
            return
        if self.spider.spider_id and (request.save_response or self.spider.save_response):
            self.save_response_into_mongo(request, response)
        # 直接使用回调函数处理，若是没有指定函数，直接使用spider.parse解析
        try:
            callback = request.callback if getattr(request, "callback") else "parse"
            callback = getattr(self.spider, callback)
            result = callback(request, response)
            for item in (result or []):
                if isinstance(item, Request):
                    self.queue.add(item)
                elif isinstance(item, ItemsInterface):
                    if self.spider.test_flag:
                        print(item)
                    self.item_queue.add(item)
            self.queue.success_nums += 1
        except Exception as e:
            status = 0
            self.queue.error_nums += 1 # 回调解析失败，保存结果，不再重试
            if setting.SAVE_ERROR_RESPONSE and getattr(request, "save_error", True):
                self.save_response_into_mongo(request, response, col="error")
            log.error("parse error:")
            log.exception(e)
        self.save_request_track(status)
        
    def save_request_track(self, status):
        """记录请求脚印"""
        # if self.spider.task_mysql: # 请求日志可以保存到mysql
        #     self.foot.append((self.spider.task_code, datetime.datetime.now(),status)) # 任务code, 时间， 状态
        #     if len(self.foot)>1000:
        #         sql = f"INSERT INTO {settings.REQUEST_TABLE} (task_code, date, status)VALUES(%s,%s,%s)"
        #         self.spider.request_mysql.execute(sql, self.foot, category="many")
        #         self.foot = []
        pass


    def save_response_into_mongo(self, request, response, col="task"):
        """保存请求结果到mongo"""
        try:
            if self.response_mongo is None:
                self.response_mongo = ResponseRecordMongo(col=col)
            res = self.response_mongo.save_response(response, request, self.spider, trace=traceback.format_exc(), error=repr(sys.exc_info()[1]))
            if col=="error" and res:
                log.info("response save into mongo : %s", res.inserted_id)
        except Exception as e:
            log.error(e)
            log.exception(e)

    def verify_reponse(self, request, response):
        """验证请求结果是否正确"""
        if self.spider.test_flag:
            print(response.text)
        if response.status_code != 200:
            log.error("request error: status code is %s", response.status_code)
        try:
            check_reponse = getattr(request, "check_reponse", self.spider.check_reponse)
            if check_reponse is None:
                return True
            return check_reponse(request, response)
        except Exception as e:
            log.error("check reponse error")
            log.exception(e)
            if repr(e) not in self.error_collections:
                self.error_collections[repr(e)] = {"name":"请求结果检查", "nums":0}
            self.error_collections[repr(e)]["nums"] += 1 
            self.retry_request(request, response)
        return False

    def retry_request(self, request, response):
        """重新请求"""
        request.retry_times += 1
        if request.retry_times<setting.RETRY_TIMES: # 小于重试次数
            self.queue.add(request)
        else: # 失败之后继续后续请求
            self.next_request(request)
        self.queue.error_nums += 1
        log.error("request error: retry time %s", request.retry_times)
        if setting.SAVE_ERROR_RESPONSE and getattr(request, "save_error", True):
            self.save_response_into_mongo(request, response, col="error") # 错误结果保存

    def before_request(self, request):
        """请求之前的hook函数"""
        before_request = request.before_request if getattr(request, "before_request", None) else self.spider.before_request
        self.record_length("请求未完成")
        return before_request(request)
