#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 3:02 下午
# @Author  : Yiqiang.wei
# @Site    : KissPython
# @File    : mem_storage.py


import threading


class HostMapInstanceClass:
    _instance_lock = threading.Lock()

    def __init__(self):
        self.host_map = {}
        self.cache = {}

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(HostMapInstanceClass, "_instance"):
            with HostMapInstanceClass._instance_lock:
                if not hasattr(HostMapInstanceClass, "_instance"):
                    HostMapInstanceClass._instance = HostMapInstanceClass(*args, **kwargs)
        return HostMapInstanceClass._instance


storage = HostMapInstanceClass()
