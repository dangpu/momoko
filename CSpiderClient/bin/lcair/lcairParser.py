#!/usr/bin/env python
#coding=UTF8

'''
    @author: nemo
    @date: 2014-06-26
    @desc:
        lcairParser
'''

import re
import time
import sys
import random
import datetime
import json
from common.crawler import UrllibCrawler, MechanizeCrawler
from common.class_common import Flight, EachFlight
from util.crawl_func import request_post_data
from common.logger import logger
from common.common import get_proxy, invalid_proxy
from common.airline_common import Airline

reload(sys)
sys.setdefaultencoding='utf8'

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

AIRPORT_CITY_CN_DICT = {'CPH': '哥本哈根', 'LIN': '米兰', 'AGB': '奥格斯堡', 'BGO': '卑尔根', 'HEL': '赫尔辛基', \
        'NAP': '那不勒斯', 'LIS': '里斯本', 'NAY': '北京', 'BOD': '波尔多', 'FNI': '尼姆', 'AGP': '马拉加', \
        'PEK': '北京', 'SXB': '斯特拉斯堡', 'SXF': '柏林', 'LYS': '里昂', 'LBA': '利兹', 'HAJ': '汉诺威', \
        'HAM': '汉堡', 'MRS': '马赛', 'BFS': '贝尔法斯特', 'LPL': '利物浦', 'LHR': '伦敦', 'SVQ': '塞维利亚', \
        'VIE': '维也纳', 'BVA': '巴黎', 'MAD': '马德里', 'LEJ': '莱比锡', 'MAN': '曼彻斯特', 'TSF': '威尼斯', \
        'FLR': '佛罗伦萨', 'BER': '柏林', 'RTM': '鹿特丹', 'VLC': '瓦伦西亚', 'SZG': '萨尔茨堡', 'OSL': '奥斯陆', \
        'AMS': '阿姆斯特丹', 'BUD': '布达佩斯', 'STO': '斯德哥尔摩', 'TRN': '都灵', 'BLQ': '博洛尼亚', \
        'PRG': '布拉格', 'GRX': '格拉纳达', 'SHA': '上海', 'OXF': '牛津', 'PSA': '比萨', 'MXP': '米兰', 'LCY': '伦敦', \
        'INN': '因斯布鲁克', 'ANR': '安特卫普', 'OPO': '波尔图', 'BCN': '巴塞罗那', 'LUX': '卢森堡', \
        'GLA': '格拉斯哥', 'MUC': '慕尼黑', 'LUG': '卢加诺', 'CGN': '科隆', 'BSL': '巴塞尔', 'PMF': '米兰', \
        'PVG': '上海', 'SEN': '伦敦', 'NUE': '纽伦堡', 'VRN': '维罗纳', 'FCO': '罗马', 'FRA': '法兰克福', \
        'WAW': '华沙', 'DUS': '杜塞尔多夫', 'LTN': '伦敦', 'CDG': '巴黎', 'MMX': '马尔默', 'ORY': '巴黎', \
        'BRU': '布鲁塞尔', 'EDI': '爱丁堡', 'BRS': '布里斯托尔', 'BRN': '伯尔尼', 'BRE': '不莱梅', \
        'CIA': '罗马', 'TXL': '柏林', 'VCE': '威尼斯', 'STN': '伦敦', 'GVA': '日内瓦', 'GOA': '热那亚', \
        'KLV': '卡罗维发利', 'STR': '斯图加特', 'GOT': '哥德堡', 'ZRH': '苏黎世', 'BHD': '贝尔法斯特', \
        'NCE': '尼斯', 'BHX': '伯明翰', 'NCL': '纽卡斯尔', 'LGW': '伦敦', 'ARN': '斯德哥尔摩'}

AIRPORT_CITY_DICT = {'CPH':'CPH','LIN':'MIL','AGB':'AGB','BGO':'BGO','HEL':'HEL','NAP':'NAP','LIS':'LIS','BOD':'BOD','FNI':'FNI','AGP':'AGP','SXB':'SXB',\
        'SXF':'BER','LYS':'LYS','LBA':'LBA','HAJ':'HAJ','HAM':'HAM','MRS':'MRS','BFS':'BFS','LPL':'LPL','LHR':'LON','SVQ':'SVQ','VIE':'VIE','BVA':'PAR',\
        'MAD':'MAD','BRU':'BRU','MAN':'MAN','TSF':'VCE','FLR':'FLR','BER':'BER','RTM':'RTM','VLC':'VLC','SZG':'SZG','OSL':'OSL','AMS':'AMS','BUD':'BUD',\
        'STO':'STO','TRN':'TRN','BLQ':'BLQ','PRG':'PRG','GRX':'GRX','OXF':'OXF','PSA':'PSA','MXP':'MIL','LCY':'LON','INN':'INN','ANR':'ANR','OPO':'OPO',\
        'BCN':'BCN','LUX':'LUX','GLA':'GLA','MUC':'MUC','LUG':'LUG','CGN':'CGN','BSL':'BSL','PMF':'MIL','SEN':'LON','NUE':'NUE','VRN':'VRN','FCO':'ROM',\
        'FRA':'FRA','WAW':'WAW','DUS':'DUS','LTN':'LON','CDG':'PAR','MMX':'MMA','ORY':'PAR','LEJ':'LEJ','EDI':'EDI','BRS':'BRS','BRN':'BRN','BRE':'BRE',\
        'CIA':'ROM','TXL':'BER','VCE':'VCE','STN':'LON','GVA':'GVA','GOA':'GOA','KLV':'KLV','STR':'STR','GOT':'GOT','ZRH':'ZRH','BHD':'BFS','LGW':'LON',\
        'BHX':'BHX','NCL':'NCL','NCE':'NCE','ARN':'STO','PEK':'BJS','PVG':'SHA','SHA':'SHA','NAY':'BJS','CAN':'CAN','SZX':'SZX'}

Referer = 'http://www.lcair.com/search.php?fromCity=%s(%s)&toCity=%s(%s)&fromDate=%s&returnDate='
SearchURL = 'http://www.lcair.com/service/search.php?t=lcair2013'

def CalDur(dur_str):
    
    during = -1

    try:
        during = int(dur_str.split(':')[0]) * 3600 + int(dur_str.split(':')[1]) * 60
    except Exception,e:
        pass

    return during

def CalDateTime(date_str, time_str):

    date_time = 'NULL'
    try:
        date_time = date_str + 'T' + time_str[0:2] + ':' + time_str[2:] + ':00'
    except Exception,e:
        pass

    return date_time

def CalWaitTime(date0, time0, date1, time1):

    try:
        days = (datetime.datetime(int(date1[0:4]), int(date1[5:7]), int(date1[8:])) - datetime.datetime(int(date0[0:4]), int(date0[5:7]), int(date0[8:]))).days

        hours = int(time1[0:2]) - int(time0[0:2])

        minutes = int(time1[2:]) - int(time0[2:])

        waittime = days * 86400 + hours * 3600 + minutes * 60

        return waittime
    except Exception, e:
        return None

def getPostData(dept_id, dest_id, dept_date):
    
    postdata = None

    try:
        json_str = {}
        json_str['tripType'] = 0
        json_str['airCo'] = 'All'
        json_str['passengerType'] = '0'
        json_str['seatType'] = 'Y'
        json_str['adultCount'] = 1
        json_str['sortType'] = 0
        json_str['fare'] = 0
        json_str['fromDate'] = dept_date

        trip = []
        trip_dict = {}
        trip_dict['date'] = dept_date
        trip_dict['fromCity'] = AIRPORT_CITY_CN_DICT[dept_id]
        trip_dict['toCity'] = AIRPORT_CITY_CN_DICT[dest_id]
        trip.append(trip_dict)

        json_str['trips'] = trip

        postdata = {'json': json.dumps(json_str)}
    except Exception, e:
        return None

    return postdata

def lcair_page_parser(content):

    flights = {}
    tickets = []

    if content == '' or content == None:
        return tickets, flights
    
    try:
        content_json = json.loads(content)
        all_flights = content_json['routes']
    except Exception,e:
        return tickets, flights

    for flight_info in all_flights:

        segments = flight_info['segments']

        flight = Flight()

        flight.currency = flight_info['coinType']
        flight.price = int(flight_info['totalFare'])
        flight.tax = int(flight_info['totalTax'])

        flight.seat_type = '经济舱'

        flight.stop = int(flight_info['transfer'])
        if flight.stop > 1:
            print 'found a flight whose transfer_times > 1'
            continue

        flight.source = 'lcair::lcair'

        flight.dept_id, flight.dest_id = flight_info['routeStr'].split('-')[0], flight_info['routeStr'].split('-')[-1]

        flight.dept_day = flight_info['fromDate']

        flight.flight_no = ''
        flight.airline = ''
        flight.plane_no = ''

        flight_dur = 0
        
        #direct
        if flight.stop == 0:
            for single_flight in segments[0]['flights']:
                flight.flight_no = single_flight['flightNumber']
                try:
                    flight.airline = Airline[single_flight['airCo']]
                except:
                    flight.airline = single_flight['airCo']

                flight.plane_no = single_flight['equipType']
                flight.dept_time = CalDateTime(single_flight['fromDate'], single_flight['fromTime'])
                flight.dest_time = CalDateTime(single_flight['toDate'], single_flight['toTime'])
                flight.dur = CalDur(single_flight['duration'])

                flight_tuple = (flight.flight_no,flight.plane_no,flight.airline,flight.dept_id,flight.dest_id,flight.dept_day,\
                        flight.dept_time,flight.dest_time,flight.dur,flight.price,flight.tax,flight.surcharge,\
                        flight.currency,flight.seat_type,flight.source,flight.return_rule,flight.stop)

                tickets.append(flight_tuple)

        elif flight.stop == 1:
            for i in range(0, len(segments[0]['flights'])):
                for j in range(0, len(segments[1]['flights'])):

                    single_flight1 = segments[0]['flights'][i]
                    single_flight2 = segments[1]['flights'][j]

                    flight.flight_no = single_flight1['flightNumber'] + '_' + single_flight2['flightNumber']
                    flight.plane_no = single_flight1['equipType'] + '_' + single_flight2['equipType']

                    try:
                        flight.airline = Airline[single_flight1['airCo']] + '_' + Airline[single_flight2['airCo']]
                    except:
                        flight.airline = str(single_flight1['airCo']) + '_' + str(single_flight2['airCo'])
                    flight.dept_time = CalDateTime(single_flight1['fromDate'], single_flight1['fromTime'])
                    flight.dest_time = CalDateTime(single_flight2['toDate'], single_flight2['toTime'])
                    flight.dur = CalDur(single_flight1['duration']) + CalDur(single_flight2['duration']) + CalWaitTime(single_flight1['toDate'],single_flight1['toTime'],single_flight2['fromDate'],single_flight2['fromTime'])

                    flight_tuple = (flight.flight_no,flight.plane_no,flight.airline,flight.dept_id,flight.dest_id,flight.dept_day,\
                            flight.dept_time,flight.dest_time,flight.dur,flight.price,flight.tax,flight.surcharge,\
                            flight.currency,flight.seat_type,flight.source,flight.return_rule,flight.stop)
                    tickets.append(flight_tuple)

        for segment in segments:
            route_flights = segment['flights']

            for single_flight in route_flights:
                each_flight = EachFlight()

                each_flight.flight_no = single_flight['flightNumber']
                try:
                    each_flight.airline = Airline[single_flight['airCo']]
                except:
                    each_flight.airline = single_flight['airCo']
                each_flight.plane_no = single_flight['equipType']
                each_flight.dept_id = single_flight['fromAirport']
                each_flight.dest_id = single_flight['toAirport']
                each_flight.dept_time = CalDateTime(single_flight['fromDate'], single_flight['fromTime'])
                each_flight.dest_time = CalDateTime(single_flight['toDate'], single_flight['toTime'])
                each_flight.dur = CalDur(single_flight['duration'])

                #print '--------'
                #print each_flight.flight_no
                #print each_flight.airline
                #print each_flight.plane_no
                #print each_flight.dept_id, each_flight.dest_id, each_flight.dept_time, each_flight.dest_time, each_flight.dur

                each_flight.flight_key = each_flight.flight_no + '_' + each_flight.dept_id + '_' + each_flight.dest_id

                flights[each_flight.flight_key] = (each_flight.flight_no, each_flight.airline, \
                        each_flight.plane_no, each_flight.dept_id, each_flight.dest_id, \
                        each_flight.dept_time, each_flight.dest_time, each_flight.dur)


    return tickets, flights


def lcair_task_parser(content):


    #初始化参数
    #返回para，改版后返回result
    result = {}
    result['para'] = {'ticket':[], 'flight':{ } }
    result['error'] = 0

    try:
        infos = content.strip().split('&')
        dept_id = infos[0]  #机场三字码
        dest_id = infos[1]  #机场三字码
        dept_day = infos[2]
        dept_date = dept_day[0:4] + '-' + dept_day[4:6] + '-' + dept_day[6:]
    except Exception, e:
        logger.error('lcairFlight: Wrong Content Format with %s'%content)
        result['error'] = TASK_ERROR
        return result

    if AIRPORT_CITY_DICT.has_key(dept_id) == False or AIRPORT_CITY_DICT.has_key(dest_id) == False:
        logger.warning('ceairFlight: airport not in AIRPORT_CITY_DICT')
        logger.info(dept_id)
        logger.info(dest_id)
        result['error'] = DATA_NONE
        return result

    p = get_proxy(source = 'lcairFlight')

    if p == None:
        result['error'] = PROXY_NONE
        return result
    
    postdata = getPostData(dept_id, dest_id, dept_date)

    if postdata == None:
        result['error'] = UNKNOWN_TYPE
        return result

    #referer = Referer%(AIRPORT_CITY_CN_DICT[dept_id], AIRPORT_CITY_DICT[dept_id], AIRPORT_CITY_CN_DICT[dest_id], AIRPORT_CITY_DICT[dest_id], dept_date)

    uc = UrllibCrawler(p = p)
    #uc.get(referer)
    html = uc.post(SearchURL, postdata, html_flag = True)

    #print html

    tickets, flights = lcair_page_parser(html)
    if tickets == []:
        result['error'] = DATA_NONE
        return result

    result['para']['ticket'] = tickets
    result['para']['flight'] = flights 

    return result

def lcair_request_parser(content):

    result = -1

    return result

if __name__ == "__main__":

    content = 'PEK&CDG&20140709'

    result = lcair_task_parser(content)

    print result
