#! /usr/bin/env python
#coding=UTF8

import sys
from util.crawl_func import crawl_single_page
import cookielib
import urllib
import urllib2
import time
import re
import json
from common.logger import logger
from common.class_common import RoundFlight, EachFlight
import time
import datetime
from common.airline_common import Airline
from common.common import get_proxy, invalid_proxy

reload(sys)
sys.setdefaultencoding('utf-8')
#pattern
search_pattern = re.compile(r'URL=/pages/selquote.aspx\?SesnID=(.*?)&SearchId=(.*?)">', re.S)

URL = 'http://www.smartfares.com/Handlers/FlightQuotes.ashx?SearchId=%s&SystemSiteID=14'
HOST = 'http://www.smartfares.com'
airline_dict = Airline

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

CONTENT_LEN = 100

def smartfares_task_parser(taskcontent):
    result = {}
    flights = {}
    tickets = []
    result['para'] = {'flight':flights, 'ticket':tickets}
    result['error'] = 0

    taskcontent = taskcontent.encode('utf-8')
    try:
        dept_id, dest_id, dept_day, dest_day = taskcontent.strip().split('&')[0], \
            taskcontent.strip().split('&')[1], taskcontent.strip().split('&')[2], \
            taskcontent.strip().split('&')[3]
    except:
        logger.error('smartfaresFlight::Wrong Content Format with %s'%taskcontent)
        result['error'] = TASK_ERROR
        return result

    p = get_proxy(source='smartfaresFlight')
    #p= None
    if p == None:
        result['error'] = PROXY_NONE
        return result

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    try:
        search_url = get_search_url(dept_day,dest_day,dept_id,dest_id)
        content = crawl_single_page(search_url, proxy=p, referer=HOST)
        search_id = get_search_id(content)
        if search_id == '' or search_id == None:
            logger.error('smartfares::Parse search id failed')
            result['error'] = PROXY_INVALID
            return result
    except:
        logger.error('smartfares::Parse search id failed')
        result['error'] = PROXY_INVALID
        return result

    url_real = URL%search_id
    i = 0
    content_len = 0
    while i < 3 and content_len < CONTENT_LEN:
        content_real = crawl_single_page(url=url_real, proxy=p, referer=search_url)
        content_len = len(content_real)
        i += 1

    if len(content_real) > 100:
        parser_result = parsePage(content_real)
        tickets = parser_result['ticket']
        flights = parser_result['flight']
        result['para'] = {'flight':flights, 'ticket':tickets}
        return result
    else:
        result['error'] = DATA_NONE
        return result


def smartfares_request_parser(taskcontent):

    result = -1

    return result


def get_search_url(dept_day, dest_day, dept_id, dest_id):
    dept_day1 = dept_day[0:4]
    dept_day2 = dept_day[4:6]
    dept_day3 = dept_day[6:8]

    dest_day1 = dest_day[0:4]
    dest_day2 = dest_day[4:6]
    dest_day3 = dest_day[6:8]

    search_url = 'http://www.smartfares.com/?Type=2&Adult=1&Child=0&Lap=0' + \
                 '&Date0=' + dept_day2 + '/' + dept_day3 + '/' + dept_day1 + \
                 '&DestCity0=' + dest_id + '&OrigCity0=' + dept_id + \
                 '&Date1=' + dest_day2 + '/' + dest_day3 + '/' + dest_day1 + \
                 '&Airline=&Cabin=Y'

    return search_url


def get_search_id(content):
    try:
        search_id = search_pattern.findall(content)[0][1]
        return search_id
    except Exception, e:
        return None


def parsePage(content):
    result = {}
    tickets = []
    flights = {}

    try:
        flight_json = json.loads(content)
        flight_json_list = flight_json[1]
        if len(flight_json_list) <= 0:
            logger.error('Loading json content failed withed error: ' + str(e))
            result['flight'] = flights
            result['ticket'] = tickets
            return result

    except Exception, e:
        logger.error('Loading json content failed withed error: ' + str(e))
        result['flight'] = flights
        result['ticket'] = tickets
        return result

    for each_flight_json in flight_json[1]:
        roundflight = RoundFlight()
        try:

            roundflight.price = int(each_flight_json[0]) + 1
            roundflight.tax = int(each_flight_json[3]) + 1 - roundflight.price

            outbound_info_list = each_flight_json[5][0]
            inbound_info_list = each_flight_json[5][1]
            
            roundflight.dur_A = int(outbound_info_list[5]) * 60
            roundflight.dur_B = int(inbound_info_list[5]) * 60
            roundflight.dept_id = outbound_info_list[1]
            roundflight.dest_id = outbound_info_list[3]
            
            roundflight.dept_day = day_calculator(outbound_info_list[4])
            roundflight.dest_day = day_calculator(inbound_info_list[4])
            
            #parse dept_time and dest_time of each_flight
            dept_time_A_day = outbound_info_list[4]
            dept_time_A_day = day_calculator(dept_time_A_day)
            dept_time_A_mins = int(outbound_info_list[7][0][5])
            roundflight.dept_time_A = time_calculator(dept_time_A_day, dept_time_A_mins)

            dest_time_A_day = outbound_info_list[7][-1][6]
            dest_time_A_day = day_calculator(dest_time_A_day)
            dest_time_A_mins = int(outbound_info_list[7][-1][7])
            roundflight.dest_time_A = time_calculator(dest_time_A_day, dest_time_A_mins)

            dept_time_B_day = inbound_info_list[4]
            dept_time_B_day = day_calculator(dept_time_B_day)
            dept_time_B_mins = int(inbound_info_list[7][0][5])
            roundflight.dept_time_B = time_calculator(dept_time_B_day, dept_time_B_mins)

            dest_time_B_day = inbound_info_list[7][-1][6]
            dest_time_B_day = day_calculator(dest_time_B_day)
            dest_time_B_mins = int(outbound_info_list[7][-1][7])
            roundflight.dest_time_B = time_calculator(dest_time_B_day, dest_time_B_mins)

            flight_no_A = ''
            airline_A = ''
            plane_no_A = ''

            for each_flight_content in outbound_info_list[7]:

                each_flight_dict = eachflightParser(each_flight_content)
                if each_flight_dict != {}:
                    flights.update(each_flight_dict)

                flight_no_A += each_flight_content[2] + each_flight_content[10] + '_'
                plane_no_A += each_flight_content[12] + '_'
                airline_A += airline_dict[each_flight_content[2]] + '_'

            roundflight.plane_no_A = plane_no_A[:-1]
            roundflight.flight_no_A = flight_no_A[:-1]
            roundflight.airline_A = airline_A[:-1]
            roundflight.stop_A = len(outbound_info_list[7]) - 1
            roundflight.stop_B = len(inbound_info_list[7]) - 1

            flight_no_B = ''
            airline_B = ''
            plane_no_B = ''

            for each_flight_content in inbound_info_list[7]:

                each_flight_dict = eachflightParser(each_flight_content)
                if each_flight_dict != {}:
                    flights.update(each_flight_dict)

                flight_no_B += each_flight_content[2] + each_flight_content[10] + '_'
                airline_B += airline_dict[each_flight_content[2]] + '_'
                plane_no_B += each_flight_content[12] + '_'

            roundflight.plane_no_B = plane_no_B[:-1]
            roundflight.flight_no_B = flight_no_B[:-1]
            roundflight.airline_B = airline_B[:-1]


            if roundflight.airline_A[0] == '_' or roundflight.plane_no_A[0] == '_' or \
                    roundflight.airline_B[0] == '_' or roundflight.plane_no_B[0] == '_':
                continue


            roundflight.source = 'smartfares::smartfares'
            roundflight.seat_type_A = '经济舱'
            roundflight.seat_type_B = '经济舱'
            roundflight.currency = 'USD'

            each_ticket_tuple = (roundflight.dept_id, roundflight.dest_id, roundflight.dept_day, \
                    roundflight.dest_day, roundflight.price, roundflight.tax, roundflight.surcharge, \
                    roundflight.currency, roundflight.source, roundflight.return_rule, roundflight.flight_no_A, \
                    roundflight.airline_A, roundflight.plane_no_A, roundflight.dept_time_A, \
                    roundflight.dest_time_A, roundflight.dur_A, roundflight.seat_type_A, roundflight.stop_A, \
                    roundflight.flight_no_B, roundflight.airline_B, roundflight.plane_no_B, \
                    roundflight.dept_time_B, roundflight.dest_time_B, roundflight.dur_B, \
                    roundflight.seat_type_B, roundflight.stop_B)
            print each_ticket_tuple
            tickets.append(each_ticket_tuple)
        except Exception, e:
            print str(e)
            continue


    result['flight'] = flights
    result['ticket'] = tickets
    return result


def eachflightParser(each_flight_content):
    eachflight = EachFlight()

    #print each_flight_content
    each_flight_dict = {}
    try:
        eachflight.flight_no = each_flight_content[2] + each_flight_content[10]
        eachflight.dept_id = each_flight_content[0]
        eachflight.dest_id = each_flight_content[1]
        eachflight.flight_key = eachflight.flight_no + '_' + eachflight.dept_id + \
            '_' + eachflight.dest_id

        eachflight.plane_no = each_flight_content[12]

        try:
            eachflight.airline = airline_dict[each_flight_content[2]]
        except:
            logger.info('[AIRLINEERRORCODE]' + each_flight_content[2])
            return each_flight_dict

        dept_time_day = each_flight_content[4]
        dept_time_mins = each_flight_content[5]
        dest_time_day = each_flight_content[6]
        dest_time_mins = each_flight_content[7]
        dept_time_day = day_calculator(dept_time_day)
        dest_time_day = day_calculator(dest_time_day)

        eachflight.dept_time = time_calculator(dept_time_day, dept_time_mins)
        eachflight.dest_time = time_calculator(dest_time_day, dest_time_mins)

        if each_flight_content[4] == each_flight_content[6]:
            eachflight.dur = (int(each_flight_content[7]) - int(each_flight_content[5]) + \
                              int(each_flight_content[11])) * 60
        else:
            eachflight.dur = (int(each_flight_content[7]) - int(each_flight_content[5]) + \
                              int(each_flight_content[11]) + 1400 ) * 60

        each_flight_dict[eachflight.flight_key] = (eachflight.flight_no, eachflight.airline, \
            eachflight.plane_no, eachflight.dept_id, eachflight.dest_id, \
            eachflight.dept_time, eachflight.dest_time, eachflight.dur)
    except Exception, e:
        return each_flight_dict

    return each_flight_dict


def time_calculator(dept_day, mins):
    if mins > 0:
        hour_str = str(mins / 60)
        min_str = str(mins % 60)
    else:
        hour_str = '0'
        min_str = '00'

    #cal_time = dept_day + 'T' + hour_str + ':' + min_str + ':' + '00'
    cal_time = str(datetime.datetime(int(dept_day[0:4]), int(dept_day[5:7]), \
                                     int(dept_day[8:10]), int(hour_str), \
                                     int(min_str), 0)).replace(' ','T')

    return cal_time


def day_calculator(dept_day_temp):
    dept_day_list = dept_day_temp.split('/')
    dept_day = str(datetime.datetime(int(dept_day_list[2]), int(dept_day_list[0]), \
                                     int(dept_day_list[1])))[:10]

    return dept_day


def sec_calculator(time_str):
    seconds = time.mktime(time.strptime(time_str,'%Y-%m-%dT%H:%M:%S'))

    return seconds


if __name__ == '__main__':

    taskcontent = 'PEK&CDG&20140716&20140801'
    result = smartfares_task_parser(taskcontent)
    tickets = result['para']['ticket']
    print result
    if tickets != []:
        for x in tickets:
            print x

    '''
    dept_day = '2014-07-14'
    dept_mins = 1240
    print time_calculator(dept_day,dept_mins)
    '''
