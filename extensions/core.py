#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 3:14 下午
# @Author  : Yiqiang.wei
# @Site    : KissPython
# @File    : core.py


import time
import threading
from apps import app
from mns.queue import *
from mns.topic import *
from mns.subscription import *
from mns.account import Account
from extensions.mem_storage import storage
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.ModifyInstanceAttributeRequest import ModifyInstanceAttributeRequest
from aliyunsdkecs.request.v20140526.RebootInstanceRequest import RebootInstanceRequest
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.acs_exception.exceptions import ClientException
from .log_handlers import logs
from .counter import get_counter
from .kubernetes import Kubernetes


class AliAPI:
    def __init__(self):
        self.client = AcsClient(
            app.config.get("ALI_ACCESS_KEY"),
            app.config.get("ALI_ACCESS_SECRET"),
            app.config.get("BASE_REGION"))
        self.account = Account(
            app.config.get("MNS_ENDPOINT"),
            app.config.get("ALI_ACCESS_KEY"),
            app.config.get("ALI_ACCESS_SECRET"), "")
        self.wait_seconds = 10
        self.kube = Kubernetes()

    def reboot_ecs(self, ecs_id):
        """
        reboot ecs
        :param ecs_id:
        :return:
        """
        try:
            request = RebootInstanceRequest()
            request.set_accept_format('json')
            request.set_InstanceId(ecs_id)
            response = self.client.do_action_with_exception(request)
            logs.info("reboot ecs {} successed result is {}".format(ecs_id, response))
            return True
        except ServerException as exc:
            logs.info("reboot ecs failed msg is {}".format(exc))

    def set_ecs(self, ecs_id, ecs_hostname, ecs_instancename):
        """
        set ecs hostname
        :param ecs_id:
        :param ecs_hostname:
        :param ecs_instancename:
        :return:
        """
        try:
            request = ModifyInstanceAttributeRequest()
            request.set_accept_format('json')

            request.set_InstanceId(ecs_id)
            request.set_InstanceName(ecs_instancename)
            response = self.client.do_action_with_exception(request)
            logs.info("set ecs ecs_id is {} ecs_hostname is {} ecs_instancename is {} response is {}".format(ecs_id,
                                                                                                             ecs_hostname,
                                                                                                             ecs_instancename,
                                                                                                             response))
            return True
        except ServerException as exc:
            logs.error("set ecs failed msg is {}".format(exc))

    def get_ecs_info(self, ecs_id):
        """
        get ecs ip and hostname
        :param ecs_id:
        :return:
        """
        ip, hostname = None, None
        try:
            request = DescribeInstancesRequest()
            request.set_accept_format('json')
            request.set_InstanceIds([ecs_id, ])
            response = json.loads(self.client.do_action_with_exception(request))
            # 私有网络IP
            ip = response.get("Instances").get("Instance")[0].get("VpcAttributes").get("PrivateIpAddress").get(
                "IpAddress")[0]
            hostname = response.get("Instances").get("Instance")[0].get("HostName")
        except ServerException as exc:
            logs.error("get ecs info failed msg is {}".format(exc))
        finally:
            return ip, hostname

    def handlers(self, transiton, ecs_id, hostname, ip, scaling_groupname):
        """
        响应伸缩组活动
        :param transiton:
        :param ecs_id:
        :param hostname:
        :param ip:
        :param scaling_groupname:
        :return:
        """
        assert self.set_ecs(ecs_id, hostname, hostname), AssertionError('set ecs failed.')
        if ip and hostname:
            if hasattr(self.kube, transiton.lower()):
                result = getattr(self.kube, transiton.lower())(ip, hostname)
                if not result:
                    logs.info("Reboot Ecs id is {} hostname is {}".format(ecs_id, hostname))
                    self.reboot_ecs(ecs_id)

            # 发送钉钉通知
            self.kube.notice.send_mardown(
                title='伸缩组活动', text='#### 伸缩组活动\n'
                                    '> \n\n'
                                    '> - 伸缩组名称   {}\n'
                                    '> - 动作类型   **{}**\n'
                                    '> - ECS服务器名称    {}\n'
                                    '> - ECS服务器IP     {}\n'
                                    '> ###### {} \n'.format(scaling_groupname,
                                                            "缩容机器" if transiton == "SCALE_IN" else "扩容机器",
                                                            hostname, ip,
                                                            time.strftime("%Y-%m-%d %H:%M:%S",
                                                                          time.localtime()))
            )

    def receive_msg(self, queue_name=app.config.get("MNS_QUEUENAME")):
        queue = self.account.get_queue(queue_name)
        while 1:
            try:
                recv_msg = queue.receive_message(self.wait_seconds)
                message_body = bytes.decode(recv_msg.message_body)
                change_msg_vis = queue.change_message_visibility(recv_msg.receipt_handle, 35)
                self.delete_msg(change_msg_vis)
                try:
                    message_body = json.loads(message_body)
                except json.decoder.JSONDecodeError:
                    logs.debug("json decoder failes.")

                # 只处理dict类型数据
                if type(message_body) is dict:
                    logs.info("recv msg is {}".format(message_body))
                    transiton = message_body.get("content").get("lifecycleTransition")
                    if transiton not in storage.cache:
                        storage.cache[transiton] = []
                    scaling_groupname = message_body.get("content").get("scalingGroupName")
                    for ecs_id in message_body.get("content").get("instanceIds"):
                        if ecs_id not in storage.cache[transiton]:
                            storage.cache[transiton].append(ecs_id)
                            ip, _ = self.get_ecs_info(ecs_id)
                            if ip in storage.host_map:
                                hostname = storage.host_map[ip]
                            else:
                                # 拼接主机名
                                hostname = "{}{}".format(app.config.get("HOSTNAME_PREFIX"), ("%03d" % get_counter()))
                                storage.host_map[ip] = hostname

                            # 线程处理
                            threading.Thread(
                                target=self.handlers,
                                args=(transiton, ecs_id, hostname, ip, scaling_groupname)).start()

            except MNSExceptionBase as e:
                logs.error("recv msg failed {}".format(e))

    def delete_msg(self, change_msg_vis, queue_name=app.config.get("MNS_QUEUENAME")):
        queue = self.account.get_queue(queue_name)
        queue.delete_message(change_msg_vis.receipt_handle)
        logs.info("del msg {}".format(change_msg_vis.receipt_handle))
