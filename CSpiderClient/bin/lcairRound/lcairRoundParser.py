#!/usr/bin/env python
#coding=UTF8

'''
    @author: nemo
    @date: 2014-06-27
    @desc:
        lcairRoundFlight
'''


import re
import time
import sys
import random
import datetime
import json
from common.crawler import UrllibCrawler, MechanizeCrawler
from common.class_common import RoundFlight, EachFlight
from util.crawl_func import request_post_data
from common.logger import logger
from common.common import get_proxy, invalid_proxy
from common.airline_common import Airline

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

def getPostData(dept_id, dest_id, dept_date, return_date):
    
    postdata = None

    try:
        json_str = {}
        json_str['tripType'] = 1
        json_str['airCo'] = 'All'
        json_str['passengerType'] = '0'
        json_str['seatType'] = 'Y'
        json_str['adultCount'] = 1
        json_str['sortType'] = 0
        json_str['fare'] = 0
        json_str['fromDate'] = dept_date

        trip = []

        dept_trip_dict = {}
        return_trip_dict = {}

        dept_trip_dict['date'] = dept_date
        dept_trip_dict['fromCity'] = AIRPORT_CITY_CN_DICT[dept_id]
        dept_trip_dict['toCity'] = AIRPORT_CITY_CN_DICT[dest_id]
        trip.append(dept_trip_dict)

        return_trip_dict['date'] = return_date
        return_trip_dict['fromCity'] = AIRPORT_CITY_CN_DICT[dest_id]
        return_trip_dict['toCity'] = AIRPORT_CITY_CN_DICT[dept_id]
        trip.append(return_trip_dict)

        json_str['trips'] = trip

        postdata = {'json': json.dumps(json_str)}

    except Exception, e:
        return None

    return postdata

def getOneTripInfo(segments):
    
    trips = []

    stop = len(segments) - 1

    if stop == 0:
        for single_flight in segments[0]['flights']:
            trip = {}
            trip['flight_no'] = single_flight['flightNumber']
            try:
                trip['airline'] = Airline[single_flight['airCo']]
            except:
                trip['airline'] = single_flight['airCo']

            trip['plane_no'] = single_flight['equipType']

            trip['dept_time'] = CalDateTime(single_flight['fromDate'], single_flight['fromTime'])
            trip['dest_time'] = CalDateTime(single_flight['toDate'], single_flight['toTime'])
            trip['dur'] = CalDur(single_flight['duration'])
            trip['stop'] = 0

            trips.append(trip)

    elif stop == 1:
        for i in range(0, len(segments[0]['flights'])):
            for j in range(0, len(segments[1]['flights'])):

                single_flight1 = segments[0]['flights'][i]
                single_flight2 = segments[1]['flights'][j]
                trip = {}

                trip['flight_no'] = single_flight1['flightNumber'] + '_' + single_flight2['flightNumber']
                trip['plane_no'] = single_flight1['equipType'] + '_' + single_flight2['equipType']

                try:
                    trip['airline'] = Airline[single_flight1['airCo']] + '_' + Airline[single_flight2['airCo']]
                except:
                    trip['airline'] = single_flight1['airCo'] + '_' + single_flight2['airCo']

                trip['dept_time'] = CalDateTime(single_flight1['fromDate'], single_flight1['fromTime'])
                trip['dest_time'] = CalDateTime(single_flight2['toDate'], single_flight2['toTime'])
                trip['dur'] = CalDur(single_flight1['duration']) + CalDur(single_flight2['duration']) + CalWaitTime(single_flight1['toDate'],single_flight1['toTime'],single_flight2['fromDate'],single_flight2['fromTime'])
                trip['stop'] = 1

                trips.append(trip)

    else:
        pass

    return trips

def lcairRound_page_parser(content):

    flights = {}
    tickets = []

    if content == '' or content == None:
        return tickets, flights
        
    try:
        content_json = json.loads(content)
        all_flights = content_json['routes']
    except Exception, e:
        return tickets, flights

    for flight_info in all_flights:

        roundflight = RoundFlight()

        roundflight.dept_id = flight_info['from']['routeStr'].split('-')[0]
        roundflight.dest_id = flight_info['to']['routeStr'].split('-')[0]

        roundflight.dept_day = flight_info['from']['fromDate']
        roundflight.dest_day = flight_info['to']['fromDate']

        roundflight.seat_type_A = '经济舱'
        roundflight.seat_type_B = '经济舱'
        roundflight.price = flight_info['totalFare']
        roundflight.tax = flight_info['totalTax']

        roundflight.source = 'lcairRound::lcairRound'
        
        segments = flight_info['segments']

        goTripLen = int(flight_info['fromSegmentCount'])

        fromSegments = segments[0:goTripLen-1]
        toSegments = segments[goTripLen:]

        fromTrips = getOneTripInfo(fromSegments)    #[{ },{ }]
        toTrips = getOneTripInfo(toSegments)    #[{ },{ }]
        
        for fromTrip in fromTrips:
            for toTrip in toTrips:
                
                roundflight.flight_no_A, roundflight.airline_A, roundflight.plane_no_A, roundflight.dept_time_A, roundflight.dest_time_A, roundflight.dur_A, roundflight.stop_A = \
                        fromTrip['flight_no'], fromTrip['airline'], fromTrip['plane_no'], fromTrip['dept_time'], fromTrip['dest_time'], fromTrip['dur'], fromTrip['stop']
                roundflight.flight_no_B, roundflight.airline_B, roundflight.plane_no_B, roundflight.dept_time_B, roundflight.dest_time_B, roundflight.dur_B, roundflight.stop_B = \
                        toTrip['flight_no'], toTrip['airline'], toTrip['plane_no'], toTrip['dept_time'], toTrip['dest_time'], toTrip['dur'], toTrip['stop']

                
                #print roundflight.flight_no_A
                #print roundflight.airline_A
                #print roundflight.plane_no_A
                #print roundflight.dept_time_A
                #print roundflight.dest_time_A
                #print roundflight.dur_A
                #print roundflight.stop_A
                #print roundflight.dept_day
                #print roundflight.price
                #print roundflight.dept_id

                roundflight_tuple = (roundflight.dept_id, roundflight.dest_id, roundflight.dept_day, roundflight.dest_day, \
                        roundflight.price, roundflight.tax, roundflight.surcharge, roundflight.currency, roundflight.source, \
                        roundflight.return_rule, roundflight.flight_no_A, roundflight.airline_A, roundflight.plane_no_A, \
                        roundflight.dept_time_A, roundflight.dest_time_A, roundflight.dur_A, roundflight.seat_type_A, \
                        roundflight.stop_A, roundflight.flight_no_B, roundflight.airline_B, roundflight.plane_no_B, \
                        roundflight.dept_time_B, roundflight.dest_time_B, roundflight.dur_B, roundflight.seat_type_B, \
                        roundflight.stop_B)

                tickets.append(roundflight_tuple)

    return tickets, flights
def lcairRound_task_parser(content):

    #初始化参数
    #返回para，改版后返回result
    result = {}
    result['para'] = {'ticket':[], 'flight':{}}
    result['error'] = 0

    try:
        infos = content.strip().split('&')
        dept_id = infos[0]  #机场三字码
        dest_id = infos[1]  #机场三字码
        dept_day = infos[2]
        return_day = infos[3]
        dept_date = dept_day[0:4] + '-' + dept_day[4:6] + '-' + dept_day[6:]
        return_date = return_day[0:4] + '-' + return_day[4:6] + '-' + return_day[6:]

    except Exception,e:
        logger.info('lcairRoundFlight: Wrong Content Format with %s'%content)
        return result

    if AIRPORT_CITY_DICT.has_key(dept_id) == False or AIRPORT_CITY_DICT.has_key(dest_id) == False:
        logger.warning('lcairRoundFlight: airport not in AIRPORT_CITY_DICT')
        result['error'] = DATA_NONE
        return result
    
    p = get_proxy(source = 'lcairRoundFlight')
    if p == None:
        result['error'] = PROXY_NONE
        return result

    postdata = getPostData(dept_id, dest_id, dept_date, return_date)

    if postdata == None:
        result['error'] = UNKNOWN_TYPE
        return result
    
    uc = UrllibCrawler(p = p)
    html = uc.post(SearchURL, postdata, html_flag = True)

    #print html

    tickets, flights = lcairRound_page_parser(html)
    if tickets == []:
        result['error'] = DATA_NONE
        return result

    result['para']['ticket'] = tickets
    result['para']['flight'] = flights 

    return result

def lcairRound_request_parser(content):

    result = -1

    return result

if __name__ == "__main__":

    content = 'PEK&CDG&20140709&20140719'

    result = lcairRound_task_parser(content)

    print result
