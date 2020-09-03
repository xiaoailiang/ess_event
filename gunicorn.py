#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/4/27 7:42 下午
# @Author  : Yiqiang.wei
# @Site    : KissPython
# @File    : gunicorn.py.py



import os

logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

bind = "0.0.0.0:5000"
backlog = 64
worker_class = "sync"
workers = 1
threads = 1
loglevel = "info"
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'

accesslog = os.path.join(logs_dir, "gunicorn_access.log")
errorlog = os.path.join(logs_dir, "gunicorn_error.log")

proc_name = "apps"