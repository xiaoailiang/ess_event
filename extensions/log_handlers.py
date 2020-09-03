#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 3:10 下午
# @Author  : Yiqiang.wei
# @Site    : KissPython
# @File    : log_handlers.py

import os
import time
import inspect
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not os.path.exists(os.path.join(BASE_DIR, "logs")):
    os.makedirs(os.path.join(BASE_DIR, "logs"))

handlers = {
    logging.DEBUG: os.path.join(BASE_DIR, "logs", "debug.log"),
    logging.INFO: os.path.join(BASE_DIR, "logs", "info.log"),
    logging.ERROR: os.path.join(BASE_DIR, "logs", "error.log")
}


def create_handlers():
    log_levels = handlers.keys()
    for level in log_levels:
        path = os.path.abspath(handlers[level])
        handlers[level] = logging.FileHandler(path)


create_handlers()


class logs_class(object):

    @property
    def now(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def __init__(self, level=logging.DEBUG):
        self.__loggers = {}
        log_levels = handlers.keys()
        for level in log_levels:
            logger = logging.getLogger(str(level))
            logger.addHandler(handlers[level])
            logger.setLevel(level)
            self.__loggers.update({level: logger})

    def get_log_message(self, level, message):
        frame, filename, lineNo, functionName, code, unknowField = inspect.stack()[2]
        '''日志格式：[时间] [类型] [记录代码] 信息'''
        return "[%s] [%s] [%s - %s - %s] %s" % (self.now, level, filename, lineNo, functionName, message)

    def info(self, message):
        message = self.get_log_message("info", message)
        self.__loggers[logging.INFO].info(message)

    def error(self, message):
        message = self.get_log_message("error", message)
        self.__loggers[logging.ERROR].error(message)

    def debug(self, message):
        message = self.get_log_message("debug", message)
        self.__loggers[logging.DEBUG].debug(message)


logs = logs_class()
