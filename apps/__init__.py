#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 2:53 下午
# @Author  : Yiqiang.wei
# @Site    : KissPython
# @File    : __init__.py.py


from flask import Flask

app = Flask(__name__)

app.config.from_object("config.ProdConfig")

from api import *

# 线程方式启动消息监听队列
import threading
from extensions.core import AliAPI

threading.Thread(target=AliAPI().receive_msg, args=()).start()
