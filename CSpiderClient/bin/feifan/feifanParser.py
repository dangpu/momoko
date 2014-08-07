#! /usr/bin/env python
#coding=UTF8

'''
    author:fangwang
    date:2014-04-11
    desc: feifan parser
'''

import time
import random
import datetime
import re
import sys
from common.logger import logger
from common.class_common import Flight
from util.crawl_func import crawl_single_page
from common.common import get_proxy,invalid_proxy

reload(sys)
sys.setdefaultencoding('utf-8')

each_flight_content_pat = re.compile(r'<div class="most_outside"(.*?)class="holder">',re.S)
each_flight_content_temp_pat = re.compile(r'<div class="menu_body">(.*?)<div class="stopInfo">',re.S)
each_part_flight_pat = re.compile(r'<ul(.*?)</ul>', re.S)
flight_no_pat = re.compile(r'<li class="airname"><span>(.*?)</span><span>',re.S)
each_flight_no_pat = re.compile(r'<li class="f_num">(.*?)</li>', re.S)
airport_pat = re.compile(r'href="javascript:void\(0\)">(.*?)<span>')
time_temp_pat = re.compile(r'>(.*?)<font>月</font>(.*?)<font>日</font>(.*?)<', re.S)
dept_time_temp_pat = re.compile(r'"strtime">(.*?)<font>月</font>(.*?)<font>日</font>(.*?)<br />', re.S)
dest_time_temp_pat = re.compile(r'<font>月</font>(.*?)<font>日</font>(.*?)</li>', re.S)
all_price_pat = re.compile(r'price="(.*?)"', re.S)
airline_pat = re.compile(r'</span><span>(.*?)</span></li>', re.S)
price_pat = re.compile(r'font-weight:bold;"> (.*?)</label>|<span class="sp2">(\w*)<label>',re.S)
return_rule_pat = re.compile(r'class="p1">(.*?)<span class="closedef"', re.S)
plane_no_pat = re.compile(r'<span><font>(.*?)</font></span>', re.S)

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

AIRPORT_CITY_DICT = {'CPH':'CPH','LIN':'MIL','AGB':'AGB','BGO':'BGO','HEL':'HEL','NAP':'NAP','LIS':'LIS','BOD':'BOD','FNI':'FNI','AGP':'AGP','SXB':'SXB',\
        'SXF':'BER','LYS':'LYS','LBA':'LBA','HAJ':'HAJ','HAM':'HAM','MRS':'MRS','BFS':'BFS','LPL':'LPL','LHR':'LON','SVQ':'SVQ','VIE':'VIE','BVA':'PAR',\
        'MAD':'MAD','BRU':'BRU','MAN':'MAN','TSF':'VCE','FLR':'FLR','BER':'BER','RTM':'RTM','VLC':'VLC','SZG':'SZG','OSL':'OSL','AMS':'AMS','BUD':'BUD',\
        'STO':'STO','TRN':'TRN','BLQ':'BLQ','PRG':'PRG','GRX':'GRX','OXF':'OXF','PSA':'PSA','MXP':'MIL','LCY':'LON','INN':'INN','ANR':'ANR','OPO':'OPO',\
        'BCN':'BCN','LUX':'LUX','GLA':'GLA','MUC':'MUC','LUG':'LUG','CGN':'CGN','BSL':'BSL','PMF':'MIL','SEN':'LON','NUE':'NUE','VRN':'VRN','FCO':'ROM',\
        'FRA':'FRA','WAW':'WAW','DUS':'DUS','LTN':'LON','CDG':'PAR','MMX':'MMA','ORY':'PAR','LEJ':'LEJ','EDI':'EDI','BRS':'BRS','BRN':'BRN','BRE':'BRE',\
        'CIA':'ROM','TXL':'BER','VCE':'VCE','STN':'LON','GVA':'GVA','GOA':'GOA','KLV':'KLV','STR':'STR','GOT':'GOT','ZRH':'ZRH','BHD':'BFS','LGW':'LON',\
        'BHX':'BHX','NCL':'NCL','NCE':'NCE','ARN':'STO','PEK':'BJS','PVG':'SHA','SHA':'SHA','NAY':'BJS','CAN':'CAN','SZX':'SZX'}



def feifan_task_parser(taskcontent):

    #初始化
    result = {}
    result['para'] = None
    result['error'] = 0

    #解析taskcontent 中的出发城市和到达城市的三字码以及出发日期
    try:
        dept_code, dest_code, dept_date = taskcontent.strip().split('&')[0], \
                taskcontent.strip().split('&')[1], \
                taskcontent.strip().split('&')[2]

        dept_day = dept_date[:4] + '-' + dept_date[4:6] + '-' + dept_date[6:]
        dept_year= dept_date[:4]
    except Exception,e:
        logger.error('feifanFlight: wrong content format with %s'%taskcontent)
        result['error'] = TASK_ERROR
        return result
    
    #获取代理
    p = get_proxy(source='feifanFlight')

    if p == None:
        result['error'] = PROXY_NONE
        return result

    #生成URL并判断其是否可用
    url = get_url(dept_code, dest_code, dept_day)    
    
    if url == '' or url == None:
        logger.error('feifanFlight: Get url failed!')
        result['error'] = UNKNOWN_TYPE
        return result

    #抓取页面并判断其是否可用
    #feifan常常要刷新才能获取内容，所以爬取3次
    for i in range(3):
        page = crawl_single_page(url, proxy=p)

        if page != '' and len(page) > 300:
            flights = parsePage(page, dept_year)
            if flights == []:
                if page.find('非凡旅行网-抱歉,您没有权限访问') != -1:
                    invalid_proxy(proxy=p, source='feifanFlight')
                    result['error'] = PROXY_FORBIDDEN
                else:
                    result['error'] = DATA_NONE
                return result
            else:
                result['para'] = flights
                return result
        else:
            continue
    invalid_proxy(proxy=p, source='feifanFlight')
    logger.error('feifanFlight: Get page content failed!')
    result['error'] = PROXY_INVALID
        
    return result
    
def feifan_request_parser(content):
    
    result = -1

    try:
        infos = content.split('|')
        flight_info = infos[0].strip()
        time_info = infos[1].strip()
        ticketsource = infos[2].strip()

        flight_no = flight_info.split('-')[0]
        dept_id,dest_id = AIRPORT_CITY_DICT[flight_info.split('-')[1]],AIRPORT_CITY_DICT[flight_info.split('-')[2]]

        dept_day,dept_hour = time_info.split('_')[0],time_info.split('_')[1]
        dept_date = dept_day[0:4] + '-' + dept_day[4:6] + '-' + dept_day[6:]
        dept_year= dept_date[:4]
        orig_dept_time = dept_date + 'T' + dept_hour + ':00'
    except Exception,e:
        logger.error('feifanFlight: wrong content format with %s'%content + str(e))
        return result

    url = get_url(dept_id, dest_id, dept_date)

    if url == '' or url == None:
        return result
    
    for i in range(3):
        page = crawl_single_page(url, proxy=None)
        if page != '' and len(page) > 300:
            result = ValidatePage(page,dept_year, flight_no, orig_dept_time)
            return result
        else:
            continue
    
    return result

def parsePage(content,dept_year):
    flights  = []
    each_flight_content = each_flight_content_pat.findall(content)
    if len(each_flight_content) > 0: 
        for each_flight_text in each_flight_content:
            flight = Flight()
            try:
                t_price = all_price_pat.findall(each_flight_text)[0]
                each_flight_text_temp = each_flight_content_temp_pat.findall(each_flight_text)[0]
                each_part_flight = each_part_flight_pat.findall(each_flight_text_temp)
                if len(each_part_flight) >= 1:
                    time.sleep(1)
                    flight.dept_id = airport_pat.findall(each_part_flight[0])[0][1:-1]                    
                    flight.dest_id = airport_pat.findall(each_part_flight[-1])[-1][1:-1]
                     
                    dept_time_temp = dept_time_temp_pat.findall(each_part_flight[0])[0]
                    dest_time_temp = dest_time_temp_pat.findall(each_part_flight[-1])[-1]
                    flight.dept_day = dept_year + '-' + dept_time_temp[0].strip() + '-' + \
                            dept_time_temp[1].strip()
                    flight.dept_time = flight.dept_day + 'T' + dept_time_temp[2].strip() + ':00'
                    flight.dest_time = dept_year + '-' +  dept_time_temp[0].strip() + '-' + \
                    dest_time_temp[0].strip() + 'T' + dest_time_temp[1].strip()[-5:] + ':00'
                    
                    dept_time = int(time.mktime(datetime.datetime.strptime(flight.dept_time, \
                            '%Y-%m-%dT%H:%M:%S').timetuple()))
                    dest_time = int(time.mktime(datetime.datetime.strptime(flight.dest_time, \
                            '%Y-%m-%dT%H:%M:%S').timetuple()))
                    flight.dur = dest_time - dept_time + 3600
                    
                    flight.stop = len(each_part_flight) - 1
                else:
                    continue
                flight.price = price_pat.findall(each_flight_text)[0]
                if len(flight.price) > 1:
                    flight.price = int(flight.price[0])
                else:
                    flight.price = int(t_price)

                try:
                    flight.tax = int(t_price) - flight.price
                except:
                    flight.tax = -1.0
                    logger.info('feifanFlight: Can not parse tax info!')

                flight.flight_no = ''
                flight.airline = ''
                flight.plane_no = ''
                for each_flight_text_t in each_part_flight:
                    flight.flight_no = flight.flight_no + flight_no_pat.findall(each_flight_text_t)[0][:8].replace(' ','') + '_'
                    flight.plane_no = flight.plane_no + plane_no_pat.findall(each_flight_text_t)[0].replace(' ','') + '_'
                    flight.airline = flight.airline + airline_pat.findall(each_flight_text_t)[0].replace(' ','') + '_'
                
                flight.flight_no = flight.flight_no[:-1]
                flight.plane_no = flight.plane_no[:-1]
                flight.airline = flight.airline[:-1]
                
                flight.return_rule = return_rule_pat.findall(each_flight_text)[0].replace('<p>','').replace('\n','') \
                        .replace('。','').replace('</p>','。').strip().replace(' ','')
                flight.currency = 'CNY'
                flight.source = 'feifan::feifan'
                flight.seat_type = '经济舱'
                #print flight.return_rule
                flight_tuple = (flight.flight_no, flight.plane_no, flight.airline, flight.dept_id, flight.dest_id, \
                        flight.dept_day, flight.dept_time, flight.dest_time, flight.dur, flight.price, \
                        flight.tax, flight.surcharge, flight.currency, flight.seat_type, flight.source, \
                        flight.return_rule, flight.stop)

                flights.append(flight_tuple)
            except Exception, e:
                #logger.info('Parse this flight failed!' + str(e))
                continue
    else:
        logger.error('feifanFlight: Can not find each_flight_content')
        return flights

    return flights

def ValidatePage(content,dept_year, flight_no, orig_dept_time):

    result = -1

    each_flight_content = each_flight_content_pat.findall(content)

    if len(each_flight_content) > 0: 
        for each_flight_text in each_flight_content:
            flight = Flight()
            try:
                t_price = all_price_pat.findall(each_flight_text)[0]
                each_flight_text_temp = each_flight_content_temp_pat.findall(each_flight_text)[0]
                each_part_flight = each_part_flight_pat.findall(each_flight_text_temp)
                if len(each_part_flight) >= 1:
                    flight.dept_id = airport_pat.findall(each_part_flight[0])[0][1:-1]                    
                    flight.dest_id = airport_pat.findall(each_part_flight[-1])[-1][1:-1]

                    dept_time_temp = dept_time_temp_pat.findall(each_part_flight[0])[0]
                    dest_time_temp = dest_time_temp_pat.findall(each_part_flight[-1])[-1]
                    flight.dept_day = dept_year + '-' + dept_time_temp[0].strip() + '-' + dept_time_temp[1].strip()

                    flight.dept_time = flight.dept_day + 'T' + dept_time_temp[2].strip() + ':00'
                    flight.dest_time = dept_year + '-' +  dept_time_temp[0].strip() + '-' + \
                            dest_time_temp[0].strip() + 'T' + dest_time_temp[1].strip()[-5:] + ':00'
                    dest_time_temp[0].strip() + 'T' + dest_time_temp[1].strip()[-5:] + ':00'

                    dept_time = int(time.mktime(datetime.datetime.strptime(flight.dept_time,'%Y-%m-%dT%H:%M:%S').timetuple()))
                    dest_time = int(time.mktime(datetime.datetime.strptime(flight.dest_time, '%Y-%m-%dT%H:%M:%S').timetuple()))
                else:
                    continue
                flight.price = price_pat.findall(each_flight_text)[0]
                if len(flight.price) > 1:
                    flight.price = int(flight.price[0])
                else:
                    flight.price = int(t_price)

                flight.flight_no = ''
                for each_flight_text_t in each_part_flight:
                    flight.flight_no = flight.flight_no + flight_no_pat.findall(each_flight_text_t)[0][:8].replace(' ','') + '_'

                flight.flight_no = flight.flight_no[:-1]

                if flight.flight_no == flight_no and flight.dept_time == orig_dept_time:
                    result = flight.price
                    break
            except Exception, e:
                continue
    else:
        return result

    return result


def get_url(dept_code, dest_code, dept_day):
    url = ''
    t = str(random.random())
    url = 'http://www.ufeifan.com/s?national=true&flightType=2&tickType=ADT&personNum=1&originCode=' \
            + dept_code + '_1&desinationCode=' + dest_code + '_1&originDate=' + dept_day +  \
            '&childNum=0&directFlightsOnly=2&lang=ZH&currency=CNY&country=CN&syn=true&flush=' + t
    return url


if __name__ == '__main__':

    taskcontent = 'BJS&PAR&20140602'

    result1 = feifan_task_parser(taskcontent)

    print str(result1)

    content = 'SU0205_SU4456-PEK-CDG|20140602_11:40|feifan::feifan'

    result2 = feifan_request_parser(content)

    print str(result2)
