#! /usr/bin/env python
#coding=UTF8

"""
    @author:fangwang
    @date:2014-04-05
    @desc: Crawl and parse youzhan website
"""
import json
import datetime
import re
import time
"""
from crawl_func import crawl_single_page
from class_common import Hotel
from class_common import Room
from class_common import Comment
"""
import sys
from common.logger import logger
from common.common import get_proxy, invalid_proxy
#from base.vaild_proxy import vaildproxy
from common.class_common import Hotel
from common.class_common import Room
from common.class_common import Comment
from util.crawl_func import crawl_single_page

reload(sys)
sys.setdefaultencoding('utf-8')

#location pattern
staticmap_pat = re.compile(r'center=(.*?)&markers', re.S)
hotel_name_pat = re.compile(r'alt="(.*?)" class="slide_staticmap"', re.S)

#info pattern
address_pat = re.compile(r'</h3><em>(.*?)</em> | <em class="link view_on_map">', re.S)
description_pat = re.compile(r'data-fulltext="(.*?)"', re.S)
hotel_facilities_content_pat = re.compile(r'hotel_facilities(.*?)</div>',re.S)
each_facility_pat = re.compile(r'<li>(.*?)</li>', re.S)
room_facilities_content_pat = re.compile(r'room_facilities(.*?)</div>',re.S)
top9_facilities_pat = re.compile(r'top9features(.*?)</div>',re.S)
top9_each_pat = re.compile(r'hidden_phone">(.*?)</span>', re.S)
sports_facilities_pat = re.compile(r'sports(.*?)</div', re.S)

#price pattern
price_content_pat = re.compile(r'<div onclick(.*?)</span></button>',re.S)
price_pat = re.compile(r'class="price price_info" >(.*?)</strong>',re.S)
breakfast_pat = re.compile(r'breakfast (.*?)_breakfast', re.S)
#source_pat = re.compile(r'title="(.*?)"/></div>')
source_pat = re.compile(r'alt="(.*?)"', re.S)
room_desc_pat = re.compile(r'class="desc_text">(.*?)</span></div>', re.S)

#grade pattern
grade_content_pat = re.compile(r'<li(.*?)</li>', re.S)
grade_source_pat = re.compile(r'class="name">(.*?)</span>', re.S)
grade_num_pat = re.compile(r'class="rating_overall"><strong>(.*?)</strong>', re.S)


def youzhan_task_parser(taskcontent):
    all_info = []
    room_list = []
    taskcontent = taskcontent.encode('utf-8').strip()
    hotel_id = taskcontent.split('&')[0]
    star = taskcontent.split('&')[2]
    ipathid = taskcontent.split('&')[1]
    city = taskcontent.split('&')[3]
    country = taskcontent.split('&')[4]
    #room_type = taskcontent.split('&')[3]
    from_date_temp = taskcontent.split('&')[5]
    from_date = from_date_temp[:4] + '-' + from_date_temp[4:6] + '-' \
                + from_date_temp[6:]
    to_date_temp = datetime.datetime(int(from_date_temp[:4]), int(from_date_temp[4:6]), \
                                     int(from_date_temp[6:]))
    to_date = str(to_date_temp + datetime.timedelta(days = 1))[:10]

    #获取代理
    
    p = get_proxy()

    #if p == "":
        #logger.error("get proxy failed")
        #return None
    
    hotel = Hotel()
    room = Room()

    rating_url = get_rating_url(hotel_id)
    rating_page = crawl_single_page(rating_url, proxy=p)
    
    grade_str = grade_parser(rating_page)
    
    if grade_str != '':
        hotel.grade = grade_str[:-1]
    else:
        pass
        #logger.error('Error: No grade_str found!')

    map_url = get_map_url(hotel_id)
    map_page = crawl_single_page(map_url, proxy=p)
    #print map_page
    map_info_list = staticmap_parser(map_page)
    if map_info_list != []:
        hotel.hotel_name = map_info_list[1]
        if is_alphabet(hotel.hotel_name.decode('utf-8')) == True:
            hotel.hotel_name_en = hotel.hotel_name
        else:
            hotel.hotel_name_en = 'NULL'
        hotel.map_info = map_info_list[0]
    else:
        logger.error('youzhanHotel: Map info do not have hotel name and map_info')
        return []

    info_url = get_info_url(hotel_id,from_date,to_date)
    info_page = crawl_single_page(info_url,proxy=p)
    if info_page == '':
        #invalid_proxy(p)
        return []
    info_list = info_parser(info_page)

    if info_list != []:
        hotel.country = country
        hotel.city = city
        hotel.address = info_list[1]
        hotel_desc_temp = info_list[3].replace('&lt;br/&gt;','').replace('&#039;','')
        if hotel_desc_temp != '':
            hotel.description = hotel_desc_temp
        else:
            hotel.description = 'NULL'
        hotel.service = info_list[4]

        if '停车场' in hotel.service:
            hotel.has_parking = 'Yes'
        if '无线网络' in hotel.service or 'wifi' in hotel.service:
            hotel.has_wifi = 'Yes'
    else:
        return []

    hotel.source = 'youzhan'
    hotel.source_id = hotel_id
    hotel.star = star

    price_url = get_price_url(hotel_id,ipathid,from_date,to_date)
    price_page = crawl_single_page(price_url,proxy=p)
    price_list = price_parser(price_page,hotel_id)
    #print '********'
    #print price_list
    if price_list != []:
        for each_room in price_list:
            if len(each_room) > 3:
                room.city = city
                room.occupancy = 2
                room.hotel_name = hotel.hotel_name
                #print '******'
                #print each_room
                room.room_desc = each_room[3]
                room.real_source = each_room[2]
                

                num = each_room[3].find('-')
                if num > 0:
                    if len(each_room[3][:num]) < 20:
                        room.room_type = each_room[3][:num]
                    else:
                        room.room_type = 'NULL'
                else:
                    if len(each_room[3]) < 20:
                        room.room_type = each_room[3]
                    else:
                        room.room_type = 'NULL'
            
                if each_room[0] != u'nbsp;':
                    room.price = each_room[0]
                room.has_breakfast = each_room[1]
                room.room_desc = each_room[3]

                if '免费WiFi' in room.room_desc:
                    hotel.is_wifi_free = 'Yes'
                
                if '免费取消' in room.room_desc:
                    hotel.is_cancel_free = 'Yes'

                room.currency = 'CNY'
                room.source = 'youzhan'
                room.source_hotelid = hotel_id
                room.check_in = from_date
                room.check_out = to_date

                room_tuple = (room.hotel_name,room.city,room.source,room.source_hotelid,\
                    room.source_roomid,room.real_source,room.room_type,room.occupancy,\
                    room.bed_type,room.size,room.floor,room.check_in,room.check_out,room.price,\
                    room.tax,room.currency,room.is_extrabed,room.is_extrabed_free,room.has_breakfast,\
                    room.is_breakfast_free,room.is_cancel_free,room.room_desc)
                room_list.append(room_tuple)

    hotel_tuple = (hotel.hotel_name, hotel.hotel_name_en,hotel.source,hotel.source_id,hotel.brand_name,\
        hotel.map_info,hotel.address,hotel.city,hotel.country,hotel.postal_code, \
        hotel.star,hotel.grade,hotel.has_wifi,hotel.is_wifi_free,hotel.has_parking,\
        hotel.is_parking_free,hotel.service,hotel.img_items,hotel.description)
    hotel_list = []
    hotel_list.append(hotel_tuple)
    all_info.append(hotel_list)
    all_info.append(room_list)

    return all_info
    #hotel1 = all_info[0]
    #room1 = all_info[1]
    #print hotel1
    #for x in room1:
        #print x


def get_rating_url(hotel_id):
    rating_url = 'http://www.youzhan.com/search/slideout/cn-CN-CN/v8_03_1_af_cache/rating/' + hotel_id + '.html'

    return rating_url


def get_map_url(hotel_id):
    map_url = 'http://www.youzhan.com/search/slideout/cn-CN-CN/v8_03_1_af_cache/staticmap/' + hotel_id + '.html'

    return map_url


def get_info_url(hotel_id, from_date, to_date):
    info_url = 'http://www.youzhan.com/search/slideout/cn-CN-CN/v8_03_1_af_cache/info/'+ hotel_id + '.html?aDateRange[arr]=' +  from_date + '&aDateRange[dep]=' + to_date

    return info_url


def get_price_url(hotel_id, iPathId, arr_date, dept_date):
    url_temp = 'http://www.youzhan.com/search/slideout/deals/0/1/' + hotel_id + '/' + hotel_id + '/?' + 'iPathId=' + iPathId + '&aDateRange%5Barr%5D=' + arr_date + '&aDateRange%5Bdep%5D=' + dept_date  + '&iRoomType=7&&bIsFirstPoll=false&_='
    url = url_temp + str(int(time.time()))

    return url


def staticmap_parser(content):
    map_infos = []
    if content != '' and len(content) > 30:
        map_content_json = json.loads(content)
        map_html = map_content_json['sHtml']
    else:
        logger.error('youzhanHotel: Map html not found! line 213')
        return map_infos

    try:
        staticmap_temp = staticmap_pat.findall(map_html)
        hotel_name_temp = hotel_name_pat.findall(map_html)
        staticmap_x_num = staticmap_temp[0].find('%')
        staticmap_y_num = staticmap_temp[0].rfind('C') + 1
        location_x = staticmap_temp[0][:staticmap_x_num]
        location_y = staticmap_temp[0][staticmap_y_num:]
        location_temp = location_y + ',' + location_x
        map_infos.append(location_temp)
        hotel_name = hotel_name_temp[0]
        map_infos.append(hotel_name)
    except Exception,e:
        #logger.error(str(e) + ': line 227')
        return map_infos

    return map_infos


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False

def info_parser(content):
    info = []
    service = ''
    if content != '' and len(content) > 30:
        info_json = json.loads(content)
        info_html = info_json['sHtml']
    try:
        address_temp = address_pat.findall(info_html)[0]
        num01 = address_temp.rfind(',') + 1
        country = address_temp[num01:]
        #info.append(country)
        address_temp2 = address_temp[:num01 - 1]
        num02 = address_temp2.rfind(',') + 1
        city = address_temp2[num02:]
        #info.append(city)
        address = address_temp2[:num02 - 1]
        info.append(country)
        info.append(address)
        info.append(city)
    except Exception,e:
        #logger.error(str(e) + ': line 252')
        return info

    try:
        description = description_pat.findall(info_html)[0].replace(' ','').replace('\n','').replace('&lt;br/&gt;','').replace('&#039;/','') \
                .replace('&lt;/strong&gt;','').replace('&lt;strong&gt;','')
        info.append(description)
    except Exception,e:
        #logger.error(str(e) + ': line 262')
        info.append('')

    try:
        hotel_facilities_content = hotel_facilities_content_pat.findall(info_html)[0]
        hotel_facilities_temp = each_facility_pat.findall(hotel_facilities_content)
        for each_hotel_f in hotel_facilities_temp:
            service = service + each_hotel_f + '|'
    except Exception,e:
        pass
        #logger.error(str(e) + ': line 271')

    try:
        room_facilities_content = room_facilities_content_pat.findall(info_html)[0]
        room_facilities_temp = each_facility_pat.findall(room_facilities_content)
        for each_room_f in room_facilities_temp:
            service = service + each_room_f + '|'
    except Exception,e:
        pass
        #logger.error(str(e) + ': line 279')

    try:
        top9_facilities_content = top9_facilities_pat.findall(info_html)[0]
        #print top9_facilities_content
        top9_facilities_temp = each_facility_pat.findall(top9_facilities_content)
        for each_top_f in top9_facilities_temp:
            if 'disabled' in  each_top_f:
                pass
            else:
                top9_facilities = top9_each_pat.findall(each_top_f)
                for w in  top9_facilities:
                    service = service + w + '|'
    except Exception,e:
        service = service + ''
        #logger.error(str(e) + ':' + 'line 292')

    try:
        sports_facilities_content = sports_facilities_pat.findall(info_html)[0]
        sports_facilities_temp = each_facility_pat.findall(sports_facilities_content)
        for each_sport_f in sports_facilities_temp:
            service = service + each_sport_f + '|'
    except Exception,e:
        #logger.error(str(e) + ':' + 'line 300')
        service = service + ''

    if service != '':
        info.append(service.replace(',','')[:-1])
    else:
        info.append('')

    return info


def price_parser(content, hotelid):
    price_temp = []
    if content != '' and len(content) > 300:
        price_json = json.loads(content)
        price_html = price_json[hotelid]['sHtml']
    else:
        logger.error('No price content found! line 316')
        return price_temp

    if price_json[hotelid]['iNumDeals'] <= 0:
        return price_temp

    try:
        price_content = price_content_pat.findall(price_html)
        if price_content != []:
            for temp in price_content:
                each_hotel_price = []
                price_l = price_pat.findall(temp)
                breakfast = breakfast_pat.findall(temp)
                hotel_source = source_pat.findall(temp)
                room_desc = room_desc_pat.findall(temp)

                try:
                    print price_l[0].replace(' ','').replace('\n','').replace(',','')[1:]
                    each_hotel_price.append(price_l[0].replace(' ','').replace('\n','').replace(',','')[1:])
                except Exception,e:
                    logger.error(str(e) + ':' + 'no price')
                    continue

                try:
                    if breakfast[0] == 'with':
                        each_hotel_price.append('Yes')
                    elif breakfast[0] == 'no':
                        each_hotel_price.append('No')
                except Exception,e:
                    #logger.info('warning:' + str(e) + ':' + 'line 343')
                    each_hotel_price.append('No')

                try:
                    each_hotel_price.append(hotel_source[0])
                except Exception,e:
                    logger.error(str(e) + ':' + 'line 347')
                    each_hotel_price.append('NULL')

                try:
                    each_hotel_price.append(room_desc[0])
                except Exception,e:
                    logger.error(str(e) + ':' + 'line 353')
                    each_hotel_price.append('NULL')

                price_temp.append(each_hotel_price)
        else:
            logger.error('youzhanHotel: Price content not found')
    except Exception,e:
        pass
        #logger.error(str(e) + ':' + 'line 360')

    return price_temp


def grade_parser(grade_temp):
    grade_str = ''
    if grade_temp != '' and len(grade_temp) > 100:
        try:
            content_json = json.loads(grade_temp)
            grade_html = content_json['sHtml']
            grade_content = grade_content_pat.findall(grade_html)
        except Exception,e:
            #logger.error(str(e) + ':' + '403')
            return grade_str

        if grade_content != [] and type(grade_content).__name__ != 'NoneType':
            for temp in grade_content:
                grade_source = grade_source_pat.findall(temp)
                grade_num = grade_num_pat.findall(temp)
                try:
                    grade_str = grade_str + grade_source[0] + ':' +\
                                grade_num[0] + '|'
                except Exception,e:
                    #logger.error(str(e) + ':' + '414')
                    grade_str = ''
        else:
            logger.error('Error: Grade content not found!')
    else:
        logger.error('Error: Crawling rating page failed!')

    return grade_str


if __name__ == '__main__':
    content = '91485&344421&2&瓦伦西亚&西班牙&20140426'

    result = youzhan_task_parser(content)

    print str(result)
