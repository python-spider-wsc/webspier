# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/12 11:09:49
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''
import json
import os
import getpass
import datetime
from webspider.config import settings
from webspider.db.mysqlDB import BaseModel


class Record():
    """爬虫或者任务的记录"""
    def __init__(self):
        self.template_path = os.path.abspath(os.path.join(__file__, "../../templates"))
        with open(os.path.join(self.template_path, "record.json"), "r", encoding="utf-8") as f:
            self.record = json.load(f)
        self.__table_spider = None

    @property
    def table_spider(self):
        if self.__table_spider is None:
            self.__table_spider = BaseModel(settings.SPIDER_TABEL, ["name"])
        return self.__table_spider

    def add_record(self, res):
        if not res:
            return
        self.record.update(res)
        self.save_record()
        
        
    def check(self):
        """剔除已经不存在的爬虫或者任务"""
        result = {}
        save_flag = False
        for name in self.record:
            if os.path.exists(self.record[name]):
                result[name] = self.record[name]
            else:
                print("delete {}".format(name))
                save_flag = True
        if save_flag:
            self.record = result
            self.save_record()
    
    def save_record(self):
        with open(os.path.join(self.template_path, "record.json"), "w", encoding="utf-8") as f:
            json.dump(self.record, f)
    
    def export_record(self, args):
        self.check()
        if args.save_mysql:
            if args.name:
                if not self.record.get(args.name):
                    print("不存在该爬虫记录")
                self.save_record_into_mysql(name, self.record[args.name])  
            else:
                for name in self.record:
                    self.save_record_into_mysql(name, self.record[name])    
            print("爬虫记录已保存到mysql")
        else:
            if not os.path.exists("./webspider/templates"):
                print("无法在该目录下备份记录文件")
                return
            with open("./webspider/templates/record.json", "w", encoding="utf-8") as f:
                json.dump(self.record, f)
            print("爬虫记录备份成功")

    def save_record_into_mysql(self, name, path):
        if not settings.DATABASES: # 没有配置mysql信息
            raise Exception("没有配置mysql信息")
        self.table_spider.save(name=name, path=os.path.abspath(path), log=os.path.abspath(os.path.join(settings.LOG_PATH, name+'.log')))


class Create(Record):
    """用于创建爬虫和任务"""

    def __init__(self) -> None:
        super(Create, self).__init__()

    def create(self, args, template):
        template = self.deal_file_info(template)
        suffix = ".py"
        if args.path[-3:] == suffix:
            path = args.path
        else:
            filename = args.name+suffix
            path = os.path.join(args.path, filename)
        # 判断文件是否存在
        if args.save_mysql:
            self.save_record_into_mysql(args.name, path)
        name = args.name[0].upper()+args.name[1:]
        if os.path.exists(path):
            flag = input("该文件已经存在,是否覆盖,y/n: ")
            if flag.lower() != "y":
                return
        result = {args.name:path}
        template = template.replace("${object_name}", name).replace("${spider_name}", args.name)
        with open(path, 'w', encoding="utf-8") as f:
            f.write(template)
        self.create_setting_file(path)
        return result

    def create_setting_file(self, path):
        # 判断配置文件setting是否存在和创建
        path, _ = os.path.split(path)
        file = os.path.join(path, "settings.py")
        if os.path.exists(file):
            print("目录中已存在配置文件: settings.py")
        else:
            template_path = os.path.join(self.template_path, "settings.tmpl")
            with open(template_path, 'r', encoding="utf-8") as f:
                template = f.read()
            flag = input("是否创建配置文件, y/n: ")
            if flag == "y":
                with open(file, 'w', encoding="utf-8") as f:
                    f.write(template)
        
    def deal_file_info(self, file):
        user = getattr(settings, "USER", getpass.getuser())
        file = file.replace("{DATE}", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        file = file.replace("{USER}", user)
        return file

    def create_spider(self, args):
        template_path = os.path.join(self.template_path, "spider.tmpl")
        with open(template_path, 'r', encoding="utf-8") as f:
            template = f.read()
        result = self.create(args, template)
        self.add_record(result)
        print("创建爬虫成功")


class Running(Record):
    """运行任务或者爬虫"""

    def __init__(self):
        super(Running, self).__init__()

    def run(self, args):
        if args.save_mysql:
            res = self.table_spider.find({"name":args.name}, columns=("id", "path"))
            if not res:
                raise Exception("MYSQL中不存在该爬虫")
            spider_id = res["id"]
            path = res["path"]
            os.system('python '+path+" --id "+str(spider_id))
        else:
            path = self.record.get(args.name) # 查看是否记录了运行文件
            if not path:
                path = os.path.join(args.path, args.name+".py")
            if not os.path.exists(path): #没找到路径
                raise Exception("未找到爬虫文件: {}, 请输入路径参数 --path".format(args.name))
            os.system('python '+path)
        if args.name not in self.record:
            self.record[args.name] = os.path.abspath(path)
            self.save_record()

