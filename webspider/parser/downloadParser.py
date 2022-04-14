# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/08 11:30:31
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
@Desc    :   url解析器
'''

import time
from webspider.db.mongoDB import ResponseRecordMongo
import webspider.config.settings as setting
import traceback
from webspider.db.items import Items
from webspider.parser import baseParser
import traceback
from webspider.core.request import Request

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
        
    def run(self):
        while self.run_flag:
            if not self.queue.empty():
                request = self.queue.get()
                if request:
                    self.deal_request(request)
            else:
                time.sleep(0.5) # 队列为空，暂时休眠0.5s
    
    def deal_request(self, request):
        try:
            self.before_request(request)
            response = request.get_response()
        except:
            trace = traceback.format_exc()
            self.retry_request(request, None, trace)
            return
        if not self.verify_reponse(request, response): # 验证结果失败
            self.retry_request(request, response)
            return
        self.queue.success_nums += 1
        if request.save_response:
            self.save_response_into_mongo(request, response)
        # 直接使用回调函数处理
        # 若是没有指定函数，直接使用spider.parse解析
        try:
            callback = request.callback if getattr(request, "callback", None) else "parse"
            callback = getattr(self.spider, callback)
            result = callback(request, response)
            for item in (result or []):
                if isinstance(item, Request):
                    self.queue.add(item)
                elif isinstance(item, Items):
                    self.item_queue.add(item)
        except:
            print(traceback.format_exc())

    def save_response_into_mongo(self, request, response, col="spider", trace=""):
        """保存请求结果到mongo"""
        if self.response_mongo is None:
            self.response_mongo = ResponseRecordMongo(col=col)
        self.response_mongo.save_response(response, request, trace)

    def verify_reponse(self, request, response):
        """验证请求结果是否正确"""
        if response.status_code != 200:
            return False
        if getattr(request, "check_reponse", None):
            return request.check_reponse(response)
        else: # 假如没有指定check_reponse， 直接使用spider默认的check_reponse
            return self.spider.check_reponse(response)

    def retry_request(self, request, reponse, trace=""):
        """重新请求"""
        request.retry_times += 1
        if request.retry_times<setting.RETRY_TIMES: # 小于重试次数
            self.queue.add(request)
        self.queue.error_nums += 1
        if setting.SAVE_ERROR_RESPONSE and getattr(request, "save_error", True):
            self.save_response_into_mongo(request, reponse, col="error", trace=trace) # 错误结果报错

    def before_request(self, request):
        """请求之前的hook函数"""
        before_request = request.before_request if getattr(request, "before_request", None) else self.spider.before_request
        before_request(request)
        

         


