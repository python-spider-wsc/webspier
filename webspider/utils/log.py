# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/15 09:36:00
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''

import logging
from logging.handlers import RotatingFileHandler
from concurrent_log_handler import ConcurrentRotatingFileHandler # 多进程加锁日志
from webspider.config import settings
from better_exceptions import format_exception
import os, sys

def get_logger(name=None, path=None, log_level=None, max_bytes=None, backup_count=None, encoding=None, is_mp=False):
    if name: # 如果有名字，表示存储到日志文件中
        path = path or settings.LOG_PATH
        max_bytes = max_bytes or settings.LOG_MAX_BYTES
        backup_count = backup_count or settings.LOG_BACKUP_COUNT
        encoding = encoding or settings.LOG_ENCODING
        formatter = logging.Formatter(settings.LOG_FORMAT)
        if settings.PRINT_EXCEPTION_DETAILS:
            formatter.formatException = lambda exc_info: "".join(format_exception(*exc_info))
        logger = logging.getLogger(name[:-4])
        log_level = log_level or settings.LOG_LEVEL
        logger.setLevel(log_level)
        if path and not os.path.exists(path):
            os.makedirs(path)
        handler = ConcurrentRotatingFileHandler if is_mp else RotatingFileHandler
        handler = handler(
            filename=os.path.join(path, name), 
            maxBytes=max_bytes, 
            backupCount=backup_count,
            encoding=encoding
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        logger = logging.getLogger("console")
        logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.stream = sys.stdout
        formatter = logging.Formatter("[%(levelname)s]: %(filename)s[line:%(lineno)d] --  %(message)s")
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    _handler_list = []
    _handler_name_list = []
    # 检查是否存在重复handler
    for _handler in logger.handlers:
        if str(_handler) not in _handler_name_list:
            _handler_name_list.append(str(_handler))
            _handler_list.append(_handler)
    logger.handlers = _handler_list
    return logger


class Log:
    log = None

    def set_log_config(self, **kw):
        self.config = kw
        path = self.config.get("path", ".")
        file = self.config.get("name")
        self.filename = os.path.join(path, file) if file else ""
    
    def __getattr__(self, name):
        # 调用log时再初始化，为了加载最新的setting
        if name in ["set_log_filename", "filename", "config"]:
            return self.__dict__.get(name)
        if name == "filename":
            return getattr(self, name)
        if self.__class__.log is None:
            self.__class__.log = get_logger(**self.__dict__.get("config", {}))
        return getattr(self.__class__.log, name)

    @property
    def debug(self):
        return self.__class__.log.debug

    @property
    def info(self):
        return self.__class__.log.info

    @property
    def warning(self):
        return self.__class__.log.warning

    @property
    def exception(self):
        return self.__class__.log.exception

    @property
    def error(self):
        return self.__class__.log.error

    @property
    def critical(self):
        return self.__class__.log.critical

log = Log()

