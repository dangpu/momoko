#! /usr/bin/env python
#coding=UTF8

'''
    @author:fangwang
    @date:2014-06-23
    @desc:crawl and parse easyjet data
'''

import sys
from util.crawl_func import crawl_single_page, request_post_data
from common.class_common import Flight,EachFlight
from common.common import get_proxy, invalid_proxy
from common.logger import logger
from common.airport_common import Airport
import cookielib
import urllib2
import urllib
import re
import json
import time
import datetime

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

CONTENT_LEN = 100

REQUEST_URL = 'http://www.easyjet.com/EN/BasketView.mvc/AddFlight'
HOST = 'http://www.easyjet.com'

reload(sys)
sys.setdefaultencoding('utf8')

#pattern
each_day_content_pat = re.compile(r'<div class="day" >(.*?)</li></ul></div>', re.S)
each_flight_content_pat = re.compile(r'<li id=(.*?)<li id="DayLoading', re.S)
flight_to_add_state_pat = re.compile("'(.*?)' class='selectable standard'>", re.S)
backet_option_pat = re.compile(r"var BasketOptions = '(.*?)';",re.S)
search_session_pat = re.compile(r'<input id="flightSearchSession" type="hidden" value="(.*?)" />', re.S)
backet_state_pat = re.compile(r'<input id="__BasketState" name="__BasketState" type="hidden" value="(.*?)" />', re.S)
flight_info_pat = re.compile(r'Whitepages.Basket.instance.update\(\'(.*?)\'\);\}', re.S)
currency_pat =re.compile(r'"bc":"(.*?)",', re.S)
flight_no_pat = re.compile(r'"fn":"(.*?)",', re.S)
dest_id_pat = re.compile(r'"paa_iata":"(.*?)",', re.S)
dept_id_pat = re.compile(r'pda_iata":"(.*?)",', re.S)
dest_time_pat = re.compile(r'"arr_dt":"(.*?)",', re.S)
dept_time_pat = re.compile(r'"dep_dt":"(.*?)",', re.S)
price_pat = re.compile('"up":(.*?)00,', re.S)

airport = Airport

def easyjet_task_parser(taskcontent):
    result = {}
    flights = {}
    tickets = []
    result['para'] = {'flight':flights, 'ticket':tickets}
    result['error'] = 0
    try:
        dept_id, dest_id, dept_day_temp = taskcontent.strip().split('&')[0], \
                taskcontent.strip().split('&')[1], \
                taskcontent.strip().split('&')[2]
    except:
        logger.error('easyjet::Wrong Content Format with %s'%taskcontent)
        result['error'] = TASK_ERROR
        return result

    search_url = get_search_url(dept_id, dest_id, dept_day_temp)

    p = get_proxy(source='easyjet')
    
    time_zone_A = airport[dept_id]
    time_zone_B = airport[dest_id]
    #print p
    #print search_url
    if p == None:
        result['error'] = PROXY_NONE
        return result

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    
    i = 0 
    content_len = 0
    while i < 3 and content_len < CONTENT_LEN:
        content = crawl_single_page(url=search_url, proxy=p, n=1, referer=HOST)
        content_len = len(content)
        i += 1
    
    if content == '' or content == None or len(content) < CONTENT_LEN:
        result['error'] = PROXY_INVALID
        return result

    para =  parsePage(content, p, time_zone_A, time_zone_B)
    
    if para == {'flight':{}, 'ticket':[]}:
        result['error'] = DATA_NONE
        return result
    else:
        flights = para['flight']
        tickets = para['ticket']
        result['para'] = {'ticket':tickets, 'flight':flights}
        return result


def easyjet_request_parser(taskcontent):
    result = -1

    return result


def get_search_url(dept_id, dest_id, dept_day_temp):
    dept_day = dept_day_temp[6:8] + '/' + dept_day_temp[4:6] + \
            '/' + dept_day_temp[0:4]
    search_url = 'http://www.easyjet.com/links.mvc?dep=' + dept_id + \
            '&dest=' + dest_id + '&dd=' + dept_day + \
            '&apax=1&pid=www.easyjet.com&cpax=0&ipax=0&lang=EN' + \
            '&isOneWay=on&searchFrom=SearchPod|/en/'

    return search_url


def parsePage(content, proxy, time_zone_A, time_zone_B):
    content = content.replace('\n','').replace('    ','')
    flights = {}
    tickets = []
    result = {'flight':flights, 'ticket':tickets}
    
    try:
        each_day_content = each_day_content_pat.findall(content)[1]
        backet_option = backet_option_pat.findall(content)[0]     
        search_session = search_session_pat.findall(content)[0]
        backet_state = backet_state_pat.findall(content)[0]
    except Exception, e:
        print str(e)
        return result

    try:
        flights_content = each_flight_content_pat.findall(each_day_content)
        if len(flights_content) == 0:
            return result
    except:
        return result

    for flight_content in flights_content:
        try:
            flight_adding_id = flight_to_add_state_pat.findall(flight_content)[0]
        except:
            continue
        post_data = {
                'flightToAddState':flight_adding_id,
                'flightSearchSession':search_session,
                'basketOptions':backet_option,
                'flightOptionsState':'Visible',
                '__BasketState':backet_state
                }
        i = 0
        content_len = 0
        while i < 3 and content_len < CONTENT_LEN:
            content = request_post_data(url=REQUEST_URL, data=post_data, proxy=proxy, n=1)
            content_len = len(content)
            i += 1

        if len(content) < 100 or content == '' or content == None:
            continue

        para = parseFlightAndTicket(content, time_zone_A, time_zone_B)
        if para['flight'] != {}:
            flights.update(para['flight'])
        if para['ticket'] != []:
            tickets += para['ticket']

    result = {'flight':flights, 'ticket':tickets}
    return result


def parseFlightAndTicket(content_temp, time_zone_A, time_zone_B):
    content = content_temp.encode('utf-8')
    content = content.replace('£', 'GBP')
    flights = {}
    tickets = []
    result = {'ticket':tickets, 'flight':flights}

    flight = Flight()
    eachflight = EachFlight()
    
    try:
        content_json = json.loads(content)
        flight_content = content_json['Html']
        flight_content = flight_content.replace('\n','')
        
        flight.flight_no = 'EZY' + flight_no_pat.findall(flight_content)[0]
        flight.airline = 'easyjet'
        flight.dept_id = dept_id_pat.findall(flight_content)[0]
        flight.dest_id = dest_id_pat.findall(flight_content)[0]
        flight.dept_time = dept_time_pat.findall(flight_content)[0].replace(' ','T') + ':00'
        flight.dest_time = dest_time_pat.findall(flight_content)[0].replace(' ','T') + ':00'
        flight.price = price_pat.findall(flight_content)[0]
        flight.seat_type = '经济舱'
        flight.source = 'easyjet::easyjet'
        flight.currency = currency_pat.findall(flight_content)[0]
        flight.stop = 0
        flight.dept_day = flight.dept_time.split('T')[0]
        flight.dur = durCal(flight.dept_time, flight.dest_time, time_zone_A, time_zone_B)

        eachflight.flight_key = flight.flight_no + '_' + flight.dept_id + '_' + flight.dest_id
        eachflight.flight_no = flight.flight_no
        eachflight.airline = 'easyjet'
        eachflight.dept_id = flight.dept_id
        eachflight.dest_id = flight.dest_id
        eachflight.dept_time = flight.dept_time
        eachflight.dest_time = flight.dest_time
        eachflight.dur = flight.dur

        flights[eachflight.flight_key] = (eachflight.flight_no, eachflight.airline, eachflight.plane_no, \
                eachflight.dept_id, eachflight.dest_id, eachflight.dept_time, eachflight.dest_time, \
                eachflight.dur)

        tickets = [(flight.flight_no, flight.plane_no, flight.airline, flight.dept_id, flight.dest_id, \
                flight.dept_day, flight.dept_time, flight.dest_time, flight.dur, flight.price, \
                flight.tax, flight.surcharge,  flight.currency, flight.seat_type, \
                flight.source, flight.return_rule, flight.stop)]

        result['flight'] = flights
        result['ticket'] = tickets
        #flight_info_json = flight_info_pat.findall(flight_content)[0]
        #print flight_info_json
    except Exception, e:
        print str(e)
        return result

    return result


def durCal(dept_time, dest_time, time_zone_A, time_zone_B):
    try:
        dept_time_str = datetime.datetime.strptime(dept_time, '%Y-%m-%dT%H:%M:%S')
        dest_time_str = datetime.datetime.strptime(dest_time, '%Y-%m-%dT%H:%M:%S')
        dept_time_temp = int(time.mktime(dept_time_str.timetuple()))
        dest_time_temp = int(time.mktime(dest_time_str.timetuple()))
        dur = dest_time_temp - dept_time_temp 
        dur = dur - (time_zone_B - time_zone_A) * 3600
    except:
        return -1

    return dur

if __name__ == '__main__':
    taskcontent = 'CDG&LGW&20140801'
    result = easyjet_task_parser(taskcontent)
    print result
