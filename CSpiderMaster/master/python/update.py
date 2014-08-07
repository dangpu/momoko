#!/usr/bin/env python
#coding=UTF8
'''
    @author: zhangyang
    @time: 2014.07.24
    @desc:
        定时向server发请求，触发WorkloadMaster中的更新任务函数
'''
import sys
sys.path.append('/home/workspace/spider/CSpiderMaster/master/python/util')

import http_server
import http_client

def sendUpdateReq():
    client = http_client.HttpClient("112.124.18.14:8088")
    client.get("/updateTasks?")


if __name__ == '__main__':
	sendUpdateReq()
