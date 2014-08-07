#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2013-11-21
    @author: devin
    @desc:
        http client
'''
import httplib
import threading
from conn_util import is_connection_dropped


class HttpClient:
    def __init__(self, host, timeout = 1000):
        '''
            初始化
            @param host:  服务器地址
            @param timeout: 连接超时时间，单位为秒
        '''
        self.host = host
        self.conn = httplib.HTTPConnection(self.host, timeout = timeout)
        # 互斥信号量，保证同时只有一个线程使用该连接
        self.sem = threading.Semaphore()
        self.counter = 0
        self.timeout = timeout

    def get(self, path):
        '''
            发送GET请求
            @param path: 为请求地址
            @return: 返回服务器响应结果
        '''
        with self.sem:
            if self.conn and is_connection_dropped(self.conn):
                print "connection is dropped"
                self.conn.close()
                self.conn = httplib.HTTPConnection(self.host, timeout = self.timeout)
            self.conn.request("GET", path)
            ret = self.conn.getresponse()
            return ret.read()

    def __del__(self):
        self.conn.close()

class HttpClientPool:
    def __init__(self, host, timeout = 1000, maxsize = 3):
        '''
            初始化
            @param host:  服务器地址
            @param timeout: 连接超时时间，单位为秒
        '''
        self.__host = host
        import urllib3
        self.__pool = urllib3.HTTPConnectionPool(host, timeout = timeout, maxsize = maxsize)
    
    def get(self, path):
        '''
            发送GET请求
            @param path: 为请求地址
            @return: 返回服务器响应结果
        '''
        r = self.__pool.request('GET', path)
        if r.status == 200:
            return r.data
        return None

if __name__ == "__main__":
    HOST = "115.29.161.44:8089"
    client = HttpClient(HOST)
    print client.get("/test")

