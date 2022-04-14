# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/11 17:56:46
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''

import argparse
from webspider.commands.create_or_run import Create, Running

def execute():
    parser = argparse.ArgumentParser(description='webspider command:')
    parser.add_argument('params1', type=str, help='命令行必填参数', choices=["create", "run"])
    parser.add_argument('target', type=str, help='命令行必填参数', choices=["spider", "task"])
    parser.add_argument('--path', default=".", help='爬虫或者任务的路径')
    parser.add_argument('--name', required=True, help='爬虫或者任务的名字')
    args = parser.parse_args()

    if args.params1 == "create":
        if args.target == "spider":
            Create().create_spider(args)   
        else:
            print("创建任务：", args.name)
    else:
        if args.target == "spider":
            Running().run(args)
        else:
            print("运行任务：", args.name)



if __name__ == "__main__":
    execute()