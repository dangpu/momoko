#!/usr/bin/env python
#coding=UTF8

'''
    @author: nemo
    @date: 2014-05-17
    @desc:
        feiquanqiuParser
'''

import re
import json
import datetime
from util.crawl_func import crawl_single_page
from util.crawler import UrllibCrawler, MechanizeCrawler
from common.logger import logger
from common.common import get_proxy, invalid_proxy
from common.class_common import Flight, EachFlight

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

#需要填入机场三字码和日期，如北京，巴黎，六月二日，填入PEK, CDG, 06/02/2014
URL = 'http://www.feiquanqiu.com/ticketsearch?departureAirport=%s&destinationAirport=%s&departureDate=%s&returnFromAirport=&returnToAirport=&returnDate=&type=oneway&adults=1&children=0&cabin=E'
REFERER = 'http://www.feiquanqiu.com/ticketsearch?q=search&type=oneway&departureAirport=%s&destinationAirport=%s&departureDate=%s&adults=1&children=0&cabin=E&btn-search=查询'

#iatacode -> city_code:
AIRPORT_CITY_DICT = {'CPH':'CPH','LIN':'MIL','AGB':'AGB','BGO':'BGO','HEL':'HEL','NAP':'NAP','LIS':'LIS','BOD':'BOD','FNI':'FNI','AGP':'AGP','SXB':'SXB',\
                'SXF':'BER','LYS':'LYS','LBA':'LBA','HAJ':'HAJ','HAM':'HAM','MRS':'MRS','BFS':'BFS','LPL':'LPL','LHR':'LON','SVQ':'SVQ','VIE':'VIE','BVA':'PAR',\
                'MAD':'MAD','BRU':'BRU','MAN':'MAN','TSF':'VCE','FLR':'FLR','BER':'BER','RTM':'RTM','VLC':'VLC','SZG':'SZG','OSL':'OSL','AMS':'AMS','BUD':'BUD',\
                'STO':'STO','TRN':'TRN','BLQ':'BLQ','PRG':'PRG','GRX':'GRX','OXF':'OXF','PSA':'PSA','MXP':'MIL','LCY':'LON','INN':'INN','ANR':'ANR','OPO':'OPO',\
                'BCN':'BCN','LUX':'LUX','GLA':'GLA','MUC':'MUC','LUG':'LUG','CGN':'CGN','BSL':'BSL','PMF':'MIL','SEN':'LON','NUE':'NUE','VRN':'VRN','FCO':'ROM',\
                'FRA':'FRA','WAW':'WAW','DUS':'DUS','LTN':'LON','CDG':'PAR','MMX':'MMA','ORY':'PAR','LEJ':'LEJ','EDI':'EDI','BRS':'BRS','BRN':'BRN','BRE':'BRE',\
                'CIA':'ROM','TXL':'BER','VCE':'VCE','STN':'LON','GVA':'GVA','GOA':'GOA','KLV':'KLV','STR':'STR','GOT':'GOT','ZRH':'ZRH','BHD':'BFS','LGW':'LON',\
                'BHX':'BHX','NCL':'NCL','NCE':'NCE','ARN':'STO','PEK':'BJS','PVG':'SHA','SHA':'SHA','NAJ':'BJS'}

def timeshifter(time):

    #06/02/2014 02:30 -> 2014-06-02T02:30

    try:
        origdate, origtime = time.split(' ')[0], time.split(' ')[1]

        date = origdate.split('/')[2] + '-' + origdate.split('/')[0] + '-' + origdate.split('/')[1]
        time = origtime + ':00'

        return date + 'T' + time

    except Exception,e :
        return None


def getPage(url, proxy = None):
    

    for i in range(2):
        page = crawl_single_page(url, proxy = proxy, n = 1)

        if len(page) > 100:
            return page

    return None

def parsePage(page):

    #找到页面但没有航班
    #if page.find('对不起，没有符合您要求的航班，或座位已经售罄。请再试一次') != -1:
        #return None

    try:
        all_info = json.loads(page)
    except Exception, e:
        return [], {}

    if 'APIError' in all_info.keys():
        return [],{}
    
    flights = []
    singleFlights = {}
    
    #找到航班列表
    if 'airTicketListResponse' in all_info.keys():

        currency = all_info['airTicketListResponse']['currency']
        source = 'feiquanqiu::feiquanqiu'

        flight_infos = all_info['airTicketListResponse']['routings']

        for flight_info in flight_infos:
            flight = Flight()
            flight_aircorp = ''
            flight_plane = ''
            flight_no = ''

            flight.price = int(float(flight_info['adultSalesPrice']) + 1)#解析出数据是小数，取int加1
            flight.tax = int(float(flight_info['adultTax']) + 1)
            flight.dur = int(flight_info['tripTime']) * 60

            segments = flight_info['trips'][0]['segments']
            
            flight.dept_id = segments[0]['departureAirportCode']
            flight.dest_id = segments[-1]['arrivalAirportCode']
            flight.dept_time = timeshifter(segments[0]['departureTime'])
            flight.dest_time = timeshifter(segments[-1]['arrivalTime'])
            flight.dept_day = flight.dept_time.split('T')[0]

            flight.currency = currency
            flight.seat_type = '经济舱'
            flight.stop = len(segments) - 1

            flight.source = source

            for segment in segments:
                flight_aircorp += segment['airlineName'] + '_'
                flight_plane += segment['aircraftCode'].split(' ')[-1] + '_' #Airbus A330 -> A330
                flight_no += segment['airlineCode'] + segment['flightNumber'] + '_' #拼接航空公司代码和航班代码

                singleflight = EachFlight()
                singleflight.flight_no = segment['airlineCode'] + segment['flightNumber']
                singleflight.plane_no = segment['aircraftCode']
                singleflight.airline = segment['airlineName']
                singleflight.dept_id = segment['departureAirportCode']
                singleflight.dest_id = segment['arrivalAirportCode']
                singleflight.dept_time = timeshifter(segment['departureTime'])
                singleflight.dest_time = timeshifter(segment['arrivalTime'])
                singleflight.dur = int(segment['duration'] * 60)

                singleflight.flight_key = singleflight.flight_no + '_' + singleflight.dept_id + '_' + singleflight.dest_id
                singleflight_tuple = (singleflight.flight_no, singleflight.airline, singleflight.plane_no, singleflight.dept_id, singleflight.dest_id, \
                        singleflight.dept_time, singleflight.dest_time, singleflight.dur)

                singleFlights[singleflight.flight_key] = singleflight_tuple

            flight.flight_no = flight_no[:-1]
            flight.plane_no = flight_plane[:-1]
            flight.airline = flight_aircorp[:-1]

            flights.append(flight)
        
        return flights, singleFlights

    return None, None
    

def feiquanqiu_task_parser(content):
    
    #初始化参数
    #返回para，改版后返回result
    result = {}
    result['para'] = {'ticket':[], 'flight':{ } }
    result['error'] = 0

    #解析字符串
    try:
        infos = content.strip().split('&')
        dept_id = infos[0]
        dest_id = infos[1]
        day, month, year = infos[2][6:], infos[2][4:6], infos[2][0:4]
        dept_date = month + '/' + day + '/' + year
    except Exception, e:
        logger.error('feiquanqiuFlight: Wrong Content Format with %s'%content)
        result['error'] = TASK_ERROR
        return result

    url = URL%(dept_id, dest_id, dept_date)
    referer = REFERER%(dept_id, dest_id, dept_date)
    
    #取代理
    p = get_proxy(source='feiquanqiuFlight')
    if p == None:
        result['error'] = PROXY_NONE
        return result
    
    #解析页面
    mc = MechanizeCrawler(p = p, referer = referer)

    page = mc.get(url, html_flag = True)

    if page == None:
        logger.info('feiquanqiuFlight: htmlcontent is null with %s'%p)
        result['error'] = PROXY_INVALID
        return result

    flights, singleFlights = parsePage(page)
    
    if flights == None:
        result['error'] = DATA_NONE
        return result
    
    paras = []
    for flight in flights:
        single = (flight.flight_no,flight.plane_no,flight.airline,flight.dept_id,flight.dest_id,\
                flight.dept_day,flight.dept_time,flight.dest_time,flight.dur,flight.price,\
                flight.tax,flight.surcharge,flight.currency,flight.seat_type,flight.source,\
                flight.return_rule,flight.stop)
        paras.append(single)
    #logger.info('feiqianqiuFlight: find %s flight with %s - %s'%(len(flights), dept_id, dest_id))
    
    result['para']['ticket'] = paras
    result['para']['flight'] = singleFlights
    return result

def feiquanqiu_request_parser(content):

    #初始化参数
    result = -1
    #解析字符串
    try:
        infos = content.strip().split('|')
        flight_info = infos[0].strip()
        time_info = infos[1].strip()
        ticketsource = infos[2].strip()

        flight_no = flight_info.split('-')[0]
        dept_id,dest_id = flight_info.split('-')[1],flight_info.split('-')[2]
        dept_day,dept_hour = time_info.split('_')[0],time_info.split('_')[1]

        dept_time = dept_day[0:4] + '-' + dept_day[4:6] + '-' + dept_day[6:] + 'T' + dept_hour + ':00'
        dept_date = dept_day[4:6] + '/' + dept_day[6:] + '/' + dept_day[0:4]

    except Exception,e:
        logger.error('wegoFlight Content Error: cannot extract information from %s'%content)
        return result

    #解析页面

    url = URL%(dept_id, dest_id, dept_date)

    page = getPage(url,proxy = None)
    if page == None:
        return result

    flights, no_use_para = parsePage(page)
    if flights == None:
        return result

    for flight in flights:
        if flight.dept_time == dept_time and flight.flight_no == flight_no:
            return flight.price
        else:
            continue

    return result
    
if __name__ == "__main__":

    taskcontent = 'PVG&FCO&20140802'
    requestcontent = 'SU205_SU4456-PEK-CDG|20140622_11:40|feiquanqiu::feiquanqiu'

    taskresult = feiquanqiu_task_parser(taskcontent)

    print str(taskresult)

    #requestresult = feiquanqiu_request_parser(requestcontent)

    #print str(requestresult)
