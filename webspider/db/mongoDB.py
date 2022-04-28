import pymongo
import datetime
from webspider.config.settings import MONGODB, REPLICASET


class ResponseRecordMongo():
    def __init__(self,  col, database="TEZhuKeTongMessage"):
        myclient = pymongo.MongoClient(MONGODB, replicaset=REPLICASET)
        self.mydb = myclient[database]
        self.col = col

    def save_response(self, response, request, trace="", error=None):
        if request.retry_times>0:
            return
        mycol = self.mydb[self.col]
        data = {}
        if self.col != "error":
            # 同一任务同一错误同一只记录一次
            data["traceback"] = trace
            data["error_type"] = error
            if mycol.find_one({"task_id":data["task_id"], "error_type":data["error_type"]}):
                return
        data["response"] = response.text if response else ""
        data["date"] = datetime.datetime.now()
        data["status_code"] = response.status_code if response else 0
        data["name"] = request.name
        data["task_id"] = 0
        data["spider_id"] = 0
        data["service"] = 0
    
        res = mycol.insert_one(data)
        return res


