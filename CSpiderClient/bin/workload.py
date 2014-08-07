#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2013-11-15
    @author: devin
    @desc:
        作业管理
'''
import random
import json
import jsonlib
import time
from util import timer
from common.task import Task
import threading
from common.logger import logger
from crawler.workload import WorkloadStorable
from util.http_client import HttpClientPool

TASK_TIME_SPAN = 150
COMPLETE_TIME_SPAN = 20
TASK_COUNT = 100

class ControllerWorkload(WorkloadStorable):
    '''
        通过Controller进行workload管理
    '''
    def __init__(self, host, sources = None):
        self.__client = HttpClientPool(host, timeout = 1000, maxsize = 10)
        self.__sources = sources
        self.__sem = threading.Semaphore()
        self.__tasks = []
        self.__tasks_status = []
        #self.__timer = timer.Timer(TASK_TIME_SPAN, self.get_workloads)
        #self.__timer.start()
        self.__timer2 = timer.Timer(COMPLETE_TIME_SPAN, self.complete_workloads)
        self.__timer2.start()


    def add_workload(self, task):
        pass
    
    def get_workloads(self):
        '''
            从master取一批workloads
            get every TASK_TIME_SPAN (s), up to TASK_COUNT
        '''
        task_length = TASK_COUNT - len(self.__tasks)

        if task_length <= 0 :
            return None
        logger.info('Need %d New Tasks'%task_length)
        url = "/workload?count=" + str(task_length)
        result = self.__client.get(url)

        if result == None or result == []:
            return False

        try:
	    result = result.strip('\0').strip()
            tasks = eval(result)
        except Exception,e:
            logger.info('GET TASKS ERROR: '+str(e))
            return False

        logger.info('Get %d New Tasks From Master'%len(tasks))

        for task in tasks:
	    #logger.info("parse string is : %s" % str(task))
            self.__tasks.append(Task.parse(json.dumps(task)))

        return True

    def assign_workload(self):
        '''

        '''
        with self.__sem:
            if len(self.__tasks) == 0:
                logger.info('No Tasks, Get New')
                flag = self.get_workloads()

                if flag != True:
                    return None

        with self.__sem:
            try:
                task = self.__tasks[0]
                del self.__tasks[0]
                logger.info(len(self.__tasks))
                return task
            except Exception,e:
                return None

        return None
    
    def complete_workload(self, task, Error = 0):

        task_status = {"id": task.id, "content": task.content, "source": task.source, "workload_key": task.workload_key, "error": Error}
        self.__tasks_status.append(task_status)

        return True

    def complete_workloads(self):
        import urllib
        #t = [{"id": task.id, "content": task.content, "source": task.source, "workload_key": task.workload_key, "error": Error}]
        with self.__sem:
            result = self.__client.get("/complete_workload?q=" + urllib.quote(jsonlib.write(self.__tasks_status)))
            self.__tasks_status = []

        return True

    def remove_workload(self, task):
        pass
    
    def update_workload(self, task, priority = 0):
        pass
    
    def clear(self):
        '''
            清空作业
        '''
        pass
    
    def add_workloads(self, tasks):
        '''
            添加作业
        '''
        pass
    
    def get_task_status(self, task):
        '''
            获得指定任务的状态
        '''
        pass

