#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 3:21 下午
# @Author  : Yiqiang.wei
# @Site    : KissPython
# @File    : counter.py


counter = 10


def get_counter():
    global counter
    counter += 1
    return counter
