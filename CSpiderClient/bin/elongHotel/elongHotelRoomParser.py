#! /usr/bin/env python
#coding=UTF8

'''
    @author:fangwang
    @data:2014-05-11
    @desc:crawl and parse elong hotel comment
'''

import json
import sys
from util.crawl_func import crawl_single_page
from util.crawl_func import request_post_data
from common.insert_db import InsertHotel_room
from common.class_common import Room
from common.common import get_proxy, invalid_proxy
from common.logger import logger
import time
import datetime
import re

reload(sys)
sys.setdefaultencoding('utf8')

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

request_url = 'http://globalhotel.elong.com/isajax/GlobalHotelNewDetail/GetHotelRoomInfo'

def elong_room_task_parser(taskcontent):
    room_list = []

    result = {}
    result['para'] = None
    result['error'] = 0

    try:
        taskcontent = taskcontent.strip()
        city_name_zh,hotel_id,hotel_name,country_name,city_id,city_name_temp,check_in_temp = \
                taskcontent.split('&&')[0], taskcontent.split('&&')[1], \
                taskcontent.split('&&')[2], taskcontent.split('&&')[3], \
                taskcontent.split('&&')[4], taskcontent.split('&&')[5], \
                taskcontent.split('&&')[6]

        check_in = check_in_temp[:4] + '-' + check_in_temp[4:6] + '-' + check_in_temp[6:]
        check_out_temp = datetime.datetime(int(check_in_temp[:4]), int(check_in_temp[4:6]), int(check_in_temp[6:]))
        check_out = str(check_out_temp + datetime.timedelta(days=1))[:10]
        hotel_id_temp = hotel_id.split('_')[1]

    except Exception, e:
        logger.error('elongHotelParser: Wrong Content Format with %s'%taskcontent)
        result['error'] = TASK_ERROR
        return result
        
    if hotel_id_temp == '0':
        result['error'] = TASK_ERROR
        return result

    p = get_proxy(source='elongHotel')
    if p == None:
        result['error'] = PROXY_NONE
        return result

    post_data = get_post_data(hotel_id_temp, check_in, check_out)

    page = request_post_data(request_url,data=post_data,proxy=p)
    if page == None or page == '':
        invalid_proxy(proxy=p, source='elongHotel')
        result['error'] = PROXY_INVALID
        return result

    room_list = parseRoom(page,hotel_name,city_name_zh,check_in,check_out,hotel_id)

    if room_list != []:
        result['para'] = room_list
        return result
    else:
        result['error'] = DATA_NONE

    return result

def elong_room_request_parser(content):

    result = -1

    return result
    

def parseRoom(content,hotel_name,city_name_zh,check_in,check_out,hotel_id):
    room_list = []
    if content == '' or len(content) < 100:
        return room_list

    try:
        content_json = json.loads(content)['value']['hotelRoomList']
    except Exception, e:
        logger.info('elongHotelParser: Cannot load json' + str(e))
        return room_list
    
    for each_hotel in content_json:
        room = Room()

        try:
            room_type = str(each_hotel['RoomName'])
            num_temp1 = room_type.find(',')
            if num_temp1 > 0:
                room.room_type = room_type[:num_temp1]
            else:
                room.room_type = room_type
        except Exception,e:
            logger.error('Cannot paese room type of this hotel!' + str(e))

        try:
            room.source_roomid = each_hotel['RoomId']
        except Exception, e:
            logger.info('Cannot parse this room id with error: ' + str(e))

        try:
            room_desc = ''
            if each_hotel['rp'] != 'none':
                room_desc += each_hotel['rp']
            if each_hotel['roomStaticDescription'] != '':
                room_desc += each_hotel['roomStaticDescription']
            room.room_desc = re.sub('<.*?>','', room_desc)
        except Exception, e:
            logger.info('Cannot parse this room description with error: ' + str(e))

        try:
            if '可以免费取消' in each_hotel['cancellationPolicyNew'] or '可以免费取消' \
                in each_hotel['cancellationPolicy']:
                room.is_cancel_free = 'Yes'
        except Exception,e:
            logger.info('Cannot parse cancel info with error: ' + str(e))

        try:
            bed_type = each_hotel['bedTypes'][0]['description']
            room.bed_type = str(bed_type)
        except Exception, e:
            logger.info('Cannot parse bed type of this room with error: ' + str(e))

        try:
            size_num_temp = room.room_desc.find('平方米')
            if size_num_temp > 0:
                size_content = room.room_desc[:size_num_temp]
                size_num_temp2 = size_content.rfind('（')
                if size_num_temp2 > 0:
                    room_size = size_content[size_num_temp2 + 1:]
                    room.size = room_size.strip().replace(' ','')
        except Exception, e:
            logger.info('Cannot parse size of this room with error: ' + str(e))

        except Exception,e:
            logger.info('Cannot parse room size info with error: ' + str(e))

        try:
            if '不含早餐' not in room.room_desc and '早餐' in room.room_desc:
                room.has_breakfast = 'Yes'
            if '免费' in room.room_desc and '早餐' in room.room_desc:
                room.is_breakfast_free = 'Yes'
        except Exception,e:
            logger.info('Cannot parse breakfast info with error: ' + str(e))

        try:
            if '加床' in room.room_desc:
                room.is_extrabed = 'Yes'
            if '免费加床' in room.room_desc or '加床免费' in room.room_desc:
                room.is_extrabed_free = 'Yes'
        except Exception, e:
            logger.info('Cannor parse extrabed info with error: ' + str(e))

        try:
            try:
                total_price = each_hotel['chargeableRoomRateTotal']
                tax_price = each_hotel['chargeableRoomRateTaxesAndFees']
                room.tax = float(str(tax_price))
                room.price = float(str(total_price)) - room.tax
            except:
                total_price = each_hotel['chargeableRoomRateTotal']
                room.price = float(str(total_price))
                room.tax = 0
        except Exception,e:
            logger.error('Cannot parse this room\'s price with error:' + str(e))
            continue

        try:
            if '三人' in room.room_type or '3' in room.bed_type:
                room.occupancy = 3
            elif '四人' in room.room_type or '4' in room.bed_type:
                room.occupancy = 4
            else:
                room.occupancy = 2
        except:
            room.occupancy = 2

        room.hotel_name = hotel_name
        room.city = city_name_zh
        room.check_in = check_in
        room.check_out = check_out
        room.source = 'elong'
        room.source_hotelid = hotel_id
        room.currency = 'CNY'
        room.real_source = 'elong'

        room_tuple = (room.hotel_name,room.city,room.source,room.source_hotelid,room.source_roomid, \
            room.real_source,room.room_type,room.occupancy,room.bed_type,room.size,room.floor, \
            room.check_in,room.check_out,room.price,room.tax,room.currency,room.is_extrabed, \
            room.is_extrabed_free,room.has_breakfast,room.is_breakfast_free, \
            room.is_cancel_free,room.room_desc)
        room_list.append(room_tuple)

    return room_list


def get_post_data(hotel_id,check_in,check_out):
    post_data = {
            'hotelid':hotel_id,
            'indate':check_in,
            'outdate':check_out,
            'RoomNum':'1',
            'AdultNum':'2',
            'ChildNum':'0',
            'couponcode':'coupon',
            'GlobalHotelid':hotel_id,
            'viewpath':'~/views/channel/Detail.aspx',
            }

    return post_data


def data_writer(room_list,taskcontent):
    if room_list == []:
        logger.error('room_list.size == 0')
        return
    try:
        InsertHotel_room(room_list)
        logger.info(taskcontent + ' [success]')
        logger.info('with ' + str(len(room_list)) + ' values!')
    except Exception, e:
        logger.info(taskcontent + ' [failed]')
        logger.info(str(e))


def get_orig_data(fout):
    content = fout.read()
    content_list = content.split('\n')
    del content_list[-1]

    return content_list


if __name__ == '__main__':

    taskcontent = '巴黎&&196618_323263&&巴黎东圣穆尔凯富酒店&&法国&&179898&&paris(andvicinity)&&20140602'
    result1 = elong_room_task_parser(taskcontent)
    print str(result1)

    content = ''

    result2 = elong_room_request_parser(content)
    print str(result2)

