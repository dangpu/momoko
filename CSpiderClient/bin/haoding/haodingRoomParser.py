#! /usr/bin/env python
#coding=UTF8

'''
    @author:fangwang
    @date:2014-05-24
    @desc: hotels.cn parser
'''

import sys
#sys.path.append('/home/workspace/wangfang/SpiderClient/bin/')
#sys.path.append('/home/workspace/wangfang/SpiderClient/lib/')
import time
import datetime
import re
from common.logger import logger 
from common.class_common import Room
from util.crawl_func import crawl_single_page
from common.common import get_proxy,invalid_proxy
import urllib
import urllib2
from common.insert_db import InsertHotel_room

reload(sys)
sys.setdefaultencoding('utf-8')
#pattern
rooms_content_pat = re.compile('<div id="rooms" class="rooms dateful tab description">(.*?)<div class="details tab description ">', \
        re.S|re.M)
each_type_room_content_pat = re.compile(r'<tbody id="room(.*?)</tbody>', re.S|re.M)
hotel_name_info_pat = re.compile(r'<div class="vcard item">(.*?)<div id="marketingChannelCode"', re.S|re.M)
hotel_name_pat = re.compile(r'<h1 class="fn org">(.*?)</h1>', re.S|re.M)
room_desc_pat = re.compile(r'<tr class="room-information-container(.*?)</tr>', re.S|re.M)
bed_type_pat = re.compile(r'<h5>床型选择</h5>(.*?)</div>', re.S|re.M)
room_type_pat = re.compile(r'<td class="room-type"(.*?)</h3>', re.S|re.M)
occupancy_temp_content_temp = re.compile(r'<td class="rate-occupancy">(.*?)</td>', re.S|re.M)
occupancy_num_pat = re.compile(r'<span class="text">最多(.*?)人入住</span>', re.S|re.M)
each_room_content_pat = re.compile(r'<tr class="rate(.*?)</td>\n</tr>', re.S|re.M)
price_temp_pat = re.compile(r'<span class="current-price">(.*?)</strong>', re.S|re.M)
is_cancel_content_pat = re.compile(r'<strong class="free-cancellation-text(.*?)</strong>', re.S|re.M)
wifi_content_pat = re.compile(r'<li class="wifi(.*?)</span>', re.S|re.M)
breakfast_content_pat = re.compile(r'<li class="breakfast(.*?)</span>', re.S|re.M)
star_temp_pat = re.compile(r'<div class="star-rating">(.*?)</div>', re.S|re.M)
star_pat = re.compile(r'title="(.*?) 星级">', re.S|re.M)
hotel_name_info_pat = re.compile(r'<div class="vcard item">(.*?)<div id="marketingChannelCode"', re.S|re.M)
room_id_pat = re.compile(r'<input name="rateCode" type="hidden" value="(.*?)" />', re.S|re.M)

CONTENT_LEN = 3000
TASK_ERROR = 12
NO_PROXY = 21
NO_CONTENT = 22
NO_INFO = 23
NO_RESULT = 24

hotel_dict = {
        '哥本哈根':0.25, '布达佩斯':[0.18, 0.22], '卢森堡':0.03, '维也纳':0.1, '萨尔茨堡':0.1, \
                '因斯布鲁克':0.1, '慕尼黑':0.07, '柏林':0.07, '法兰克福':0.07, '科隆':0.07, \
                '海德堡':0.07, '汉堡':0.07, '杜塞尔多夫':0.07, '斯图加特':0.07, '波恩':0.07, \
                '纽伦堡':0.07, '汉诺威':0.07, '不来梅':0.07, '亚琛':0, '莱比锡':0.07, '班贝格':0.07, \
                '曼海姆':0.07, '奥格斯堡':0, '罗马':0.1, '威尼斯':0.1, '佛罗伦萨':0.1, '米兰':0.1, \
                '比萨':0.1, '维罗纳':0.1, '那不勒斯':0.1, '热那亚':0.1, '博洛尼亚':0.1, '都灵':0, \
                '奥斯陆':0.08, '卑尔根':0.08, '布拉格':0.15, '卡罗维发利':0.15, '布鲁塞尔':0.06, \
                '安特卫普':0.06, '根特':0.06, '尼斯':0.1, '巴黎':0.1, '马赛':0.1, '里昂':0.1, \
                '斯特拉斯堡':0.1, '波尔多':0.1, '尼姆':0.1, '华沙':0.08, '斯德哥尔摩':0.12, \
                '哥德堡':0.12, '马尔默':0.12, '苏黎世':0.03, '日内瓦':0.038, '伯尔尼':0.038, \
                '巴塞尔':0.038, '卢加诺':0, '赫尔辛基':0.1, '伦敦':0.2, '爱丁堡':0.2, '牛津':0.2, \
                '曼彻斯特':0.2, '伯明翰':0.2, '格拉斯哥':0.2, '利物浦':0.2, '利兹':0.2, \
                '布里斯托尔':0.2, '诺丁汉':0.2, '纽卡斯尔':0, '贝尔法斯特':0.2, '谢菲尔德':0.2, \
                '阿姆斯特丹':0.06, '鹿特丹':0.06, '里斯本':0.06, '波尔图':0.06, '巴塞罗那':0.1, \
                '马德里':0.1, '塞维利亚':0.1, '格拉纳达':0.1, '瓦伦西亚':0.1, '马拉加':0.1}


def haoding_room_task_parser(taskcontent_temp):
    taskcontent = taskcontent_temp.encode('utf8')
    try:
        city_name_zh,country_name_zh,city_id,hotel_id,check_in_temp = \
                taskcontent.split('&&')[0], taskcontent.split('&&')[1], \
                taskcontent.split('&&')[2], taskcontent.split('&&')[3], \
                taskcontent.split('&&')[4]
    except Exception, e:
        logger.error('haodingHotel::Cannot parse task content with error: ' + str(e))
        return {'para':[], 'error':TASK_ERROR}

    check_in = check_in_temp[:4] + '-' + check_in_temp[4:6] + '-' + check_in_temp[6:]
    check_out_temp = datetime.datetime(int(check_in_temp[:4]), int(check_in_temp[4:6]), \
            int(check_in_temp[6:]))
    check_out = str(check_out_temp + datetime.timedelta(days=1))[:10]

    hotel_url = get_hotel_url(city_name_zh,city_id,hotel_id,check_in,check_out)
    
    #p = get_proxy()
    #print p
    p = get_proxy(source='haodingHotel')
    if p == '' or p == None:
        return {'para':[], 'error':NO_PROXY}
    
    i = 0
    content_len = 0
    while i < 3 and content_len < CONTENT_LEN:
        i += 1
        content = crawl_single_page(hotel_url, proxy = p)
        content_len = len(content)

    if content == '' or content == None:
        invalid_proxy(proxy = p, source='haodingHotel')
        return {'para':[], 'error':NO_CONTENT}

    if len(content) < CONTENT_LEN:
        return {'para':[], 'error':NO_INFO}

    room_list = parseRoom(content,city_name_zh,country_name_zh,hotel_id,check_in,check_out)

    if room_list == [] or room_list == None:
        return {'para':[], 'error':NO_RESULT}

    return {'para':room_list, 'error':0}


def haoding_room_request_parser(content):

    result = -1

    return result


def parseRoom(content,city_name_zh,country_name_zh,hotel_id,check_in,check_out):
    room_list = []

    try:
        rooms_content = rooms_content_pat.findall(content)[0]
        if len(rooms_content) == 0:
            return room_list
    except Exception, e:
        logger.error('haodingHotel::Cannot parse rooms of this hotel [' + hotel_id + ']')
        logger.error('haodingHotel::' + str(e))
        return room_list

    try:
        hotel_name_info_content = hotel_name_info_pat.findall(content)[0]
        
        hotel_name_temp = hotel_name_pat.findall(hotel_name_info_content)[0]
        hotel_name = hotel_name_temp.strip()
        hotel_name_num = hotel_name.find('(')
        if hotel_name_num > 0:
            hotel_name_real = hotel_name[:hotel_name_num]
            hotel_name_en = hotel_name[hotel_name_num+1:-1]
        else:
            hotel_name_real = hotel_name_en = hotel_name
    except:
        #logger.error('haodingHotel::Cannot parse hotel name')
        return room_list

    try:
        room_type_list = each_type_room_content_pat.findall(rooms_content)
        if len(room_type_list) == 0:
            return room_list
    except Exceprion, e:
        #logger.error('haodingHotel::Cannot parse rooms of this hotel [' + hotel_id + ']')
        logger.error('haodingHotel::' + str(e))
        return room_list

    for each_type_room_content in room_type_list:
        room = Room()

        room.hotel_name = hotel_name_real
        room.city = city_name_zh
        room.source = 'hotels'
        room.source_hotelid = hotel_id
        room.real_source = 'hotels'
        room.currency = 'CNY'
        room.check_in = check_in
        room.check_out = check_out

        try:
            room_desc_temp = room_desc_pat.findall(each_type_room_content)[0].strip()
            room_desc_temp = '<' + room_desc_temp
            room.room_desc = re.sub('<.*?>','',room_desc_temp).replace('\n','').replace(' ',',')
            room.room_desc = room.room_desc.replace(',,','').replace(' ','').replace('。,','。')
        except Exception, e:
            #logger.info('haodingHotel::Cannot parse room desc of this type room')
            #logger.info('haodingHotel::' + str(e))
            pass

        #print room.room_desc
        try:
            room_type_temp = room_type_pat.findall(each_type_room_content)[0]
            bed_type_temp = bed_type_pat.findall(each_type_room_content)[0]
            room_type_temp = '<' + room_type_temp
            room_type = re.sub('<.*?.>','',room_type_temp).strip()
            bed_type = re.sub('<.*?>','',bed_type_temp).strip()
            #print bed_type
            #if '加床' in bed_type:
            #    room.is_extrabed = 'Yes'
            if '加床' in bed_type:# and '免费' in bed_type:
                room.is_extrabed = 'Yes'
                room.is_extrabed_free = 'Yes'
            room.room_type = room_type.split('\n')[0]
            if '(' in room.room_type:
                room_num = room.room_type.find('(')
                room.room_type = room.room_type[:room_num]
            room.bed_type = bed_type.split('\n')[0]
        except:
            #logger.info('haodingHotel::Cannot parse room_type, bed_type !')
            #logger.info('haodingHotel::' + str(e))
            pass
            
        #print  room.room_type,room.bed_type
        try:
            room_content_list = each_room_content_pat.findall(each_type_room_content)
            if len(room_content_list) == 0:
                continue
        except Exception, e:
            #logger.info('haodingHotel::Parse this room failed with error: ' + str(e))
            continue

        for each_room_content in room_content_list:
            try:
                price_content_temp = price_temp_pat.findall(each_room_content)[0]
                price_content = re.sub('<.*?>','',price_content_temp).strip()
                price = price_content.replace('￥','').replace(',','')
                room.price = int(price)
                cancel_content_temp = is_cancel_content_pat.findall(each_room_content)[0]
                cancel_content_temp = '<' + cancel_content_temp
                cancel_content = re.sub('<.*?>','',cancel_content_temp).strip()
                if '免费取消' in cancel_content:
                    room.is_cancel_free = 'Yes'
             
                breakfast_content_temp = breakfast_content_pat.findall(each_room_content)[0]
                breakfast_content_temp = '<' + breakfast_content_temp
                breakfast_content = re.sub('<.*?>','',breakfast_content_temp).strip()
                if '早餐' in breakfast_content:
                    room.has_breakfast = 'Yes'
                if '免费' in breakfast_content and '早餐' in breakfast_content:
                    room.has_breakfast = 'Yes'
                    room.is_breakfast_free = 'Yes'
                #print room.price, room.is_cancel_free,room.is_breakfast_free
                try:
                    #print each_room_content
                    room_id = room_id_pat.findall(each_room_content)[0]
                    room.source_roomid = room_id
                except Exception, e:
                    pass
                    #logger.info('haodingHotel::Cannot parse id of this room!')
                    #logger.info('haodingHotel::' + str(e))
                #print room.source_roomid  
                try:
                    room.occupancy = occupancy_num_pat.findall(each_room_content)[0]
                except:
                    room.occupancy = 2

                try:
                    if city_name_zh == '布达佩斯':
                        hotel_name_info_temp = hotel_name_info_pat.findall(content)[0]
                        hotel_star_temp = hotel_star_pat.findall(hotel_name_info_temp)[0]
                        hotel_star = int(hotel_star_temp)
                        if hotel_star == 5:
                            room.tax = int(room.price * 0.22)
                        else:
                            room.tax = int(room.price * 0.18)
                    else:
                        tax_per = hotel_dict[city_name_zh]
                        room.tax = int(room.price * tax_per)
                except:
                    #logger.info('haodingHotel::Parse room tax failed!')
                    continue
                        
                room_tuple = (room.hotel_name, room.city, room.source, room.source_hotelid, room.source_roomid, \
                        room.real_source, room.room_type, room.occupancy, room.bed_type, room.size, room.floor, \
                        room.check_in, room.check_out, room.price, room.tax, room.currency, room.is_extrabed, \
                        room.is_extrabed_free, room.has_breakfast, room.is_breakfast_free, room.is_cancel_free, \
                        room.room_desc)
                #print room_tuple
                room_list.append(room_tuple)
            except Exception, e:
                logger.info('haodingHotel::Parse this room failed with error: ' + str(e))
                continue

    return room_list
    

def get_hotel_url(city_name_zh,city_id,hotel_id,check_in,check_out):
    city_name = urllib2.quote(city_name_zh)
    hotel_url = 'http://www.hotels.cn/hotel/details.html?&tab=description&destinationId=' + city_id + \
            '&searchDestination=' + city_name + '&hotelId=' + hotel_id + '&arrivalDate=' + check_in + \
            '&departureDate=' + check_out 

    return hotel_url


def data_writer(room_list, taskcontent):
    if room_list == None or room_list == []:
        logger.error('No hotel parsed')
        return 
    try:
        InsertHotel_room(room_list)
        logger.info('Insert hotel [success] ' + taskcontent)
    except Exception, e:
        logger.error('Insert hotel [failed] ' + taskcontent)
        return 
    return 




if __name__ == '__main__':
    fout = open('haodingcontent_20140601.txt','r')
    content = fout.read()
    content_list = content.split('\n')
    del content_list[-1]

    for taskcontent in content_list[1:20]:
        result = haoding_room_task_parser(taskcontent)
        room_list = result['para']
        data_writer(room_list,taskcontent)
        #print room_list
