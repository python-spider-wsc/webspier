# -*- encoding: utf-8 -*-
'''
@Time    :   2022/04/11 15:29:24
@Author  :   Shucheng wang 
@Version :   1.0
@Contact :   wsc352@126.com
'''

from os.path import dirname, join
from sys import version_info

import setuptools


if version_info < (3, 6, 0):
    raise SystemExit("Sorry! webspider requires python 3.6.0 or later.")

with open(join(dirname(__file__), "webspider/VERSION"), "rb") as f:
    version = f.read().decode("ascii").strip()


packages = setuptools.find_packages()
requires = [
    "better-exceptions>=0.2.2",
    "DBUtils>=2.0",
    "PyMySQL>=0.9.3",
    "redis>=2.10.6,<4.0.0",
    "requests>=2.22.0",
    "pymongo>=3.10.1",
    "urllib3>=1.22",
]


setuptools.setup(
    name="webspider",
    version=version,
    author="wsc352",
    license="MIT",
    author_email="wsc352@126.com",
    python_requires=">=3.6",
    description="自定义爬虫模块",
    install_requires=requires,
    entry_points={"console_scripts": ["webspider = webspider.commands.cmdline:execute"]},
    packages=packages,
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
)