# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/08 17:33:46
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''
from webspider.parser import baseParser
from webspider.utils.log import log
import time


class DatabaseParser(baseParser.BaseParser):
    """
    监听piplines, 存储数据
    """
    def __init__(self, queue, spider) -> None:
        super(DatabaseParser, self).__init__()
        self.queue = queue
        self.spider = spider
        

    def run(self):
        while self.run_flag:
            if not self.queue.empty():
                items = self.queue.get()
                if items:
                    self.save_data(items)
            else:
                time.sleep(0.5) # 队列为空，暂时休眠0.5s

    def save_data(self, data):
        self.record_length()
        self.queue.nums += 1
        try:
            self.spider.before_save(data)
            if hasattr(data, "callback"):
                data.callback()
            else:
                data.save()
            self.queue.success_nums += 1
            self.spider.after_save(data)
        except Exception as e:
            log.error("save item error:")
            log.exception(e)
            self.queue.error_nums += 1
