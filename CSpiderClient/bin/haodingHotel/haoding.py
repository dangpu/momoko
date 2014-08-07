#!/bin/env python
#coding=UTF-8
'''
    @author:nemo
    @date:2014-04-02
    @desc:
        haoding hotel&room解析，将数据写入数据库
'''

import parser
from haodingParser import haoding_room_task_parser
from haodingParser import haoding_room_request_parser
from common.insert_db import InsertHotel,InsertHotel_room
from common.logger import logger
import datetime
import time
import random

ERR_CODE = 31
DATA_ERR_CODE = 32
DB_ERR_CODE = 33

# 继承Parser类，实现parse和request方法
class haodingParser(parser.Parser):
    def __init__(self):
        pass

    def parse(self,task):
        #解析test，提取出字段
        content = task.content
        source = task.source
        
        #每天日期
        today = str(datetime.datetime.now()).split(' ')[0].replace('-','')

        table_name = ''#today
        
        #任务开始时间
        stime = time.time()
        update_time = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
        logger.info ('haodingHotel: start a new task @ %s'%str(update_time))

        para = []
        error = ERR_CODE
        
        #如果失败，重复抓取的次数，当前为1
        for i in range(2):
            result = haoding_room_task_parser(content)

            try:
                para = result['para']
                error = result['error']
            except Exception,e:
                return error
        
            if para == None or para == []:
                logger.error ('haodingHotel: task failed with %s for %sth time'%(content,i))
                time.sleep(random.randint(1,2))
                continue

            else:
                try:
                    InsertHotel_room(para)
                    etime = time.time()#任务完成时间
                    dur = int((etime - stime) * 1000)
                    logger.info("haodingHotel: task %s finish using %d ms"%(content, dur))
                    return error
                except Exception,e:
                    logger.error('haodingHotel: Insertation Error: %s'%str(e))
                    error = DB_ERR_CODE
                    return error         

        return error


    def request(self,content):

        #content = task.content
        #source = task.source

        result = -1
        #request重复抓两遍，失败则返回-1
        for i in range(2):
            
            result = haoding_room_request_parser(content)
            if result != -1:
                break

        return result

if __name__ == "__main__" :

    task1 = Task()
    task1.content = ''
    result1 = parse(task2.content)

    task2 = Task()
    task2.content = ''
    result2 = request(task2.content)

    #print result1
    #print result2
    
