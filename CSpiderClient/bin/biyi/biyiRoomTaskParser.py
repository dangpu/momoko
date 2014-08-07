#! /usr/bin/env python
#coding=UTF8

'''
    @author:fangwang
    @date:2014-04-21
    @desc:crawl and parse biyi room data
'''

import re
import json
import time
import sys
#sys.path.append('/home/workspace/spider/SpiderClient/bin/common/')
import datetime
import random
from common.logger import logger
#from common import get_proxy, invalid_proxy
from common.class_common import Hotel
from common.class_common import Room
from util.multi_times_crawler import with_cookie_crawler
from common.common import get_proxy
reload(sys)
sys.setdefaultencoding('utf-8')

all_room_info_pat = re.compile(r'<tbody>(.*?)</tbody>', re.S)
each_room_info_pat = re.compile(r'<tr class="(.*?)</tr>', re.S)
real_source_pat = re.compile(r'data-providername="(.*?)">', re.S)
price_pat = re.compile(r'class="hc_pr_syb">CN¥</span>(.*?)</a>', re.S)
other_info_pat = re.compile(r'<span class="hc_htl_pmi_deal">(.*?)</span>', re.S)
room_type_info_pat = re.compile(r'id="RoomLink" target="_blank">(.*?)</a>', re.S)
room_desc_pat = re.compile(r'id="RoomLink" target="_blank">(.*?)</a>', re.S|re.M)

def biyi_room_task_parser(taskcontent):
    taskcontent = taskcontent.encode('utf-8')
    try:
        hotel_id = taskcontent.strip().split('&')[0]
        hotel_name = taskcontent.strip().split('&')[1]
        map_info = taskcontent.strip().split('&')[2]
        city_name_zh = taskcontent.strip().split('&')[3]
        city_name_en = taskcontent.strip().split('&')[4]
        country_name_zh = taskcontent.strip().split('&')[5]
        check_in_day_temp = taskcontent.strip().split('&')[6]
    except Exception, e:
        logger.error('Can not parse taskcontent!')
        return []

    check_in_day = check_in_day_temp[:4] + '-' + check_in_day_temp[4:6] + '-' + \
            check_in_day_temp[6:]

    check_out_day_temp = datetime.datetime(int(check_in_day_temp[:4]),int(check_in_day_temp[4:6]), \
            int(check_in_day_temp[6:]))
    check_out_day = str(check_out_day_temp  + datetime.timedelta(days = 1))[:10] 
    
    first_url = 'http://www.biyi.cn/'
    url = get_url(hotel_name, city_name_en, check_in_day, check_out_day)

    content = ''
    i = 0
    while i < 2 and len(content) < 3000:
        p = get_proxy()
        i += 1
        content = with_cookie_crawler(first_url=first_url, second_url=url, proxy=p, min_page_len = 3000)
        if len(content) > 3000:
            break
            
    if content != '' and len(content) > 2000:
        room_lists = parseRoom(content,hotel_id,hotel_name,city_name_zh,check_in_day,check_out_day)
    else:
        logger.info('Get room content failed!')
        return []

    return room_lists


def get_url(hotel_name, city, check_in_day,check_out_day):
    rt =random.random()
    url = 'http://www.biyi.cn/SearchedHotelRates.aspx?languageCode=CS&currencyCode=CNY&fileName=' + \
            hotel_name + '&destination=place:' + city + '&radius=0km&checkin=' + check_in_day + \
            '&checkout=' + check_out_day + '&Rooms=1&adults_1=2&r=' + str(rt)

    return url


def parseRoom(content,hotel_id,hotel_name,city,check_in,check_out):
    rooms = []
    try:
        all_info = all_room_info_pat.findall(content)[0]
        each_room_info_list = each_room_info_pat.findall(all_info)
        print len(each_room_info_list)
        time.sleep(3)
    except Exception, e:
        logger.error('Can not parse rooms info!' + str(e))
        return rooms

    for each_room_info in each_room_info_list:
        room = Room()
        room.hotel_name = hotel_name.replace('_',' ')
        room.city = city
        room.source_hotelid = hotel_id
        room.currency = 'CNY'
        room.source = 'biyi'
        room.check_in = check_in
        room.check_out = check_out
        
        try:
            room.real_source = real_source_pat.findall(each_room_info)[0]
            room.price = price_pat.findall(each_room_info)[0].replace(' ','').replace(',','')
        except Exception, e:
            logger.error('Can not parse important info of this room! Detail: ' + str(e))
            return rooms
        
        other_info = ''
        try:
            other_info = other_info_pat.findall(each_room_info)[0]
            if '免费取消' in other_info:
                room.is_cancel_free = 'Yes'
            else:
                room.is_cancel_free = 'No'
        except:
            room.is_cancel_free = 'No'

        try:
            room_desc_temp = room_desc_pat.findall(each_room_info)[0]
            room_desc = fan_to_jian(room_desc_temp)
            #room_desc = room.desc.encode('utf-8'
            #room_desc = room_desc_temp
            room.room_desc = room_desc

            if '含早餐' in other_info or 'Breakfast' in room_desc:
                room.has_breakfast = 'Yes'
                room.is_breakfast_free = 'Yes'
            else:
                logger.info('Cannot parse breakfast info!')
                room.has_breakfast = 'No'
                room.is_breakfast_free = 'No'
            
            type_num01 = room_desc.find('(')
            type_num02 = room_desc.find('Room')
            if type_num01 > 0:
                room.room_type = room_desc[:type_num01]
            elif type_num02 > 0:
                room.room_type = room_desc[:type_num02 + 4]
            else:
                logger.info('Cannot parse room type info!')
                room.room_type = room_desc

            if '单人床' in room_desc:
                room.bed_type = '单人床'
            elif '双人床' in room_desc:
                room.bed_type = '双人床'
            elif '大床' in room_desc:
                room.bed_type = '大床'
            else:
                room.bed_type = 'NULL'

            if '双人' in room_desc or 'Double' in room_desc or '双床' in room_desc:
                room.occupancy = 2
            elif '三人' in room_desc or 'Three' in room_desc:
                room.occupancy = 3
            elif '四人' in room_desc or 'Four' in room_desc:
                room.occupancy = 4
            else:
                room.occupancy = 2

            if '加床' in room_desc or 'extra' in room_desc:
                room.is_extrabed = 'Yes'
                room.is_extrabed_free = 'Yes'
            else:
                room.is_extrabed = 'No'
                room.is_extrabed_free = 'No'

        except:
            logger.info('Cannot parse room description info!')
            continue
         
        room_tuple = (room.hotel_name, room.city, room.source, room.source_hotelid, room.source_roomid, \
                room.real_source, room.room_type, room.occupancy, room.bed_type, room.size, room.floor, \
                room.check_in, room.check_out, room.price, room.tax, room.currency, room.is_extrabed, \
                room.is_extrabed_free, room.has_breakfast, room.is_breakfast_free, room.is_cancel_free, \
                room.room_desc)
        rooms.append(room_tuple)

    return rooms

            
if __name__ == '__main__':
    fileHandle = open('/home/workspace/spider/SpiderClient/bin/workload/workload_content/biyi/biyicontent_20140502.txt','r')
    content = fileHandle.read()
    task_list = content.split('\n')
    for taskcontent in task_list[44:45]:
        taskcontent = '1074146&Palace_Bonvecchiati_Hotel_Venice&12.336316,45.435503&威尼斯&Venice&意大利&20140501'
        print biyi_room_parser(taskcontent)
