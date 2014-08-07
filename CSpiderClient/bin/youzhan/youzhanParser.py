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
import sys
from common.logger import logger
from common.common import get_proxy, invalid_proxy
from common.class_common import Hotel
from common.class_common import Room
from common.class_common import Comment
from util.crawl_func import crawl_single_page

reload(sys)
sys.setdefaultencoding('utf-8')

#info pattern
address_pat = re.compile(r'</h3><em>(.*?)</em> | <em class="link view_on_map">', re.S)
description_pat = re.compile(r'data-fulltext="(.*?)"', re.S)
#price pattern
price_content_pat = re.compile(r'<div onclick(.*?)</span></button>',re.S)
price_pat = re.compile(r'class="price price_info" >(.*?)</strong>',re.S)
breakfast_pat = re.compile(r'breakfast (.*?)_breakfast', re.S)
#source_pat = re.compile(r'title="(.*?)"/></div>')
source_pat = re.compile(r'alt="(.*?)"', re.S)
room_desc_pat = re.compile(r'class="desc_text">(.*?)</span></div>', re.S)


cities_dict = {'巴黎':'36103','罗马':'44337','威尼斯':'94718','佛罗伦萨':'45864','米兰':'45605',\
        '巴塞罗那':'344066','阿姆斯特丹':'46814','慕尼黑':'3577','伦敦':'38715','维也纳':'44232',\
        '布拉格':'42694','柏林':'8513','法兰克福':'511162','尼斯':'37090','布鲁塞尔':'44365',\
        '马德里':'32026','比萨':'45888','苏黎世':'46889','日内瓦':'46871','科隆':'15481',\
        '斯德哥尔摩':'52040','爱丁堡':'41576','布达佩斯':'529160','哥本哈根':'45069',\
        '海德堡':'1109','牛津':'478575','伯尔尼':'46869','卢森堡':'71752','塞维利亚':'346456',\
        '汉堡':'9643','鹿特丹':'46852','曼彻斯特':'38961','马赛':'37113','赫尔辛基':'81568',\
        '里昂':'37514','维罗纳':'118721','杜塞尔多夫':'15475','那不勒斯':'45499','因斯布鲁克':'44026',\
        '斯图加特':'3401','格拉纳达':'339311','伯明翰':'41018','安特卫普':'44394','格拉斯哥':'41585',\
        '巴塞尔':'46868','波恩':'15471','卑尔根':'44291','利物浦':'38950','纽伦堡':'7761',\
        '斯特拉斯堡':'35905','波尔图':'51096','根特':'44462','瓦伦西亚':'344421','华沙':'86484',\
        '波尔多':'35213','汉诺威':'458029','热那亚':'45560','博洛尼亚':'45358','不来梅':'9640',\
        '哥德堡':'52398','利兹':'41373','布里斯托尔':'40057','亚琛':'15468','卢加诺':'49294','诺丁汉':'37870',\
        '尼姆':'36223','卡罗维发利':'73394','莱比锡':'21470','都灵':'45700','纽卡斯尔':'38773',\
        '贝尔法斯特':'404053','曼海姆':'1112','谢菲尔德':'41443','奥格斯堡':'3565','奥斯陆':'44269','马尔默':'52259'}

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

CONTENT_LEN = 1000

def youzhan_task_parser(taskcontent):
    all_info = []
    room_list = []

    result = {}
    result['para'] = None
    result['error'] = 0

    taskcontent = taskcontent.encode('utf-8').strip()

    try:
        hotel_id = taskcontent.split('&')[0]
        star = taskcontent.split('&')[2]
        ipathid = taskcontent.split('&')[1]
        city = taskcontent.split('&')[3]
        country = taskcontent.split('&')[4]
        from_date_temp = taskcontent.split('&')[5]
        from_date = from_date_temp[:4] + '-' + from_date_temp[4:6] + '-' \
                    + from_date_temp[6:]
        to_date_temp = datetime.datetime(int(from_date_temp[:4]), int(from_date_temp[4:6]), \
                                         int(from_date_temp[6:8]))
        to_date = str(to_date_temp + datetime.timedelta(days = 1))[:10]
    except Exception,e:
        logger.info('youzhanHotel: Wrong Content Format with %s'%taskcontent)
        result['error'] = TASK_ERROR
        return result

    room = Room()

    price_url = get_price_url(hotel_id,ipathid,from_date,to_date)
    i = 0
    content_len = 0
    while i < 5 and content_len < CONTENT_LEN:
        #p = get_proxy()
        p = get_proxy(source='youzhanHotel')
        #print p
        if p == None:
            result['error'] = PROXY_NONE
            return result

        url = price_url + str(int(time.time() * 1000))
        price_page = crawl_single_page(url,proxy=p,n=1)
        content_len = len(price_page)
        i += 1

    if price_page == None or price_page == '':
        invalid_proxy(proxy=p, source='youzhanHotel')
        result['error'] = PROXY_INVALID
        return result
    #print price_page
    price_list = price_parser(price_page,hotel_id)

    if price_list != []:
        for each_room in price_list:
            if len(each_room) > 3:
                room.city = city
                room.occupancy = 2
                #room.hotel_name = hotel.hotel_name
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
                    room.is_wifi_free = 'Yes'
                
                if '免费取消' in room.room_desc:
                    room.is_cancel_free = 'Yes'

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

    else:
        result['error'] = DATA_NONE
        return result

    result['para'] = room_list
    return result


def youzhan_request_parser(content):
    #content = hotelid|city_cn_name|roominfo(room_type)|date|source
    #example = 107634|根特|双人间|20140419-20140520|youzhan::Booking.com

    content = content.strip().encode('utf-8')
    try:
        infos = content.split('|')
        hotel_id = infos[0]
        city_name = infos[1]
        ipathid = cities_dict[city_name.encode('utf-8')]
        room_type = infos[2]
        checkin_date = infos[3].split('-')[0]#format:2014-05-05
        checkout_date = infos[3].split('-')[1]#format:2014-05-06
        real_source = infos[4].split('::')[-1]
    except Exception,e:
        logger.error('youzhanHotel: Wrong Content Format with %s'%content)
        return -1

    result = 1000000#设置一个极大值

    room = Room()

    price_url = get_price_url(hotel_id,ipathid,checkin_date,checkout_date)
    i = 0
    content_len = 0
    while i < 5 and content_len < CONTENT_LEN:
        #p = get_proxy()
        #print p
        url = price_url + str(int(time.time() * 1000))
        #print 'url: ' + url
        price_page = crawl_single_page(url,proxy=None,n=1)
        content_len = len(price_page)
        #print i
        i += 1

    #print price_page
    if price_page == None or price_page == '':
        invalid_proxy(proxy=p, source='youzhanHotel')
        result['error'] = PROXY_INVALID
        return result

    price_list = price_parser(price_page,hotel_id)
    #print price_list

    if price_list != []:
        for each_room in price_list:
            if len(each_room) > 3:
                room.real_source = each_room[2]

                num = each_room[3].find('-')
                if num > 0:
                    if len(each_room[3][:num]) < 20:
                        room.room_type = each_room[3][:num].strip()
                    else:
                        room.room_type = 'NULL'
                else:
                    if len(each_room[3]) < 20:
                        room.room_type = each_room[3].strip()
                    else:
                        room.room_type = 'NULL'

                if each_room[0] != u'nbsp;':
                    room.price = int(each_room[0])
                else :
                    room.price = -1

                if room.room_type == room_type and room.real_source == real_source:
                    if room.price < result and room.price != -1:
                        result = room.price

            if result < 1000000:
                 return result
            else:
                 return -1

    else:
        return -1


def get_price_url(hotel_id, iPathId, arr_date, dept_date):
    url_temp = 'http://www.youzhan.com/search/slideout/deals/0/1/' + hotel_id + '/' + hotel_id + '/?' + 'iPathId=' + iPathId + '&aDateRange%5Barr%5D=' + arr_date + '&aDateRange%5Bdep%5D=' + dept_date  + '&iRoomType=7&&bIsFirstPoll=false&_='

    return url_temp


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False


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
                    #print price_l[0].replace(' ','').replace('\n','').replace(',','')[1:]
                    each_hotel_price.append(price_l[0].replace(' ','').replace('\n','').replace(',','')[1:])
                except Exception,e:
                    logger.error('youzhanHotel: ' + str(e) + ':' + 'no price')
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


if __name__ == '__main__':
    '''
    fout = open('content','r')
    content = fout.read()
    content_list = content.split('\n')
    del content_list[-1]

    for task in content_list:
        print task
        result = youzhan_task_parser(task)
        print 'room list length' + str(len(result))

       # print len(result)
    #for x in result:
    #    print x
    '''
    content = '91485&344421&2&瓦伦西亚&西班牙&20140605'

    result1 = youzhan_task_parser(content)

    print str(result1)

    content = '107634|根特|双人间|20140701-20140702|youzhan::Booking.com'
    result2 = youzhan_request_parser(content)

    print str(result2)
