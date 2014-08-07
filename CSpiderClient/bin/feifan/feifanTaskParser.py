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

each_flight_content_pat = re.compile(r'<div class="most_outside"(.*?)class="holder">', \
        re.S)
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

def feifan_task_parser(taskcontent):
    #解析taskcontent 中的出发城市和到达城市的三字码以及出发日期
    try:
        dept_code, dest_code, dept_date = taskcontent.strip().split('&')[0], \
                taskcontent.strip().split('&')[1], \
                taskcontent.strip().split('&')[2]
    except Exception,e:
        logger.error('feifanFlight: wrong content format with %s'%taskcontent)
        return []
    
    dept_day = dept_date[:4] + '-' + dept_date[4:6] + '-' + dept_date[6:]
    dept_year= dept_date[:4]
    #获取代理
    p = get_proxy()

    #生成URL并判断其是否可用
    url = get_url(dept_code, dest_code, dept_day)    
    
    if url != '' and url != None:
        page = crawl_single_page(url, proxy=p)
    else:
        logger.error('feifanFlight: Get url failed!')
        return []
    #抓取页面并判断其是否可用
    if page != '' and len(page) > 300:
        flights = parsePage(page, dept_year)
    else:
        logger.error('feifanFlight: Get page content failed!')
        return []
        
    return flights
    

def parsePage(content,dept_year):
    flights  = []
    each_flight_content = each_flight_content_pat.findall(content)
    print len(each_flight_content)
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

def get_url(dept_code, dest_code, dept_day):
    url = ''
    t = str(random.random())
    url = 'http://www.ufeifan.com/s?national=true&flightType=2&tickType=ADT&personNum=1&originCode=' \
            + dept_code + '_1&desinationCode=' + dest_code + '_1&originDate=' + dept_day +  \
            '&childNum=0&directFlightsOnly=2&lang=ZH&currency=CNY&country=CN&syn=true&flush=' + t
    return url


if __name__ == '__main__':
    fileHandle = open('workload/feifancontent_20140417.txt','r')
    contentlist = fileHandle.readlines()
    for content in contentlist[100:101]:
        #taskcontent = content.strip()
        taskcontent = 'PAR&LON&20140501'
        print taskcontent
        print feifan_parser(taskcontent)
