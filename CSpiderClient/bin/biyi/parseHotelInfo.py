#! /usr/bin/env python
#coding=UTF8

'''
    @author:fangwang
    @date:2014-04-23
    @desc:crawl and parse biyi hotel data
'''

import sys
sys.path.append('/home/workspace/spider/SpiderClient/bin/common/')
import biyiHotelParser
from insert_db import InsertHotel
from logger import logger
import time
import random

fileHandle = open('/home/workspace/spider/SpiderClient/bin/workload/workload_content/biyi/biyicontent_20140502.txt','r')
content = fileHandle.read()
hotel_list = content.split('\n')

c = 0
for each_hotel in hotel_list[4700:-1]:
    c += 1
    if c % 10 == 0:
        time.sleep(2)

    for i in range(3):
        para = biyiHotelParser.biyi_hotel_parser(each_hotel)
        stime = time.time()
        update_time = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
        #logger.info ('start a new task @ %s'%str(update_time))

        if para == None or para == ():
            #logger.error ('task failed with %s for %sth time'%(content,i))
            #time.sleep(random.randint(2,10))
            time.sleep(1)
            continue
        else:
            try:
                if para != ():
                    para_list = []
                    para_list.append(para)
                    InsertHotel(para_list)
                etime = time.time()
                dur = int((etime - stime) * 1000)
                logger.info('wangfang=' + para[3])
                #logger.info("task %s finish using %d ms"%(content, dur))
                #time.sleep(random.randint(2,10))
                #time.sleep(1)
                break

            except Exception,e:
                logger.error('Insertation Error: %s'%str(e))
                continue
    
