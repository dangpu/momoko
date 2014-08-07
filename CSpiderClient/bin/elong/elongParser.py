#!/usr/bin/env python
#coding=UTF8

'''
    @author: nemo
    @date: 2014-07-10
    @desc:
        elongParser
'''

import lxml.html
import datetime
import json
import re
import string
from util.crawler import UrllibCrawler, MechanizeCrawler
from common.class_common import Flight, EachFlight
from common.logger import logger
from common.common import get_proxy, invalid_proxy
from common.airline_common import Airline

import sys
reload(sys)
sys.setdefaultencoding='utf8'

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

URL = 'http://iflight.elong.com/search/%s/cn_day%d.html'

flightsPattern = re.compile(r"<script>bigpipe.set\('flights',(.*?)\)</script>", re.S)

def time_shifter(time):
    '''
        convert to 2014-07-11T12:52:00
    '''

    #former format: 2014/7/11 12:52:00
    ymd, hms = time.split(' ')[0].split('/'), time.split(' ')[1].split(':')

    year, month, day = ymd[0], ymd[1], ymd[2]
    hour, minute, second = hms[0], hms[1], hms[2]

    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    if len(hour) == 1:
        hour = '0' + hour
    if len(minute) == 1:
        minute = '0' + minute

    return year+'-'+month+'-'+day+'T'+hour+':'+minute+':'+second

def cal_wait_time(arrtime, deptime):
    '''

    '''
    aday, atime = arrtime.split('T')[0], arrtime.split('T')[1]
    dday, dtime = deptime.split('T')[0], deptime.split('T')[1]

    days = (datetime.datetime(int(dday[0:4]), int(dday[5:7]), int(dday[8:])) - datetime.datetime(int(aday[0:4]), int(aday[5:7]), int(aday[8:]))).days
    hours = int(dtime[0:2]) - int(atime[0:2])
    minutes = int(dtime[3:5]) - int(dtime[3:5])

    waittime = days * 86400 + hours * 3600 + minutes * 60
    return waittime
def elong_page_parser(htmlcontent):
    '''

    '''

    tickets = []
    flights = {}

    if htmlcontent.find('您访问的页面不存在或暂时无法访问') != -1:
        return tickets, flights

    try:
        flights_json = flightsPattern.findall(htmlcontent)[0]
        allflights = json.loads(flights_json)['FlightLegList']

        for flightInfo in allflights:
            flight = Flight()

            flight.currency = 'CNY'
            flight.seat_type = '经济舱'
            flight.stop = len(flightInfo['segs']) - 1
            flight.price = int(flightInfo['cabs'][0]['oprice'])
            flight.tax = int(flightInfo['tax'])
            flight.source = 'elong::elong'

            flight.airline = ''
            flight.plane_no = ''
            flight.flight_no = ''
            flight.dur = 0

            for singleflightInfo in flightInfo['segs']:
                eachFlight = EachFlight()
                eachFlight.flight_no = singleflightInfo['fltno']
                eachFlight.plane_no = singleflightInfo['plane']
                eachFlight.airline = singleflightInfo['corpn']
                eachFlight.dept_id = singleflightInfo['dport']
                eachFlight.dest_id = singleflightInfo['aport']
                eachFlight.dept_time = time_shifter(singleflightInfo['dtime'])  #convert to 2014-07-11T12:06:00
                eachFlight.dest_time = time_shifter(singleflightInfo['atime'])
                eachFlight.dur = int(singleflightInfo['ftime']) * 60

                eachFlight.flight_key = eachFlight.flight_no + '_' + eachFlight.dept_id + '_' + eachFlight.dest_id

                flights[eachFlight.flight_key] = (eachFlight.flight_no, eachFlight.airline, eachFlight.plane_no, eachFlight.dept_id, \
                        eachFlight.dest_id, eachFlight.dept_time, eachFlight.dest_time, eachFlight.dur)

                flight.airline = flight.airline + eachFlight.airline + '_'
                flight.plane_no = flight.plane_no + eachFlight.plane_no + '_'
                flight.flight_no = flight.flight_no + eachFlight.flight_no  + '_'

                flight.dur += eachFlight.dur
            
            if len(flightInfo['segs']) > 1:
                for i in range(0, len(flightInfo['segs']) - 1):
                        flight.dur += cal_wait_time(time_shifter(flightInfo['segs'][i]['atime']), time_shifter(flightInfo['segs'][i+1]['dtime']))

            flight.flight_no = flight.flight_no[:-1]
            flight.plane_no = flight.plane_no[:-1]
            flight.airline = flight.airline[:-1]

            flight.dept_id = flightInfo['segs'][0]['dport']
            flight.dest_id = flightInfo['segs'][-1]['aport']
            flight.dept_time = time_shifter(flightInfo['segs'][0]['dtime'])
            flight.dest_time = time_shifter(flightInfo['segs'][-1]['atime'])
            flight.dept_day = flight.dept_time.split('T')[0]

            flight_tuple = (flight.flight_no,flight.plane_no,flight.airline,flight.dept_id,flight.dest_id,flight.dept_day,\
                    flight.dept_time,flight.dest_time,flight.dur,flight.price,flight.tax,flight.surcharge,flight.currency,\
                    flight.seat_type,flight.source,flight.return_rule,flight.stop)

            tickets.append(flight_tuple)

    except Exception, e:
        logger.info(str(e))
        return [], {}

    return tickets, flights


def elong_task_parser(content):
    '''

    '''
    
    #初始化result
    result = {}
    result['para'] = {'ticket':[], 'flight':{}}
    result['error'] = 0

    #解析content
    try:
        contents = content.split('&')
        dept, dest, origdate = contents[0].strip(),contents[1].strip(),contents[2].strip()
        location = dept + '-' + dest

        origday = datetime.datetime(string.atoi(origdate[0:4]),string.atoi(origdate[4:6]),string.atoi(origdate[6:]))
        urlday = (origday - datetime.datetime.today()).days
        dept_date = str(origday).split(' ')[0].strip()
    except Exception,e:
        logger.error('elongFlight:taskcontent error: %s'%str(e))
        result['error'] = TASK_ERROR
        return result

    url = URL%(location,urlday)

    p = get_proxy(source='elongFlight')
    
    if p == None:
        result['error'] = PROXY_NONE
        return result

    mc = MechanizeCrawler(p = '')

    page = mc.get(url, html_flag = True)

    if page == None:
        invalid_proxy(proxy = p, source='elongFlight')
        logger.error('elongFlight: Proxy Error: htmlcontent is null with proxy: %s'%p)
        result['error'] = PROXY_INVALID
        return result

    tickets, flights = elong_page_parser(page)

    if tickets == [] or tickets == None:
        result['error'] = DATA_NONE
        return result

    result['para']['flight'] = flights
    result['para']['ticket'] = tickets

    return result

def elong_request_parser(content):

    result = -1

    return result

if __name__ == '__main__':

    taskcontent = 'beijing&paris&20140802'

    taskresult = elong_task_parser(taskcontent)

    print taskresult
