# import os, sys
# import re
# sys.path.insert(0, os.getcwd())
# sys.path.insert(0, re.sub(r"([\\/]items$)|([\\/]spiders$)", "", os.getcwd()))

__all__ = [
    "spider",
    "core",
    "db",
    "config"
]

# from feapder.core.spiders import Spider, BatchSpider, AirSpider
# from feapder.core.base_parser import BaseParser, BatchParser
# from feapder.network.request import Request
# from feapder.network.response import Response
# from feapder.network.item import Item, UpdateItem
# from feapder.utils.custom_argparse import ArgumentParser
