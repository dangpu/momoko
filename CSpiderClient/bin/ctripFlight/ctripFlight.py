#!usr/bin/env python
#coding=UTF-8
'''
    @author:nemo
    @date:2014-04-02
    @desc:
        ctripFlight机票解析，将数据写入数据库
'''

import parser
import jsonlib
from ctripFlightParser import ctripFlight_task_parser
from ctripFlightParser import ctripFlight_request_parser
from common.insert_db import InsertFlight
from common.logger import logger
from common.task import Task
import datetime
import time
import random

ERR_CODE = 31
DATA_ERR_CODE = 32
DB_ERR_CODE = 33

# 继承Parser类，实现parse和request方法
class ctripFlightParser(parser.Parser):
    def __init__(self):
        pass

    def parse(self,task):
         #解析test，提取出字段
        content = task.content
        source = task.source
        
        #数据表名，每天日期
        today = str(datetime.datetime.now()).split(' ')[0].replace('-','')
        #table_name = today
        table_name = ''
        
        #任务开始时间
        stime = time.time()
        update_time = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
        logger.info('ctripFlightFlight: start a new task @ %s'%str(update_time))
        
        #初始化参数
        para = []
        error = ERR_CODE

        #如果失败，重复抓取的次数
        for i in range(2):
            #返回值是一个dict，{'para':[(),()],'error':0}
            result = ctripFlight_task_parser(content)

            try:
                para = result['para']
                error = result['error']
            except Exception,e:
                logger.error('ctripFlight error: Wrong Result Format %s'%str(e))
                return error
            
            if para == None or para == []:
                time.sleep(random.randint(1,2))
                continue
                
            else:
                try:
                    InsertFlight(para)
                    etime = time.time()#任务完成时间
                    dur = int((etime - stime) * 1000)
                    logger.info('task finish with %s using %d ms' %(content, dur))
                    return error
                except Exception,e:
                    logger.error('ctripFlight: Insertation Error: %s'%str(e))
                    error = DB_ERR_CODE
                    return error

        return error

    def request(self,content):

        result = -1
        #request重复抓两遍，失败则返回-1
        for i in range(2):

            result = ctripFlight_request_parser(content)

            if result != -1:
                break

        return result

if __name__ == "__main__":
    
    Parser = ctripFlightParser()
    
    task = Task()
    task.content = 'BJS&PAR&20140602'
    task.source = 'ctripFlight'

    result = Parser.parse(task)

    task2 = Task()
    task2.content = 'AY058_AY735-PVG-AGP|20140620_09:20|ctrip::ctrip'
    task2.source = 'ctripFlight'

    result2 = Parser.request(task2.content)

    print str(result)
    print str(result2)
