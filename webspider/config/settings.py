############请求网络相关的配置###################
REQUEST_TIMEOUT = 10  #超时时间 
USE_SESSION = False   # 是否启用会话
USER_AGENT_TYPE = "chrome" # 随机请求头类型
RETRY_TIMES = 2 # 失败重试次数
SAVE_ERROR_RESPONSE = False
SLEEP_TIME = 0 # 休眠时间（秒）
##############################################

###############日志模块的配置###################
LOG_LEVEL= "DEBUG"
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 5
LOG_ENCODING = "utf8"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [<pid: %(process)s>] [<tid: %(thread)d>] -- %(filename)s[line:%(lineno)d] %(message)s"
PRINT_EXCEPTION_DETAILS = True
LOG_PATH = "logs"
##############################################

###############数据库相关配置###################
# -------------爬虫的几张表--------------------
MYSQL = dict(host=None, user="root", password=None, database=None, port=3306)
SPIDER_TABEL = "wsc_spider"
TASK_TABLE = "wsc_task"
SERVICE_TABLE = "wsc_service"
REQUEST_TABLE = "wsc_request"
# -----------------redis----------------------
REDIS_HOST = None
REDIS_PORT = 6379
REDIS_PWD = None
REDIS_DB = 0
REDIS_TYPE = "queue"
# ------------------------------------------
DATABASES = None
##############################################

###############消息推送###################
WORKWECHATKEY=None
##############################################

############# 导入公用的爬虫setting #############
try:
    import os, sys
    sys.path.insert(0, os.getenv("SettingPath"))
    from setting import *
except:
    pass

############# 导入公每个爬虫各自的setting #############
try:
    from settings import *
except:
    pass