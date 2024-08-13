import pymongo
import datetime
from webspider.config.settings import MONGODB, REPLICASET
from webspider.utils import tools


class ResponseRecordMongo():
    def __init__(self,  col, database="TEZhuKeTongMessage"):
        myclient = pymongo.MongoClient(MONGODB, replicaset=REPLICASET)
        self.mydb = myclient[database]
        self.col = col

    def save_response(self, response, request, spider, trace, error):
        if request.retry_times>1 or self.find_response(spider, error):
            # 同一个错误不需要记录多次
            return
        mycol = self.mydb[self.col]
        data = {}
        if self.col != "error":
            data["traceback"] = None
            data["error_type"] = None
        else:
            data["traceback"] = trace
            data["error_type"] = error
        data["response"] = response.text if response else ""
        data["date"] = str(datetime.datetime.now())
        data["status_code"] = response.status_code if response else 0
        for key in request.requests_kwargs:
            if isinstance(request.requests_kwargs[key], datetime.date):
                request.requests_kwargs[key] = str(request.requests_kwargs[key])
        data["request"] = request.requests_kwargs
        data["task_id"] = spider.task_id
        data["spider_id"] = spider.spider_id
        data["service"] = tools.get_service_ip()
    
        res = mycol.insert_one(data)
        return res

    def find_response(self, spider, error):
        mycol = self.mydb[self.col]
        query = {"task_id":spider.task_id, "error_type":error}
        return mycol.find_one(query)


