#!/usr/bin/env python
#coding=UTF8
'''
    @author: devin
    @time: 2014-02-23
    @desc:
        slave
'''
import threading
import time
from util import http_server
from util import http_client
from util import timer
from util.logger import logger
from info import SlaveInfo
import urllib
import os

HEARTBEAT_TIME_SPAN = 10

class Slave:
    def __init__(self, host, port, master_host, workers, recv_real_time_request = False):
        '''
            初始化
            @param host: 接收实时请求的ip，当recv_real_time_request为True的时候才使用
            @param port: 接收实时请求的端口，当recv_real_time_request为True的时候才使用
            @param master_host: master的ip和端口
            @param workers: 线程组
            @param recv_real_time_request: 是否能接收实时请求，True表示可以接收，其它表示不能
        '''
        if recv_real_time_request:
            self.__server = http_server.HttpServer(host, port)
        self.__client = http_client.HttpClient(master_host)
        # 保存slave的相关信息
        self.info = SlaveInfo()
        self.info.recv_real_time_request = recv_real_time_request
        self.info.server = host
        self.info.server_ip = host + ":" + str(port)
        self.info.path = os.getcwd()
        # timer，用来定时发送heartbeat状态
        self.__timer = timer.Timer(HEARTBEAT_TIME_SPAN, self.heartbeat)
        # 互斥信号量
        self.__sem = threading.Semaphore()
        self.__workers = workers
    
    def run(self):
        '''
            启动slave
        '''
        # register 
        self.register("/modify_thread_num", self.modify_thread_num)

        
        # register to master
        if not self.register_in_master():
            logger.error("Can't register to master.")
            return
        
        # start the timer
        self.__timer.start()
        
        # start the workers
        self.__workers.start()
        
        # start the server
        if self.info.recv_real_time_request:
            self.__server.run()
    
    def register(self, path, func):
        '''
            注册http服务
            @param path: http服务的地址
            @param func: 响应请求的函数
        '''
        if self.info.recv_real_time_request:
            self.__server.register(path, func)

    def heartbeat(self):
        '''
            向master发起心跳请求，上报目前状态
        '''
        data = {"id": self.info.id,
                "thread_num": self.__workers.get_thread_num(), 
                "process_task_num": self.info.process_task_num,
                "error_task_num": self.info.error_task_num,
                "request_task_num": self.info.request_task_num}
        path = "/heartbeat?" + urllib.urlencode(data)
        self.__client.get(path)
    
    def register_in_master(self):
        '''
            向master注册，并获得master分配的id
        '''
        data = {"name": self.info.name,
                "server": self.info.server,
                "path": self.info.path,
                "server_ip": self.info.server_ip,
                "type": self.info.type,
                'recv_real_time_request': self.info.recv_real_time_request}
        path = "/register_slave?" + urllib.urlencode(data)
        id = self.__client.get(path).strip()
        id = id.strip('\0')
        if len(id) == 0 or not id.isdigit():
            return False
        self.info.id = int(id)
        logger.info("slave register id is : %d" % self.info.id)
        return True

    def modify_thread_num(self, params):
        '''
            响应用户或者master的修改线程请求
        '''
        thread_num = params.get("thread_num")
        if thread_num == None or not thread_num.isdigit():
            return False
        thread_num = int(thread_num)
        self.__workers.set_thread_num(thread_num)
        
        return True
