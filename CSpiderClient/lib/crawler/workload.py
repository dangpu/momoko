#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2013-11-15
    @author: devin
    @desc:
        作业管理
'''

import abc
import threading

class Task(object):
    '''
        保存一个作业
    '''
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def __init__(self):
        pass

class WorkloadStorable(object):
    '''
        作业管理接口
    '''
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def add_workload(self, task):
        '''
            添加作业
        '''
        pass
    
    @abc.abstractmethod
    def add_workloads(self, tasks):
        '''
            添加作业
        '''
        pass
    
    @abc.abstractmethod
    def assign_workload(self):
        '''
            获取一个未处理的作业
        '''
        pass
    
    @abc.abstractmethod
    def complete_workload(self, task, isError = False):
        '''
            完成一个作业，isError用来标识处理过程是否出错
        '''
        pass
    
    @abc.abstractmethod
    def remove_workload(self, task):
        '''
            删除一个task
        '''
        pass
   
    @abc.abstractmethod
    def update_workload(self, task):
        '''
            更新task
        '''
        pass

    @abc.abstractmethod
    def clear(self):
        '''
            清空作业
        '''
        pass
    
    @abc.abstractmethod
    def get_task_status(self, task):
        '''
            获得指定任务的状态
        '''
        pass

class InternalWorkload(WorkloadStorable):
    '''
        作业管理，用内存来进行URL管理
    '''
    def __init__(self):
        self.semaphore = threading.Semaphore()      #互斥访问信号量
        self.visitedURLs = {}       #已访问列表，保存已经访问的URL（除WAITING状态的URL）
        self.unvisitURLs = set()    #等待访问队列，保存未访问的URL（WAITING状态的URL）
    
    def add_workload(self, url):
        #首先，判断url在已访问列表中，如果不在，则添加到等待访问队列;
        #否则不做任何处理
        with self.semaphore:
            if url not in self.visitedURLs:
                self.unvisitURLs.add(url)
            
    def add_workloads(self, urls):
        with self.semaphore:
            for url in urls:            
                if url not in self.visitedURLs:
                    self.unvisitURLs.add(url)
            
    
    def assign_workload(self):
        with self.semaphore:        
            if len(self.unvisitURLs) > 0:
                url = self.unvisitURLs.pop()
                self.visitedURLs[url] = TaskStatus.RUNNING
                return url
            else:           #等待访问队列为空，返回None
                return None
        
    
    def complete_workload(self, url, isError = False):
        #isError为true，设置状态为ERROR，否则设置为COMPLETE
        with self.semaphore:        
            if isError :
                self.visitedURLs[url] = TaskStatus.ERROR
            else:
                self.visitedURLs[url] = TaskStatus.COMPLETE
        
    
    def clear(self):
        #情况已访问列表和等待访问队列
        with self.semaphore:        
            self.visitedURLs.clear()
            self.unvisitURLs.clear()
    
    
    def get_task_status(self, url):
        if url in self.visitedURLs:
            return self.visitedURLs[url]
        else:
            return TaskStatus.WAITING
