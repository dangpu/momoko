#!/usr/bin/env python
#coding=UTF-8
import urllib2
import cookielib
import json
import re
import sys
import time
from common.logger import logger
from util.crawl_func import crawl_single_page
from common.common import get_proxy
from fan_to_jian import fan_to_jian
reload(sys)
sys.setdefaultencoding('utf-8')

key_list = ['searchResultsModel','offers','legs']
legs_key_list = ['price','timeline','stops','departureLocation','arrivalLocation','departureTime','arrivalTime','duration']

JSON_LEN = 100
TASK_ERROR = 12
PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25
CONTENT_LEN = 100

def get_json_url(dept_city=None,dest_city=None,dept_time=None):
    html_url = 'http://www.expedia.com.hk/Flights-Search?trip=oneway&leg1=from:'+dept_city+',to:'+dest_city+',departure:'+dept_time+'TANYT&passengers=children:0,adults:1,seniors:0,infantinlap:Y&options=cabinclass:coach&mode=search&'
    html_res = crawl_single_page(html_url)
    regex = re.compile(r'<div id="originalContinuationId">(.*?)</div>',re.M|re.S|re.I)
    match_id = re.search(regex,html_res)
    if match_id:
        return match_id.group(1).strip('\s')
    else:
        logger.info('not catch the originalContinuationId of json data')
        return False

def get_day(str_day):
    day = str_day.split('/')
    if len(day[1]) < 2:
        day[1]  = '0' + day[1]
    if len(day[2]) < 2:
        day[2]  = '0' + day[2]
    return '-'.join(day)

def get_time(str_time):
    if str_time[0:2] == '上午':
        time = str_time[2:].split(':')
        if int(time[0]) < 10 and len(time[0]) < 2:
            return '0' + str_time[2:]
        else:
            return str(int(time[0]) % 12) + ':' + str(time[1])
    else:
        time = str_time[2:].split(':')
        if int(time[0]) < 12:
            return str(int(time[0]) + 12) + ':' + str(time[1])
        else:
            return str_time[2:]



def get_seat_type(seat_id):
    if seat_id == '1':
        return '头等舱'
    elif seat_id == '2':
        return '商务舱'
    elif seat_id == '3':
        return '经济舱'
    else:
        return '超经济舱'

def expedia_task_parser(taskcontent):
    flights = {}
    tickets = []
    result = {}
    result['para'] = {'flight':flights, 'ticket':tickets}
    result['error'] = 0
    try:
        dept_city,dest_city = taskcontent.split('&')[0].strip(),taskcontent.split('&')[1].strip()
        dept_time = taskcontent.split('&')[2].strip()
        dept_time = dept_time[0:4] +'/'+ dept_time[4:6] + '/' + dept_time[6:8]
    except Exception,e:
        logger.info('url id wrong :'+e)
        result['error'] = TASK_ERROR
        return result
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    url_res = get_json_url(dept_city,dest_city,dept_time)
    if  url_res != False:
        url = 'http://www.expedia.com.hk/Flight-Search-Outbound?c='+ url_res +'&_='+str(time.time())
        task_content_proxy = get_proxy(source='expediaFlight')
        if task_content_proxy == None:
            result['error'] = PROXY_NONE
            return result
        html_res = crawl_single_page(url, proxy = task_content_proxy)
        if html_res == '' or html_res == None:
            result['error'] = PROXY_INVALID
            return result
    else:
        result['error'] = TASK_ERROR
        return result
    try:
        json_list = json.loads(html_res)
        if json_list[key_list[0]] == None:
            result['error'] = DATA_NONE
            return result
        search_legs = json_list[key_list[0]][key_list[1]]
        for legs_list in search_legs:
            for legs_key in legs_list:
                if legs_key == key_list[2]: #legs list
                    ticket_flight_no_list = []
                    ticket_plane_no_list = []
                    ticket_airline_list = []
                    ticket_seat_code_list = []
                    ticket_dept_id = 'NULL'
                    ticket_dest_id = 'NULL'
                    ticket_dept_day = 'NULL'
                    ticket_dept_time = 'NULL'
                    ticket_dest_time = 'NULL'
                    ticket_dur = -1
                    ticket_price = -1.0
                    ticket_tax = -1.0
                    ticket_surcharge = -1.0
                    ticket_currency = 'NULL'
                    ticket_stop = -1
                    legs_child_list = legs_list[legs_key]
                    for child_list in legs_child_list:
                        for child_key in child_list:
                            if child_key == legs_key_list[0]:
                                price_node = child_list[child_key]
                                ticket_price = price_node['totalPriceAsDecimal']
                                ticket_currency = price_node['currencyCode']
                            if child_key == legs_key_list[6]:
                                ticket_dest_day = get_day(child_list[child_key]['date'])
                                ticket_dest_time = ticket_dest_day + 'T' + get_time(child_list[child_key]['time']) + ':00'
                            if child_key == legs_key_list[5]:
                                ticket_dept_day = get_day(child_list[child_key]['date'])
                                ticket_dept_time = ticket_dept_day + 'T' + get_time(child_list[child_key]['time']) + ':00'
                            if child_key == legs_key_list[4]:
                                ticket_dest_id = child_list[child_key]['airportCode']
                            if child_key == legs_key_list[3]:
                                ticket_dept_id = child_list[child_key]['airportCode']
                            if child_key == legs_key_list[2]:
                                ticket_stop = child_list[child_key]
                            if child_key == legs_key_list[7]:
                                hours = child_list[child_key]['hours']
                                minutes =  child_list[child_key]['minutes']
                            if child_key == legs_key_list[1]:
                                timeline_list = child_list[child_key]
                                for each_flight in timeline_list:
                                    if each_flight['segment'] == True:
                                        each_carrier = each_flight['carrier']
                                        each_flight_no = each_carrier['airlineCode']+each_carrier['flightNumber']
                                        ticket_flight_no_list.append(each_flight_no)
                                        each_plane = each_carrier['plane']
                                        ticket_plane_no_list.append(each_plane)
                                        each_airline = each_carrier['airlineName']
                                        ticket_airline_list.append(each_airline)
                                        each_dept_id = each_flight['departureAirport']['code']
                                        each_dest_id = each_flight['arrivalAirport']['code']

                                        each_dept_day = get_day(each_flight['departureTime']['date'])
                                        each_dept_time = each_dept_day + 'T'+ get_time(each_flight['departureTime']['time']) + ':00'

                                        each_dest_day = get_day(each_flight['arrivalTime']['date'])
                                        each_dest_time = each_dest_day + 'T' + get_time(each_flight['arrivalTime']['time']) +':00'
                                        each_duration = each_flight['duration']
                                        each_dur_hours = each_duration['hours']
                                        each_dur_mins = each_duration['minutes']
                                        each_dur = (60*each_dur_mins + each_dur_hours)*60

                            #* each flight
                                        each_seat_code = get_seat_type(each_flight['carrier']['cabinClass'])
                                        ticket_seat_code_list.append(each_seat_code)
                                        flight_key = each_flight_no + '_' + each_dept_id + '_' + each_dest_id
                                        flights[flight_key] = (each_flight_no,fan_to_jian(each_airline),each_plane,\
                                 each_dept_id,each_dest_id,each_dept_time,each_dest_time,each_dur)
                    ticket_source = 'expedia::expedia'
                    ticket_return_rule = 'NULL'
                    ticket_seat_type = '_'.join(ticket_seat_code_list)

                    ticket_flight_no = '_'.join(ticket_flight_no_list)
                    ticket_plane_no = '_'.join(ticket_plane_no_list)
                    ticket_airline = '_'.join(ticket_airline_list)
                    ticket_dur = (hours*60 + minutes) * 60
                    tickets.append((ticket_flight_no,ticket_plane_no,fan_to_jian(ticket_airline),ticket_dept_id,\
                           ticket_dest_id,ticket_dept_day,ticket_dept_time,ticket_dest_time,ticket_dur,\
                           ticket_price,ticket_tax, ticket_surcharge,ticket_currency, ticket_seat_type,\
                          ticket_source,ticket_return_rule,ticket_stop))
        result['error'] = 0
        return result
    except KeyError, e:
        print e
        result['error'] = DATA_NONE
        return result
    except Exception,e:
        print e
        result['error'] = DATA_NONE
        return result
def expedia_request_parser(content):

    result = -1

    return result
if __name__ == '__main__':
    taskcotent = 'Paris&Beijing&20140721'
    result = expedia_task_parser(taskcotent)


