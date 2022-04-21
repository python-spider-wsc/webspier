############请求网络相关的配置###################
REQUEST_TIMEOUT = 10  #超时时间 
USE_SESSION = False   # 是否启用会话
USER_AGENT_TYPE = "chrome" # 随机请求头类型
RETRY_TIMES = 2 # 失败重试次数
SAVE_ERROR_RESPONSE = False
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
# -----------------redis----------------------
REDIS_HOST = None
REDIS_PORT = 6379
REDIS_PWD = None
REDIS_DB = 0
REDIS_TYPE = "queue"
# -------------------mysql----------------------
MYSQL_HOST = None
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PWD = None
MYSQL_DB = 0
##############################################

############# 导入用户自定义的setting #############
try:
    from settings import *
except:
    pass