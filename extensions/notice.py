#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 3:19 下午
# @Author  : Yiqiang.wei
# @Site    : KissPython
# @File    : notice.py


import json
import requests
from apps import app
from .log_handlers import logs


class Notice:
    def __init__(self, webhook=app.config.get("DINGTALK_WEBHOOK")):
        self.webhook = webhook

    def send_mardown(self, title, text, is_at_all=False, at_mobiles=[]):
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {}
        }
        if is_at_all:
            data["at"]["isAtAll"] = is_at_all

        if at_mobiles:
            at_mobiles = list(map(str, at_mobiles))
            data["at"]["atMobiles"] = at_mobiles

        return self.post(data)

    def post(self, data):
        try:
            headers = {'Content-Type': 'application/json'}
            result = requests.post(self.webhook, data=json.dumps(data), headers=headers)
            logs.info("Dingtalk request params is {} code is {} response is {}".format(
                data,
                result.status_code,
                result.json())
            )
        except Exception as exc:
            logs.info("Dingtalk request error msg is {}".format(exc))
