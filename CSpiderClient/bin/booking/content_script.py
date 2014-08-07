#! /usr/bin/env python
#coding=UTF8

'''
    @author:fangwang
    @date:2014-05-06
    @desc:生成 booking workload
'''

import sys
#sys.path.append('/home/workspace/wangfang/SpiderClient/lib/')
#sys.path.append('/home/workspace/wangfang/SpiderClient/bin/')
import time
import datetime
from common.logger import logger

if len(sys.argv) != 2:
    logger.error('Usage: python content_script.py check_in_day')
    sys.exit()
else:
    pass


def get_orig_data():
    fileHandle = open('hotel.txt','r')
    content = fileHandle.read()
    content_list = content.split('\n')
    del content_list[-1]

    return content_list


check_in_day = sys.argv[1]
check_in_temp = datetime.datetime(int(check_in_day[:4]), int(check_in_day[4:6]), \
        int(check_in_day[6:]))
#crawl_day = str(check_in_temp + datetime.timedelta(days=1))[:10].replace('-','')
fout = open('bookingcontent_' + check_in_day + '.txt','a+')

hotel_list = get_orig_data()

for each_hotel_temp in hotel_list:
    each_hotel = each_hotel_temp.split('&')
    fout.write(each_hotel[0] + '&' + each_hotel[1] + '&' +  check_in_day + '\n')
fout.close()
