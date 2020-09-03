#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 3:13 下午
# @Author  : Yiqiang.wei
# @Site    : KissPython
# @File    : core.py

from flask import jsonify
from extensions.mem_storage import storage
from extensions.counter import get_counter
from apps import app


# ip 与 主机名的对应
@app.route("/hostname/<string:ip>")
def hostname(ip):
    if ip in storage.host_map:
        return storage.host_map[ip]
    else:
        hostname = "{}{}".format(app.config.get("HOSTNAME_PREFIX"), ("%03d" % get_counter()))
        storage.host_map[ip] = hostname
        return hostname


@app.route("/all")
def all_hostname():
    return jsonify(storage.host_map)
