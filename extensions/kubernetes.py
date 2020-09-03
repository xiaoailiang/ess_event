#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 3:14 下午
# @Author  : Yiqiang.wei
# @Site    : KissPython
# @File    : kubernetes.py.py

import time
from apps import app
from .notice import Notice
from .log_handlers import logs
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class Kubernetes:
    def __init__(self):
        self.config = config
        self.config_file = app.config.get("KUBERNETES_CONFIG")
        self.load_config()
        self.v1 = client.CoreV1Api()
        self.notice = Notice()

    def load_config(self):
        """ load config """
        self.config.load_kube_config(config_file=self.config_file)

    def node_ready(self, name):
        """ 判断新加入节点是否就绪 60秒"""
        timer = 0
        interval = 10
        flags = False
        while timer <= 60:
            try:
                result = self.v1.read_node(name)
                node_status = result.status.conditions[-1].status
                node_name = result.metadata.name
                if node_status and node_name == name:
                    logs.info("Kubernetes node ready successed name is {}".format(name))
                    flags = True
                    break
                else:
                    logs.info(
                        "Kubernetes node ready check status is error name is {} wait for next check ...".format(name))
                    time.sleep(10)

            except ApiException:
                logs.info("Kubernetes node ready check is non-existent name is {} wait for next check ...".format(name))
            except Exception as exc:
                logs.error("Kubernetes node ready check error name is {} msg is {}".format(name, exc))

            time.sleep(interval)
            timer += interval
        else:
            logs.info("Kubernetes node ready failed name is {}".format(name))
        return flags

    def delete_node(self, name):
        """ 驱逐pod 删除节点 """
        flags = True
        try:
            result = self.v1.delete_node(name=name)
            if result.get("status") == "Success":
                logs.info("Kubernetes Cluster Delete node {} Successed".format(name))
            else:
                logs.info("Kubernetes Cluster Delete node {} Failed".format(name))
        except Exception as exc:
            logs.error("Kubernetes Cluster Delete node Failed msg is {}".format(exc))
        return flags

    def scale_out(self, ip, hostname):
        """ 扩容机器 """
        logs.info("Kubernetes scale_out {} {}".format(ip, hostname))
        return self.node_ready(hostname)

    def scale_in(self, ip, hostname):
        """ 缩容机器 """
        logs.info("Kubernetes scale_in {} {}".format(ip, hostname))
        return self.delete_node(hostname)
