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
from webspider.db.baseMQ import BaseMQ
import pickle
import requests
import json


class RedisDB(BaseMQ):
    FUNC_MAP = {
        "set":{"add":"sadd", "get":"spop", "empty":"scard"},
        "queue":{"add":"lpush", "get":"rpop", "empty":"llen"}
    }
    
    def __init__(self, table, category=settings.REDIS_TYPE, serialize="pickle", **kwarg):
        super(RedisDB, self).__init__()
        self.category = category
        self.table = table
        self.connect(**kwarg)
        self.serialize = serialize

    @classmethod
    def get_redis_config(cls):
        headers = {
            'Connection': 'keep-alive',
            'Authorization': 'Basic '+settings.REDIS_Authorization,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
        }
        response = requests.get(settings.REDIS_URL, headers=headers,verify=False)
        res = response.json()
        data = {}
        data['host'], data['port']= res[0]['instances'][0]['ip'].split(':')
        data['password'] = res[0]['instances'][0]['password']
        return data

    def connect(self, **kwarg):
        if not settings.REDIS_URL:
            raise ConnectionError("无redis配置信息, 请配置。。。")
        redis_config = RedisDB.get_redis_config()
        redis_config.update(**kwarg)
        redis_config["max_connections"] = kwarg.get("max_connections",1000)
        POOL = redis.ConnectionPool(**redis_config)
        self.redis = redis.Redis(connection_pool=POOL)
        return self.redis.ping()

    def add(self, data, **kwargs):
        if not self.redis.ping():
            self.connect()
        super().add()
        if self.serialize=="pickle":
            data = pickle.dumps(data)  # 序列化
        elif self.serialize=="json":
            data = json.dumps(data)
        else:
            data = str(data)
        table = kwargs.get("talbe", self.table)
        func = getattr(self.redis, self.__class__.FUNC_MAP[self.category]["add"])
        func(table, data)


    def get(self, **kwargs):
        if not self.redis.ping():
            self.connect()
        table = kwargs.get("talbe", self.table)
        func = getattr(self.redis, self.__class__.FUNC_MAP[self.category]["get"])
        res  = func(table) # 序列化
        if self.serialize=="pickle":
            res = pickle.loads(res)  # 序列化
        elif self.serialize=="json":
            res = json.loads(res)
        return res

    def empty(self, **kwargs):
        table = kwargs.get("talbe", self.table)
        func = getattr(self.redis, self.__class__.FUNC_MAP[self.category]["empty"])
        return func(table)==0

