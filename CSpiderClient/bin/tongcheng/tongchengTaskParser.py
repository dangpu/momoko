#!/usr/bin/env python
#coding=UTF8

"""
    @author:fangwang
    @date:2014-04-13
    @desc: crawl and parse 17u web content
"""

import json
import time
import re
import sys
import urllib
from common.logger import logger
from util.crawl_func import crawl_single_page
from common.class_common import Flight
from common.common import get_proxy, invalid_proxy
from time import sleep

reload(sys)
sys.setdefaultencoding('utf-8')

url_pat1 = re.compile(r'tc10805565235\((.*?)\);"', re.S)
search_code_pat = re.compile(r'code:"(.*?)"', re.S)

def tongcheng_task_parser(taskcontent):
    flights = []
    taskcontent.encode('utf-8')
    try:
        info_list = taskcontent.split('&')
        if len(info_list) < 5:
            return []
    except Exception, e:
        logger.error('tongchengFlight,wrong content format with %s'%(taskcontent))
    
    dept_id, dest_id, dept_city, dest_city, dept_date_temp = info_list[0], info_list[1], \
            info_list[2], info_list[3], info_list[4]

    dept_day = dept_date_temp[:4] + '-' + dept_date_temp[4:6] + '-' +dept_date_temp[6:]
    
    p = get_proxy()
        
    url = get_url(dept_city, dest_city, dept_day, dept_id, dest_id, p)

    if url != '':
        page = crawl_single_page(url, proxy = p)#, Accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    else:
        logger.error('tongchengFlight: Get url failed!')
        return flights
    
    if page != '' and len(page) > 100:
        flights = ParsePage(page)
    else:
        logger.error('tongchengFlight: Crawl page failed!')
        return flights

    return flights


def get_url(dept_city, dest_city, dept_date, dept_id, dest_id, proxy):
    parser_url = ''
    url_temp = 'http://www.ly.com/iflight/flightinterajax.aspx?action=SEARCHURL&airplaneInternatType=1&iOrgPort=' + dept_city + '&iArvPort=' + dest_city + '&idtGoDate=' + dept_date + '&idtBackDate=时间/日期&sel_inCabinType=Y&sel_inPassengersType=1&sel_inAdult=1&sel_inChild=0&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&callback=tc10805565235'

    page1 = crawl_single_page(url_temp, proxy=proxy)#, n=1,  Accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    
    try:
        num01 = page1.find('(')
        num02 = page1.rfind(')')
        json_content_temp = page1[num01+1:num02]
        json_temp1 = json.loads(json_content_temp)
        if json_temp1['state'] == 100:
            url_temp1 =  json_temp1['href']
        else:
            return parser_url
        #if json_temp1[''] 
    except Exception,e:
        #logger.error('Can not get url temp 1!')
        return parser_url
    print 'Yeap'
    url_temp2 = 'http://www.ly.com' + url_temp1
    
    page2 = crawl_single_page(url_temp2,proxy = proxy)#, n=1, Accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    #print page2
    try:
        search_code = search_code_pat.findall(page2)[0]
    except Exception,e:
        logger.error('tongchengFlight: Can not get search code!' + str(e))
        return parser_url
    
    parser_url = 'http://www.ly.com/iflight/AjaxHandler.ashx?action=GRADATIONQUERYFLIGHT&TravelType=0&Departure=' + dept_city + '&DepartureC=' + dept_id + '&Arrival=' + dest_city + '&ArrivalC=' + dest_id + '&DepartureDate=' + dept_date + '&ReturnDate=1900-01-01&AdultNum=1&ChildNum=0&CabinType=1&FlatType=1&PassengerType=1&pageCode=' + search_code + '&SearchGuid=&PreGuid=&userId=&isFirst=true'
    
    return parser_url


def ParsePage(content):
    flights = []
    
    if content != '' and len(content) > 100:

        content_json = json.loads(content)
        #print content_json['OriginDestinationOption']
        if 'OriginDestinationOption' in content_json.keys():
            for each_flight_json in content_json['OriginDestinationOption']:
                #print each_flight_json
                try:
                    flight = Flight()
                    
                    flight_nums = len(each_flight_json['FlightSegment'])
                    
                    flight.flight_no = each_flight_json['FlightNos'].replace('-','_')
                    flight.dept_id = each_flight_json['AirPorts'][:3]
                    flight.dest_id = each_flight_json['AirPorts'][-3:]
                    
                    #print flight.flight_no,flight.dept_id,flight.dest_id
                    dept_time_tamp = each_flight_json['FlightSegment'][0]['DepartureDate'][6:-2]
                    dest_time_tamp = each_flight_json['FlightSegment'][-1]['ArrivalDate'][6:-2]
                    #flight.dur = int(dest_time_temp) - int(dept_time_temp)
                    #flight.dur = flight.dur / 1000
                    flight_time_json = each_flight_json['FlightSegment']
                    
                    if flight_nums == 1:
                        time_str_temp = flight_time_json[0]['FlyTime'].encode('utf8')
                    
                        str_num = time_str_temp.find('小')
                        if str_num < 0:
                            h_nums_str = time_str_temp[:time_str_temp.find('时')].strip()
                            m_nums_str = time_str_temp[time_str_temp.find('时')+3:time_str_temp.find('分')].strip()
                        else:
                            h_nums_str = time_str_temp[:time_str_temp.find('小时')].strip()
                            m_nums_str = time_str_temp[time_str_temp.find('小时')+6:time_str_temp.find('分')].strip()
                        flight.dur = 0
                        if h_nums_str != '':
                            flight.dur += int(h_nums_str) * 3600
                        if m_nums_str != '':
                            flight.dur += int(m_nums_str) * 60
                    else:
                        flight.dur = 0
                        for i in range(flight_nums):
                            time_str_temp = flight_time_json[i]['FlyTime'].encode('utf8')

                            str_num = time_str_temp.find('小')
                            if str_num > 0:
                                h_nums_str = time_str_temp[:time_str_temp.find('小时')].strip()
                                m_nums_str = time_str_temp[time_str_temp.find('小时')+6:time_str_temp.find('分')].strip()
                            else:
                                h_nums_str = time_str_temp[:time_str_temp.find('时')].strip()
                                m_nums_str = time_str_temp[time_str_temp.find('时')+3:time_str_temp.find('分')].strip()
                            if h_nums_str != '':
                                flight.dur += int(h_nums_str) * 3600
                            if m_nums_str != '':
                                flight.dur += int(m_nums_str) * 60

                        for i in range(1,flight_nums):
                            dept_time_temp = each_flight_json['FlightSegment'][i]['DepartureDate'][6:-2]
                            dest_time_temp = each_flight_json['FlightSegment'][i-1]['ArrivalDate'][6:-2]
                            flight.dur += (int(dept_time_temp) - int(dest_time_temp)) / 1000
                    flight.dept_time = time.strftime('%Y-%m-%d %H:%M:%S', \
                            time.localtime(float(str(dept_time_tamp)[:-3]))).replace(' ','T')
                    flight.dest_time = time.strftime('%Y-%m-%d %H:%M:%S', \
                            time.localtime(float(str(dest_time_tamp)[:-3]))).replace(' ','T')
                    flight.dept_day = flight.dept_time.split('T')[0]
                    flight.source = 'tongcheng::tongcheng'
                    flight.stop = int(flight_nums) - 1
                    #print flight.stop, flight.dept_time, flight.dept_day
                    flight.currency = 'CNY'
                    flight.price = each_flight_json['FareInfo'][0]['TCPrice_Audlt']
                    flight.tax = each_flight_json['FareInfo'][0]['TaxPrice_Audlt']
                    
                    #print flight.price,flight.tax
                    airline_temp = ''
                    plane_no_temp = ''
                    
                    #print each_flight_json['FlightSegment'][0]
        
                    for i in range(flight_nums):
                        plane_no_temp = plane_no_temp + \
                                each_flight_json['FlightSegment'][i]['Equipment'] + '_'
                    
                        airline_temp = airline_temp + \
                                each_flight_json['FlightSegment'][i]['AirCompanyName'] + '_'
                    
                    flight.plane_no = plane_no_temp[:-1]
                    flight.airline = airline_temp[:-1]
                    #print plane_no_temp,airline_temp
                    flight.seat_type = '经济舱'

                    flight_tuple = (flight.flight_no, flight.plane_no, flight.airline, \
                            flight.dept_id, flight.dest_id, flight.dept_day, flight.dept_time, \
                            flight.dest_time, flight.dur, flight.price, flight.tax, \
                            flight.surcharge, flight.currency, flight.seat_type, \
                            flight.source, flight.return_rule, flight.stop)
                    flights.append(flight_tuple)
                except Exception, e:
                    logger.info('tongchengFlight: Parse this flight failed!' + str(e))
                    continue
        else:
            logger.error('tongchengFlight: Crawl this page failed!')
            return flights
    return flights

if __name__ == '__main__':
