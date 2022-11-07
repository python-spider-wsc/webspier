# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/19 10:09:19
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
@Desc    :   使用redis作为消息队列
'''

import redis
from redis.exceptions import ConnectionError
from webspider.config import settings
from webspider.utils.log import log
from webspider.db.baseMQ import BaseMQ
import pickle

class RedisDB(BaseMQ):
    FUNC_MAP = {
        "set":{"add":"sadd", "get":"spop", "empty":"scard"},
        "queue":{"add":"lpush", "get":"rpop", "empty":"llen"}
    }
    
    def __init__(self, table, host=settings.REDIS_HOST, port=settings.REDIS_PORT,pwd=settings.REDIS_PWD, db=settings.REDIS_DB, category=settings.REDIS_TYPE, decode_responses=True, max_connections=1000, **kwarg):
        super(RedisDB, self).__init__()
        self.host = host
        self.port = port
        self.pwd = pwd
        self.db = db
        self.category = category
        self.decode_responses = decode_responses
        self.max_connections = max_connections
        self.table = table
        self.reconnect()

    def reconnect(self):
        if not self.host:
            raise ConnectionError("无redis配置信息, 请配置。。。")
        POOL = redis.ConnectionPool(host=self.host, port=self.port, password=self.pwd, max_connections=self.max_connections)
        self.redis = redis.Redis(connection_pool=POOL)
        return self.redis.ping()

    def add(self, item, **kwargs):
        super().add()
        item = pickle.dumps(item) # 序列化
        table = kwargs.get("talbe", self.table)
        self.nums += 1
        func = getattr(self.redis, self.__class__.FUNC_MAP[self.category]["add"])
        func(table, item)


    def get(self, **kwargs):
        table = kwargs.get("talbe", self.table)
        func = getattr(self.redis, self.__class__.FUNC_MAP[self.category]["get"])
        res  = func(table) # 序列化
        return pickle.loads(res)

    def empty(self, **kwargs):
        table = kwargs.get("talbe", self.table)
        func = getattr(self.redis, self.__class__.FUNC_MAP[self.category]["empty"])
        return func(table)==0

