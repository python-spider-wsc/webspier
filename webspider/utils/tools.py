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
import uuid
import argparse
import datetime

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

class TaskRecordContextManager():
    """任务记录上下文管理器
    """
    def __init__(self):
        self.task_mysql = BaseModel(settings.TASK_TABLE, unique_key=["task_code"])
        self.task_id = get_task_code()
        self.spider_id, _ = parse_cmdline_args()


    def __enter__(self):
        self.time_start = time.time()
        if self.spider_id:
            self.task_mysql.save(task_code=self.task_id, spider_id = self.spider_id, service = get_service_ip(), process_id = get_process_id(), logfile = log.filename or "")
        self._line = sys._getframe().f_back.f_lineno  # 调用此方法的代码的函数
        _file_name = sys._getframe(1).f_code.co_filename  # 哪个文件调了用此方法
        _, self._file_name = os.path.split(_file_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = 1
        log.info("[file: %s] [line: %s] spent time : %s", self._file_name, self._line, time.time() - self.time_start)
        if exc_type:
            status = 2
            exc_str = str(exc_type) + '  :  ' + str(exc_val)
            error = ''.join(traceback.format_tb(exc_tb))+ exc_str
            log.error(error)
        if self.spider_id:
            self.task_mysql.save(task_code=self.task_id, status=status, end_time=datetime.datetime.now())

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


def work_wechat_send_msg(text, key, mobile_list=None):
    """企业微信群中的机器人
        key：机器人的token,
        mobile_list: 提醒人的手机号列表  
    """
    mobile_list = mobile_list or []
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('key', key),
    )
    data = {
        "msgtype": "text",
        "text": {
            "mentioned_mobile_list":mobile_list,
            "content": text,
        }
    }
    requests.post('https://qyapi.weixin.qq.com/cgi-bin/webhook/send', headers=headers, params=params, json=data)

def get_task_code():
    return str(uuid.uuid1())


def parse_cmdline_args():
    """解析命令行参数"""
    argparser = argparse.ArgumentParser(description="spider record manager")
    argparser.add_argument("--id", type=int, help="spider id")
    argparser.add_argument("--save", type=int, nargs='?', const=True, help="save response into mongodb")
    args = argparser.parse_args()
    return args.id, args.save