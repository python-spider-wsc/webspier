# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/22 14:50:01
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''
from webspider.utils.log import log
from webspider.config import settings
from webspider.db.mysqlDB import BaseModel
import time
import sys, os
import traceback
import re
import requests

class TimerContextManager():
    """
    用上下文管理器计时，可对代码片段计时
    """
    def __init__(self):
        pass

    def __enter__(self):
        self.time_start = time.time()
        self._line = sys._getframe().f_back.f_lineno  # 调用此方法的代码的函数
        self._file_name = sys._getframe(1).f_code.co_filename  # 哪个文件调了用此方法
        _, self._file_name = os.path.split(self._file_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.info("[file: %s] [line: %s] spent time : %s", self._file_name, self._line, time.time() - self.time_start)
        if exc_type:
            exc_str = str(exc_type) + '  :  ' + str(exc_val)
            error = ''.join(traceback.format_tb(exc_tb))+ exc_str
            log.error(error)

def spiderDecorator(name):
    """记录爬虫任务运行时间，并记下日志"""
    def spent_time(func):
        def make_decorater(*args,**kwargs):
            log.info("spider < %s > start running", name)
            start_time = time.time()
            func(*args,**kwargs)
            log.info("spider < %s > spent time: %s s", name, time.time()-start_time)
        return make_decorater
    return spent_time

def formatSecond(second):
    """将时间间隔秒转成时分秒"""
    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    s = "{}小时".format(hour) if hour else ""
    s += "{}分钟".format(minute) if minute else ""
    if not s or second:
        s += "{}秒".format(second)
    return s

def get_service_ip():
    import socket
    ##1.获取主机名
    hostname = socket.gethostname()
    ip=socket.gethostbyname(hostname)
    res = re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", ip)
    return res[0] if res else ip

def get_process_id():
    """获取正在运行的进程ID"""
    return os.getpid()

def sleep(second):
    """休眠时间"""
    time.sleep(second)

def parseInt(value, point=2):
    value = round(float(value), point)
    if value%1==0:
        return int(value)
    return value


def work_wechat_send_msg(text, key):
    """企业微信群中的机器人
        key：机器人的token   
    """
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('key', key),
    )
    data = {
        "msgtype": "text",
        "text": {
            "mentioned_mobile_list":[],
            "content": text,
        }
    }
    response = requests.post('https://qyapi.weixin.qq.com/cgi-bin/webhook/send', headers=headers, params=params, json=data)