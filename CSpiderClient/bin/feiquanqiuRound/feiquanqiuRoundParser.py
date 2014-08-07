#!/usr/bin/env python
#coding=UTF8

'''
    @author: nemo
    @date: 2014-06-14
    @desc:
        feiquanqiuRoundParser
'''

import random
import time
import datetime
import json
from common.class_common import RoundFlight
from common.class_common import EachFlight
from common.logger import logger
from util.crawl_func import crawl_single_page
from common.common import get_proxy, invalid_proxy
from util.crawler import UrllibCrawler, MechanizeCrawler

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

URL = 'http://www.feiquanqiu.com/ticketsearch?departureAirport=%s&destinationAirport=%s&departureDate=%s&returnFromAirport=&returnToAirport=&returnDate=%s&type=roundtrip&adults=1&children=0&cabin=E'

REFERER = 'http://www.feiquanqiu.com/ticketsearch?q=search&type=roundtrip&departureAirport=%s&destinationAirport=%s&departureDate=%s&returnDate=%s&adults=1&children=0&cabin=E'
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
        return []
    
    if 'APIError' in all_info.keys():
        return []

    flights = []

    if 'airTicketListResponse' in all_info.keys():
        currency = all_info['airTicketListResponse']['currency']
        source = 'feiquanqiuRound::feiquanqiuRound'

        flight_infos = all_info['airTicketListResponse']['routings']

        for flight_info in flight_infos:
            roundflight = RoundFlight()

            roundflight_airport = ''
            roundflight_plane = ''
            roundflight_no = ''

            roundflight.price = int(float(flight_info['adultSalesPrice']) + 1)#解析出数据是小数，取int加1
            roundflight.tax = int(float(flight_info['adultTax']) + 1)
            #roundflight.dur = int(flight_info['tripTime']) * 60

            go_info = segments = flight_info['trips'][0]
            return_info = segments = flight_info['trips'][1]

            go_segments = go_info['segments']
            return_segments = return_info['segments']

            roundflight.dept_id = go_segments[0]['departureAirportCode']
            roundflight.dest_id = return_segments[0]['departureAirportCode']

            dept_time = timeshifter(go_segments[0]['departureTime'])
            dest_time = timeshifter(return_segments[0]['departureTime'])

            roundflight.dept_day = dept_time.split('T')[0]
            roundflight.dest_day = dest_time.split('T')[0]

            #roundflight.seat_type = '经济舱'
            roundflight.currency = currency
            roundflight.source = source
            
            flight_aircorp = ''
            flight_plane = ''
            flight_no = ''

            for segment in go_segments:
                flight_aircorp += segment['airlineName'] + '_'
                flight_plane += segment['aircraftCode'].split(' ')[-1] + '_' #Airbus A330 -> A330
                flight_no += segment['airlineCode'] + segment['flightNumber'] + '_' #拼接航空公司代码和航班代码

            roundflight.flight_no_A = flight_no[:-1]
            roundflight.plane_no_A = flight_plane[:-1]
            roundflight.airline_A = flight_aircorp[:-1]

            for segment in return_segments:
                flight_aircorp += segment['airlineName'] + '_'
                flight_plane += segment['aircraftCode'].split(' ')[-1] + '_' #Airbus A330 -> A330
                flight_no += segment['airlineCode'] + segment['flightNumber'] + '_' #拼接航空公司代码和航班代码

            roundflight.flight_no_B = flight_no[:-1]
            roundflight.plane_no_B = flight_plane[:-1]
            roundflight.airline_B = flight_aircorp[:-1]

            roundflight.dept_time_A = timeshifter(go_segments[0]['departureTime'])
            roundflight.dest_time_A = timeshifter(go_segments[-1]['arrivalTime'])

            roundflight.dept_time_B = timeshifter(return_segments[0]['departureTime'])
            roundflight.dest_time_B = timeshifter(return_segments[-1]['arrivalTime'])

            roundflight.seat_type_A = '经济舱'
            roundflight.seat_type_B = '经济舱'

            roundflight.dur_A = go_info['tripTime'] * 60
            roundflight.dur_B = return_info['tripTime'] * 60

            roundflight.stop_A = len(go_segments) - 1
            roundflight.stop_B = len(return_segments) - 1
        
            flights.append(roundflight)

        return flights
    
    return None

def feiquanqiu_task_parser(content):

    result = {}
    result['para'] = []
    result['error'] = 0

    try:
        infos = content.strip().split('&')
        dept_id = infos[0]
        dest_id = infos[1]
        day, month, year = infos[2][6:], infos[2][4:6], infos[2][0:4]
        dept_date = month + '/' + day + '/' + year
        rday, rmonth, ryear = infos[3][6:], infos[3][4:6], infos[3][0:4]
        dest_date = rmonth + '/' + rday + '/' + ryear

    except Exception, e:
        logger.error('feiquanqiuRoundFlight: Wrong Content Format with %s'%content)
        result['error'] = TASK_ERROR
        return result

    url = URL%(dept_id, dest_id, dept_date, dest_date)
    referer = REFERER%(dept_id, dest_id, dept_date, dest_date)

    p = get_proxy(source='feiquanqiuRoundFlight')
    if p == None:
        result['error'] = PROXY_NONE
        return result
    
    mc = MechanizeCrawler(p=p, referer=referer)

    page = mc.get(url, html_flag = True)
    if page == None:
        logger.info('feiquanqiuRoundFlight: htmlcontent is null with %s'%p)
        result['error'] = PROXY_INVALID
        return result

    flights = parsePage(page)
    if flights == None:
        result['error'] = DATA_NONE
        return result

    paras = []
    for roundflight in flights:
        roundflight_tuple = (roundflight.dept_id, roundflight.dest_id, roundflight.dept_day, roundflight.dest_day, \
                roundflight.price, roundflight.tax, roundflight.surcharge, roundflight.currency, roundflight.source, \
                roundflight.return_rule, roundflight.flight_no_A, roundflight.airline_A, roundflight.plane_no_A, \
                roundflight.dept_time_A, roundflight.dest_time_A, roundflight.dur_A, roundflight.seat_type_A, \
                roundflight.stop_A, roundflight.flight_no_B, roundflight.airline_B, roundflight.plane_no_B, \
                roundflight.dept_time_B, roundflight.dest_time_B, roundflight.dur_B, roundflight.seat_type_B, \
                roundflight.stop_B)
        paras.append(roundflight_tuple)

    result['para'] = paras
    return result

def feiquanqiu_request_parser(content):

    result = -1
    '''
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
        logger.error('jijitongRoundFlight Content Error: cannot extract information from %s'%content)
        return result
    '''
    return result

if __name__ == "__main__":

    taskcontent = 'PEK&CDG&20140722&20140802'

    taskresult = feiquanqiu_task_parser(taskcontent)
    print str(taskresult)

