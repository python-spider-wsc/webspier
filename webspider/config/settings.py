# -------请求网络相关的配置----------
REQUEST_TIMEOUT = 10  #超时时间 
USE_SESSION = False   # 是否启用会话
USER_AGENT_TYPE = "chrome" # 随机请求头类型
RETRY_TIMES = 2 # 失败重试次数
SAVE_ERROR_RESPONSE = True
# -----------------------------

############# 导入用户自定义的setting #############
try:
    from settings import *
except:
    pass