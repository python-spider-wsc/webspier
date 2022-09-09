import requests
from requests.adapters import HTTPAdapter
import webspider.config.settings as setting
from webspider.core import user_agent
from webspider.core.response import MyResponse
from webspider.utils.log import log
from webspider.utils import tools

class Request():
    user_agent_pool = user_agent
    __REQUEST_ATTRS__ = {
        "params", "data", "headers", "cookies", "files", "auth", "timeout",
        "allow_redirects", "proxies", "hooks", "stream", "verify", "cert", "json",
    }
    def __init__(
        self,
        method="GET",
        url="",
        retry_times=0,
        parser_name=None,
        callback=None,
        use_session=None,
        save_response = False,
        priority = 0,
        **kwargs,
    ):
        self.method=method
        self.url = url
        self.retry_times = retry_times
        self.parser_name = parser_name
        self.callback = callback
        self.use_session = setting.USE_SESSION if use_session is None else use_session  # self.use_session 优先级高
        self.save_response = save_response  # 是否保存请求结果
        self.priority = priority

        self.requests_kwargs = {}
        for key, value in kwargs.items():
            if key in self.__class__.__REQUEST_ATTRS__:  # 取requests参数
                self.requests_kwargs[key] = value

            self.__dict__[key] = value

    def __repr__(self):
        try:
            return "<Request {}>".format(self.url)
        except:
            return "<Request {}>".format(str(self.to_dict)[:40])

    def __setattr__(self, key, value):
        """
        针对 request.xxx = xxx 的形式, 更新reqeust及内部参数值
        @param key:
        @param value:
        @return:
        """
        self.__dict__[key] = value

        if key in self.__class__.__REQUEST_ATTRS__:
            self.requests_kwargs[key] = value

    @property
    def _session(self):
        if not self.__class__.session:
            self.__class__.session = requests.Session()
            # pool_connections – 缓存的 urllib3 连接池个数  pool_maxsize – 连接池中保存的最大连接数
            http_adapter = HTTPAdapter(pool_connections=1000, pool_maxsize=1000)
            # 任何使用该session会话的 HTTP 请求，只要其 URL 是以给定的前缀开头，该传输适配器就会被使用到。
            self.__class__.session.mount("http", http_adapter)

        return self.__class__.session

    def get_response(self):
        """
        获取带有selector功能的response
        """
        # 每次请求的休眠时间
        tools.sleep(self.__dict__.get("sleep_time", setting.SLEEP_TIME))
        # 设置超时默认时间
        self.requests_kwargs.setdefault("timeout", setting.REQUEST_TIMEOUT)
        # 随机user—agent
        if self.__dict__.get("random_user_agent"):
            headers = self.requests_kwargs.get("headers", {})
            ua = self.__class__.user_agent_pool.get(setting.USER_AGENT_TYPE)
            headers.update({"User-Agent": ua})
            self.requests_kwargs.update(headers=headers)
        if self.use_session:
            response = self._session.request(self.method, self.url, **self.requests_kwargs)
        else:
            response = requests.request(self.method, self.url, **self.requests_kwargs)
        return MyResponse(response)

    def __gt__(self,other): #优先级比较
       return self.priority<other.priority

    def __ge__(self,other): #优先级比较
       return self.priority<=other.priority

