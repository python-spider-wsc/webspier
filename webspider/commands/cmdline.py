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
    parser.add_argument('action', type=str, help='命令行必填参数',nargs='?', default=None, choices=["create", "run"])
    parser.add_argument('--path', default=".", help='爬虫的路径')
    parser.add_argument('-n', '--name', help='爬虫的名字')
    parser.add_argument('-c', '--check', nargs='?', const=True, help='剔除无效爬虫')
    parser.add_argument('-e', '--export', nargs='?', const=True, help='导出爬虫列表文件')
    parser.add_argument('--save_mysql', nargs='?', const=True, help='将爬虫记录保存到mysql')
    parser.add_argument('--save_response', nargs='?', const=True, help='将中间响应结果保存到mongo')
    args = parser.parse_args()
    if args.action:
        if not args.name:
            parser.error("缺少爬虫名字")
        if args.action == "create":
            Create().create_spider(args) 
        elif args.action == "run":
            Running().run(args)
    elif args.check:
        Create().check() 
    elif args.export:
        Create().export_record(args)



if __name__ == "__main__":
    execute()