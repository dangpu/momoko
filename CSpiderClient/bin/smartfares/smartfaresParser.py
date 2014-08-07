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
from common.class_common import Flight, EachFlight
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
        dept_id, dest_id, dept_day = taskcontent.strip().split('&')[0], \
            taskcontent.strip().split('&')[1], taskcontent.strip().split('&')[2]
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
        search_url = get_search_url(dept_day,dept_id,dest_id)
        content = crawl_single_page(search_url, proxy=p, referer=HOST)
        search_id = get_search_id(content)
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


def get_search_url(dept_day, dept_id, dest_id):
    dept_day1 = dept_day[0:4]
    dept_day2 = dept_day[4:6]
    dept_day3 = dept_day[6:8]
    search_url = 'http://www.smartfares.com/?Type=1&Adult=1&Child=0&Lap=0' + \
                 '&Date0=' + dept_day2 + '/' + dept_day3 + '/' + dept_day1 + \
                 '&DestCity0=' + dest_id + '&OrigCity0=' + dept_id + \
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
        flight = Flight()

        try:

            flight.price = int(each_flight_json[4][0][2]) + 1
            flight.tax = int(each_flight_json[4][0][3]) + 1

            flight_info_list = each_flight_json[5]
            
            flight.dur = int(flight_info_list[0][5]) * 60
            flight.dept_id = flight_info_list[0][1]
            flight.dest_id = flight_info_list[0][3]
            dept_day_temp = flight_info_list[0][4]
            flight.dept_day = day_calculator(dept_day_temp)

            each_flight_list = flight_info_list[0][7]

            dept_time_mins = int(each_flight_list[0][5])

            flight.dept_time = time_calculator(flight.dept_day, dept_time_mins)
            dest_time_day = each_flight_list[-1][6]
            dest_time_mins = each_flight_list[-1][7]
            dest_time_day = day_calculator(dest_time_day)
            flight.dest_time = time_calculator(dest_time_day, dest_time_mins)

            flight_no = ''
            airline = ''
            plane_no = ''

            for each_flight_content in each_flight_list:

                flight_no += each_flight_content[2] + each_flight_content[10] + '_'
                airline_temp = ''
                plane_no += each_flight_content[12] + '_'
                try:
                    airline_temp = airline_dict[each_flight_content[2]]
                except:
                    logger.info('[AIRLINECODE]' + each_flight_content[2])

                airline += airline_temp  + '_'


                eachflight = EachFlight()

                #print each_flight_content
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
                        continue

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

                    flights[eachflight.flight_key] = (eachflight.flight_no, eachflight.airline, \
                        eachflight.plane_no, eachflight.dept_id, eachflight.dest_id, \
                        eachflight.dept_time, eachflight.dest_time, eachflight.dur)
                except Exception, e:
                    #print str(e)
                    continue

            flight.airline = airline[:-1]
            flight.flight_no = flight_no[:-1]
            flight.plane_no = plane_no[:-1]

            if flight.airline[0] == '_' or flight.plane_no[0] == '_':
                continue

            flight.stop = len(each_flight_list) - 1

            flight.source = 'smartfares::smartfares'
            flight.seat_type = '经济舱'
            flight.currency = 'USD'

            each_ticket_tuple = (flight.flight_no, flight.plane_no, flight.airline, \
                            flight.dept_id, flight.dest_id, flight.dept_day, flight.dept_time, \
                            flight.dest_time, flight.dur, flight.price, flight.tax, \
                            flight.surcharge, flight.currency, flight.seat_type, \
                            flight.source, flight.return_rule, flight.stop)
            #print each_ticket_tuple
            tickets.append(each_ticket_tuple)
        except Exception, e:
            #print str(e)
            continue

    result['flight'] = flights
    result['ticket'] = tickets
    return result


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

    fout = open('workload.txt','r')
    content = fout.read()
    content_lsit = content.split('\n')
    for taskcontent in content_lsit[2:3]:
        taskcontent = 'PEK&CDG&20140716'
        result = smartfares_task_parser(taskcontent)
        tickets = result['para']['ticket']
        if tickets != []:
            for x in tickets:
                print x

    '''
    dept_day = '2014-07-14'
    dept_mins = 1240
    print time_calculator(dept_day,dept_mins)
    '''
