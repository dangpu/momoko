#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2014-02-23
    @author: devin
    @desc:
       抓取线程 
'''
import threading
import time
import datetime
from util.logger import logger


class Worker(threading.Thread):
    '''
        工作线程
    '''
    def __init__(self, workers, thread_name, func):
        '''
        '''
        self.__workers = workers
        self.__busy = False
        self.thread_name = thread_name
        self.__func = func
        threading.Thread.__init__(self, None, None, self.thread_name, (), {})
        logger.info("%s init complete" % self.thread_name)
    
    def __del__(self):
        #threading.Thread.__del__(self)
        pass
    
    def run(self):
        '''
        '''
        self.__busy = True
        
        while( self.__busy ):
            self.__func()

        self.__busy = False
        logger.info("%s stop" %self.thread_name)
    
    def is_busy(self):
        return self.__busy
    
    def stop(self):
        self.__busy = False
        time.sleep(0.5)         #释放CPU


class Workers:
    '''
    '''
    def __init__(self, func, thread_num = 10):
        self.__workers = []             # 存放所有的workers
        self.__func = func
        self.__index = 0
        for i in range(thread_num):
            self.add_worker()
        
    def start(self):
        '''
            启动线程
        '''
        for worker in self.__workers:
            worker.start()

    def add_worker(self):
        '''
            添加一个worker
        '''
        self.__index += 1
        worker = Worker(self, "work_thread_" + str(self.__index), self.__func)
        self.__workers.append(worker)
        return worker
        
    def stop_worker(self, worker):
        '''
            停止一个worker
        '''
        worker.stop()
    
    def status(self):
        for worker in self.__workers:
            print str(datetime.datetime.now()), worker.thread_name , worker.is_busy(), worker.isAlive()
    
    def stop(self):
        '''
            停止所有的workers线程
        '''
        for worker in self.__workers:
            worker.stop()
        time.sleep(1)
    
    def check_alive_worker(self):
        '''
            遍历所有线程，确认线程是否alive，对应不是alive的线程，从workers里面删除
        '''
        self.__workers = filter(lambda w : w.isAlive() and w.is_busy(), self.__workers)
    
    def get_thread_num(self):
        '''
            返回当前的线程数目，只统计运行的线程
        '''
        self.check_alive_worker()
        return len(self.__workers)
    

    
    def set_thread_num(self, thread_num):
        '''
            调整线程的个数
        '''
        self.check_alive_worker()
        i = len(self.__workers)
        
        if i < thread_num :             # 线程数不够，增加线程
            while i < thread_num:
                i += 1
                worker = self.add_worker()
                worker.start()
        elif i > thread_num:            # 线程数过多，stop一些线程
            while i > thread_num:
                i -= 1
                worker = self.__workers.pop()
                worker.stop()
