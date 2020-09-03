#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 3:03 下午
# @Author  : Yiqiang.wei
# @Site    : KissPython
# @File    : config.py.py


class BaseConfig:
    BASE_REGION = "cn-beijing"
    # 阿里云access ID
    ALI_ACCESS_KEY = ""

    # 阿里云access key
    ALI_ACCESS_SECRET = ""

    # 扩容出node节点主机名的前缀 000-999 k8s-s001 k8s-s002 ... k8s-999
    HOSTNAME_PREFIX = "k8s-s"

    # 阿里云mns消息地址
    MNS_ENDPOINT = ""

    # 阿里云mns队列名称
    MNS_QUEUENAME = ""

    # k8s 集群认证文件 主要用于缩容机器接口触发驱逐pod删除节点
    KUBERNETES_CONFIG = ""

    # 阿里云机器人webhook地址，扩容或缩容发送通知
    DINGTALK_WEBHOOK = ""

    # 无用配置
    SECURITYTOKEN = ""


class ProdConfig(BaseConfig):
    DEBUG = False


class DevConfig(BaseConfig):
    DEBUG = True
