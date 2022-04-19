import pymongo
import datetime
from urllib import parse
from webspider.config.settings import MONGODB, REPLICASET


class ResponseRecordMongo():
    def __init__(self,  col, database="TEZhuKeTongMessage"):
        myclient = pymongo.MongoClient(MONGODB, replicaset=REPLICASET)
        self.mydb = myclient[database]
        self.col = col

    def save_response(self, response, request, trace):
        if request.retry_times>0:
            return 
        data = {}
        data["response"] = response.text if response else ""
        data["date"] = datetime.datetime.now()
        data["status_code"] = response.status_code if response else 0
        data["url"] = request.url
        data["name"] = request.name
        data["task_id"] = 0
        data["host"] = parse.urlparse(data["url"]).netloc
        data["kw"] = request.requests_kwargs
        if self.col != "spider":
            data["traceback"] = trace
    
        mycol = self.mydb[self.col]
        res = mycol.insert_one(data)
        return res


