#! /usr/bin/env python
#encoding=UTF8

'''
    @author:fangwang
    @date:2014-05-07
    @desc:抓取booking酒店价格信息
'''

import re
import datetime
import time
import sys
from common.logger import logger
from common.class_common import Room
from util.crawl_func import crawl_single_page
from common.common import get_proxy, invalid_proxy

CONTENT_LEN = 3000

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

#pattern
city_name_pat = re.compile(r"city_name: '(.*?)',", re.S|re.M)
hotel_name_pat = re.compile(r'id="hp_hotel_name">(.*?)<span>(.*?)</span></span>', re.S|re.M)
each_room_type_pat = re.compile('maintr"><td class="roomType"(.*?)<hr class="clearBoth', re.S|re.M)
room_id_pat = re.compile(r'data-block-addons=\'{"id":"(.*?)",', re.S|re.M)
occupancy_pat = re.compile(r'"(.*?)"class="room_loop_counter', re.S|re.M)
each_room_pat = re.compile(r'data-occupancy=(.*?)</td></tr>', re.S|re.M)
price_pat = re.compile(r'data-price-without-addons="RMB (.*?)"data-price', re.M|re.S)
room_type_pat = re.compile(r'<i class="b-sprite icon_shut"></i>(.*?)</a>', re.S|re.M)
room_type_pat = re.compile(r'class="jqrt togglelink" title="">(.*?)</a><span', re.S|re.M)
room_desc_temp_pat = re.compile(r'</p> --><p>(.*)</div>', re.S|re.M)
room_size_pat = re.compile(r'客房面积(.*?) 平方米')
bed_type_pat = re.compile(r'床铺尺寸：(.*?)')

def booking_room_task_parser(taskcontent):

    result = {}
    result['para'] = None
    result['error'] = 0

    try:
        hotel_id,url_hotel_name,check_in_temp = taskcontent.strip().split('&')[0], \
                taskcontent.strip().split('&')[1], taskcontent.strip().split('&')[2]

        check_in = check_in_temp[:4] + '-' + check_in_temp[4:6] + '-' + check_in_temp[6:]
        check_out_temp = datetime.datetime(int(check_in_temp[:4]), int(check_in_temp[4:6]), int(check_in_temp[6:]))
        check_out = str(check_out_temp + datetime.timedelta(days=1))[:10]

    except Exception,e:
        logger.error('bookingHotel: Wrong Content Format with %s'%taskcontent)
        result['error'] = TASK_ERROR
        return result

    hotel_url = get_hotel_url(url_hotel_name,check_in,check_out)

    p = get_proxy(source='bookingHotel')
    if p == None:
        result['error'] = PROXY_NONE
        return result

    page = crawl_single_page(hotel_url, proxy = p)
    if page == None or page == '':
        invalid_proxy(proxy=p, source='bookingHotel')
        result['error'] = PROXY_INVALID
        return result
    
    if len(page) > CONTENT_LEN:
        room_info = parseRoom(page, check_in, check_out, hotel_id)
    else:
        result['error'] = UNKNOWN_TYPE
        return result
    
    if room_info != []:
        result['para'] = room_info
        return result
    else:
        result['error'] = DATA_NONE

    return result

def booking_room_request_parser(content):

    result = -1

    return result

def parseRoom(content, check_in, check_out, hotel_id):
    room_info = []
    room = Room()
    content = content.replace('\n', '')
    content = replace_char(content)
    if content == '' or len(content) < CONTENT_LEN:
        return room_info

    try:
        each_type_room_list = each_room_type_pat.findall(content)
        if len(each_type_room_list) == 0:
            return room_info
    except Exception,e:
        return room_info

    try:
        hotel_name = hotel_name_pat.findall(content)[0][1][1:-1]
        city = city_name_pat.findall(content)[0]
    except Exception, e:
        #logger.info('Cannot parse city and hotel name with error: ' + str(e))
        return room_info

    try:
        if '加床  的收费' in content or '一间客房增加' in content:
            room.is_extrabed = 'Yes'

        if '免费加床' in content or '加床免费' in content:
            room.is_extrabed_free = 'Yes'
    except Exception, e:
        #logger.info('Cannot parse extrabed info with error: ' + str(e))
        pass


    for each_type_room in each_type_room_list:
        try:
            try:
                room.room_type = room_type_pat.findall(each_type_room)[0]
                room.room_type = re.sub(r'<.*?>','',room.room_type)
                room.room_type = re.sub(r'\（.*?\）','',room.room_type)
            except Exception, e:
                #logger.info('Cannot parse this hotel type with error: ' + str(e))
                pass

            try:
                room_desc_temp = room_desc_temp_pat.findall(each_type_room)[0]
                room_desc = re.sub(r'<.*?>', '', room_desc_temp)
            except Exception, e:
                #logger.info('Cannot parse room desc with error:: ' + str(e))
                pass

            try:
                room.size = room_size_pat.findall(room_desc)[0]
            except Exception, e:
                #logger.info('Cannot parse room size with error: ' + str(e))
                pass

            try:
                num1 = room_desc.find('床铺尺寸：')
                num1_temp = room_desc.rfind('床')
                if num1 > 0 and num1_temp > 0:
                    room.bed_type = room_desc[num1+15:num1_temp + 3]
            except Exception, e:
                #logger.info('Cannot parse room bed type with error: ' + str(e))
                pass

            num2 = room_desc.find('客房面积')
            if num2 > 0:
                room.room_desc = room_desc[:num2]
            else:
                room.room_desc = room_desc

        except Exception, e:
            #logger.info('Cannot parse this type room with error: ' + str(e))
            continue

        each_room_list = each_room_pat.findall(each_type_room)
        if len(each_room_list) == 0:
            continue

        for each_room_content in each_room_list:
            try:
                try:
                    room.occupancy = occupancy_pat.findall(each_room_content)[0]
                except Exception, e:
                    #logger.info('Cannot parse occupancy info with error: ' + str(e))
                    pass

                try:
                    if '免费取消' in each_room_content:
                        room.is_cancel_free = 'Yes'
                except Exception, e:
                    #logger.info('Cannot parse is_cancel free info with error: ' + str(e))
                    source

                try:
                    if '包括早餐' in each_room_content:
                        room.has_breakfast = 'Yes'
                        room.is_breakfast_free = 'Yes'
                    elif '早餐的收费' in each_room_content:
                        room.has_breakfast = 'Yes'
                        room.is_breakfast_free = 'No'
                except Exception, e:
                    #logger.info('Cannot parse breakfast info with error :' + str(e))
                    pass

                try:
                    room.source_roomid = room_id_pat.findall(each_room_content)[0]
                except Exception, e:
                    #logger.info('Cannot parse this room id with error: ' + str(e))
                    pass

                try:
                    room.price = price_pat.findall(each_room_content)[0].replace(',','')
                except Exception, e:
                    #logger.info('Cannot parse price of this room with error: ' + str(e))
                    pass

                room.currency = 'CNY'
                room.source = 'booking'
                room.real_source = 'booking'
                room.hotel_name = hotel_name
                room.city = city
                room.check_in = check_in
                room.check_out = check_out
                room.source_hotelid = hotel_id

                room_tuple = (room.hotel_name, room.city, room.source, room.source_hotelid, room.source_roomid, \
                    room.real_source, room.room_type, room.occupancy, room.bed_type, room.size, room.floor, \
                    room.check_in, room.check_out, room.price, room.tax, room.currency, room.is_extrabed, \
                    room.is_extrabed_free, room.has_breakfast, room.is_breakfast_free, \
                    room.is_cancel_free, room.room_desc)
                room_info.append(room_tuple)

            except Exception, e:
                #logger.info('Cannot parse this room with error: ' + str(e))
                continue

    return room_info


def get_hotel_url(url_hotel_name,check_in,check_out):
    hotel_url = 'http://www.booking.com/' + url_hotel_name + '.zh-cn.html?checkin=' + check_in + \
            ';checkout=' + check_out + ';selected_currency=CNY'
    
    return hotel_url

def replace_char(content):
    content = content.replace('&amp','').replace('&#39;',"'").replace('&#47;','/')

    return content


if __name__ == '__main__':

    taskcontent = '54190&hotel/fr/regyn-s-montmartre&20140602'
    result1 = booking_room_task_parser(taskcontent)
    print str(result1)

    content = ''
    result2 = booking_room_request_parser(content)
    print str(result2)
