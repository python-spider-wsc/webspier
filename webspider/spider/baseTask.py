# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/12 13:55:35
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''
# 数据搬运任务

from webspider.utils.log import log
import datetime
from webspider.config import settings
from webspider.db.mysqlDB import BaseModel
from webspider.utils import tools
import traceback

class BaseTask():

    def __init__(self, entry_point="run", is_send_msg=True, **kwargs):
        self.task_id = tools.get_task_code()
        self.start_time = datetime.datetime.now()
        self.entry_point_func = getattr(self, entry_point)
        self.spider_id, _ = tools.parse_cmdline_args()
        self.save_nums = 0
        self.task_mysql = None
        self.is_send_msg=is_send_msg
        self.verify_flag = True

    def start_task(self):
        self.record_before()
        status = 1
        try:
            self.entry_point_func()
        except Exception as e:
            log.error(e)
            log.exception(e)
            text = f"""任务：<font color="comment">{self.name}</font>运行出错。\n
            >环境: **{settings.ENVIRONMENT}**
            >详情: \n`{traceback.format_exc()}`"""
            tools.work_wechat_send_msg(text, settings.WORKWECHATERRORKEY, mobile_list=settings.WORKWECHATPHONES, msg_type="markdown")
            status = 2
        finally:
            self.record_after(status)

    def record_before(self):
        """任务保存到mysql之前的初始化工作"""
        log.info("data task < %s > start running", self.name)
        if not self.spider_id:
            return
        if self.task_mysql is None:
            self.task_mysql = BaseModel(settings.TASK_TABLE, unique_key=["task_code"])
        self.task_mysql.save(task_code=self.task_id, spider_id = self.spider_id or 0, service = tools.get_service_ip(), process_id = tools.get_process_id(), logfile = log.filename or "")

    def send_msg(self, cost_time, status):
        key = self.__dict__.get("wechat_key") or settings.WORKWECHATKEY
        if key and self.is_send_msg:
            text = f"""任务：<font color="warning">{self.name}</font>运行{"成功" if status==1 else "**失败**"}。\n
            >环境: {settings.ENVIRONMENT}
            >耗时: {cost_time}
            >详情: 共保存**{self.save_nums}**条数据"""
            tools.work_wechat_send_msg(text, key, msg_type="markdown")

    def record_after(self, status=1):
        """任务保存到mysql"""
        spent_time = tools.formatSecond((datetime.datetime.now()-self.start_time).seconds)
        log.info("data task < %s > spent time: %s ", self.name, spent_time)
        if not self.spider_id:
            return
        self.send_msg(spent_time, status)
        self.task_mysql.save(task_code=self.task_id, status=status, end_time=datetime.datetime.now(), save_nums = self.save_nums)
        self.verify_task()
        log.info("data task < %s > finish", self.name)

    def verify_task(self):
        """验证此次任务是否成功：通过请求量和保存数据量"""
        sql = "SELECT  AVG(save_nums) save_nums FROM `wsc_task` WHERE spider_id=%s and status=1 and create_time>%s"
        date = self.start_time-datetime.timedelta(days=4)
        res = self.task_mysql.fetchOne(sql, self.spider_id, date.date())
        if res["save_nums"] and abs(self.save_nums-res["save_nums"])/res["save_nums"]>0.25:
            data = {"name":"保存数量", "nums":self.save_nums, "last_nums":int(res["save_nums"])}
            text = f"""爬虫：<font color="comment">{self.name}</font>数据浮动超过25%。\n
            >环境: {settings.ENVIRONMENT}
            >异常指标: 保存数量
            >详情: 近四天平均数量为{data["last_nums"]}，本次数量为{data["nums"]} """
            if self.verify_flag:
                tools.work_wechat_send_msg(text, settings.WORKWECHATERRORKEY, mobile_list=settings.WORKWECHATPHONES, msg_type="markdown", spider=self.name+"数据量")
            else:
                tools.work_wechat_send_msg(text, settings.WORKWECHATERRORKEY, mobile_list=settings.WORKWECHATPHONES, msg_type="markdown")