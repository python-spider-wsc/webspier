import pymongo
import datetime
from urllib import parse
from webspider.config.settings import MONGODB, replicaSet


class ResponseRecordMongo():
    def __init__(self,  col, database="TEZhuKeTongMessage"):
        myclient = pymongo.MongoClient(MONGODB, replicaset=replicaSet)
        self.mydb = myclient[database]
        self.col = col

    def save_response(self, response, request, trace):
        if request.retry_times>0:
            return 
        data = {}
        data["response"] = response.text if response else ""
        data["date"] = datetime.datetime.now()
        data["status_code"] = response.status_code if response else 0
        data["method"] = request.method
        data["url"] = request.url
        data["host"] = parse.urlparse(data["url"]).netloc
        data["kw"] = request.requests_kwargs
        if self.col != "spider":
            data["traceback"] = trace
    
        mycol = self.mydb[self.col]
        res = mycol.insert_one(data)
        return res


