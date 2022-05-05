import pymongo
import datetime
from webspider.config.settings import MONGODB, REPLICASET
from webspider.utils import tools


class ResponseRecordMongo():
    def __init__(self,  col, database="TEZhuKeTongMessage"):
        myclient = pymongo.MongoClient(MONGODB, replicaset=REPLICASET)
        self.mydb = myclient[database]
        self.col = col

    def save_response(self, response, request, spider, trace="", error=None):
        if request.retry_times>0:
            return
        mycol = self.mydb[self.col]
        data = {}
        if self.col != "error":
            data["traceback"] = trace
            data["error_type"] = error
        data["response"] = response.text if response else ""
        data["date"] = datetime.datetime.now()
        data["status_code"] = response.status_code if response else 0
        data["request"] = request.requests_kwargs
        data["task_id"] = spider.task_id
        data["spider_id"] = spider.spider_id
        data["service"] = tools.get_service_ip()
    
        res = mycol.insert_one(data)
        return res


