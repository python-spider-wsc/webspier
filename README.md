# webspider框架
该框架由四个组件，两个队列和一个数据对象构成  
组件：
+ 初始分发器
+ 下载器
+ 解析器
+ 存储器  

队列：
+ 待下载队列  
  由下载器监听，回调解析器中的函数解析
+ 待存储队列  
  由存储器监听，回调数据对象中的函数保存

数据对象：主要用于指定保存的字段和方法

## 生命周期
1、 初始分发器: 由用户编写，提供初始的下载请求
2、 初始化hook: 提供一些前置变量的初始化， 针对整个任务
3、 请求前hook: 在请求页面之前，针对每个请求，例如：随机UA，参数加密
4、 请求
5、 请求后hook，主要对请求结果的处理
6、 解析： 由用户编写
7、 存储前hook： 在数据存储之前的操作：是否入库以及数据清洗
8、 存储
9、 存储后hook
10、任务结束

## 常用命令行
1、创建爬虫
`
webspider create --name baidu 
`
之后会自动创建爬虫文件 baidu.py 和 配置文件 setting.py
``` 
class Baidu(BaseSpider):
    name="baidu"

    def __init__(self, *args, **kwargs):
        super(Baidu, self).__init__(*args, **kwargs)
        self.response_queue = MemoryDB() # 待解析队列
        self.database_queue = MemoryDB() # 待存储队列

    def start_requests(self):
        """初始化任务"""
        yield Request(url="https://www.baidu.com")

    def parse(self, request, response):
        """网页解析"""
        pass
    
    def before_request(self, request):
        """请求之前的hook函数"""
        request.random_user_agent=True # 随机请求头

    def check_reponse(self, request,  response):
        """检测请求的结果是否符合预期"""
        return True


if __name__ == "__main__":
    # log.set_log_config(name="baidu.log") # 日志的存储位置
    Baidu().run()
```
其中可以通过`--save-mysql`指定是否保存到mysql，该参数很重要，表示是否纳入监控平台  
2、运行爬虫
`webspider run --name baidu `

其中可以通过`--save_response`将请求结果保存到mongodb， 同样指定`--save-mysql`将记录保存到mysql

## 优缺点

### 优点  
+ 编写爬虫更加简单，只需要重点关注**初始分发器**和**解析器**这两个组件
+ 内置功能更加丰富：
  1、运行记录自动保存，包括请求的次数，成功次数，入库数据量和异常记录，起始和结束时间。
  2、中间结果保存
  3、任务完成提醒: 任务结束之后，将发送企业微信消息
  4、内置多线程：可以配置多个下载器进程
  5、解析结果自动保存到mysql
  6、异常日志提醒：将日志发送企业微信消息或邮箱
+ 将爬虫快速纳入监控和调度程序
### 缺点
+ 配置文件问题：每个爬虫文件指定一个配置文件，过于繁琐
+ 命令行问题：如何优雅的将webspider的命令行参数传给python
+ 多进程任务分发问题
