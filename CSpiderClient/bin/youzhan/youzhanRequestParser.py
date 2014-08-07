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

def youzhan_request_parser(taskcontent):
    all_info = []
    room_list = []
    #taskcontent = hotelid|city_cn_name|roominfo(room_type)|date|source
    #example = 107634|根特|双人间|20140419-20140520|youzhan::Booking.com
    taskcontent = taskcontent.strip().encode('utf-8')
    try:
        infos = taskcontent.split('|')
        hotel_id = infos[0]
        city_name = infos[1]
        ipathid = cities_dict[city_name.encode('utf-8')]
        #logger.info(ipathid)
        room_type = infos[2]
        checkin_date = infos[3].split('-')[0]#format:2014-05-05
        checkout_date = infos[3].split('-')[1]#format:2014-05-06
        real_source = infos[4].split('::')[-1]
        #logger.info('type' + room_type + ' source' + real_source)
    except Exception,e:
        logger.error('wrong content format' + str(e))
        return -1
    
    p = get_proxy()
    
    room = Room()

    price_url = get_price_url(hotel_id,ipathid,checkin_date,checkout_date)
    price_page = crawl_single_page(price_url,n=1,proxy=p)
    price_list = price_parser(price_page,hotel_id)

    result = 1000000#设置一个极大值

    if price_list != []:
        for each_room in price_list:
            if len(each_room) > 3:
                #room.city = city
                #room.occupancy = 1
                #room.hotel_name = hotel.hotel_name
                #print each_room
                #room.room_desc = each_room[3]
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

                if each_room[0] != u'nbsp;':# and each_room[0] != None:
                    room.price = int(each_room[0])
                else :
                    room.price = -1

                #logger.info('room_type: ' + room.room_type + ' room_source: ' + room.real_source + str(room.price))

                if room.room_type == room_type and room.real_source == real_source:
                    if room.price < result and room.price != -1:
                        result = room.price
        if result < 1000000:
            return result
        else : 
            return -1
    else:
        return -1


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
        logger.error('Map html not found! line 213')
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
        logger.error(str(e) + ': line 227')
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
        logger.error(str(e) + ': line 252')
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
        logger.error(str(e) + ': line 271')

    try:
        room_facilities_content = room_facilities_content_pat.findall(info_html)[0]
        room_facilities_temp = each_facility_pat.findall(room_facilities_content)
        for each_room_f in room_facilities_temp:
            service = service + each_room_f + '|'
    except Exception,e:
        logger.error(str(e) + ': line 279')

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
                    #print price_l[0].replace(' ','').replace('\n','').replace(',','')[1:]
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
            logger.error('Price content not found : 358')
    except Exception,e:
        logger.error(str(e) + ':' + 'line 360')

    return price_temp


def grade_parser(grade_temp):
    grade_str = ''
    if grade_temp != '' and len(grade_temp) > 100:
        try:
            content_json = json.loads(grade_temp)
            grade_html = content_json['sHtml']
            grade_content = grade_content_pat.findall(grade_html)
        except Exception,e:
            logger.error(str(e) + ':' + '403')
            return grade_str

        if grade_content != [] and type(grade_content).__name__ != 'NoneType':
            for temp in grade_content:
                grade_source = grade_source_pat.findall(temp)
                grade_num = grade_num_pat.findall(temp)
                try:
                    grade_str = grade_str + grade_source[0] + ':' +\
                                grade_num[0] + '|'
                except Exception,e:
                    logger.error(str(e) + ':' + '414')
                    grade_str = ''
        else:
            logger.error('Error: Grade content not found!')
    else:
        logger.error('Error: Crawling rating page failed!')

    return grade_str


if __name__ == '__main__':

    content = '107634&根特&双人间&2014-04-16&2014-04-17&Booking.com'

    result = youzhan_request_parser(content)

    print str(result)
