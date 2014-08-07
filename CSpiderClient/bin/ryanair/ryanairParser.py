#!/usr/bin/env python
#coding=UTF8
'''
    @author: nemo
    @date: 2014-04-13
    @desc: ryanair机票数据,114.215.168.168
'''

import datetime
import jsonlib
import parser
from common.class_common import Flight
from common.common import get_proxy, invalid_proxy
from util.crawl_func import request_post_data
from common.logger import logger

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

flightDataStr = "FR.flightData ="
tagStr = "FR.rynTag ="

def ParsePage(data):
    start = data.find(flightDataStr)
    if start == -1:
        return None
    end = data.find("\r\n", start)
    if end == -1:
        return None
    return data[start + len(flightDataStr): end-1]

def GetCurrency(data):
    start = data.find(tagStr)
    if start == -1:
        return None
    end = data.find("\r\n", start)
    if end == -1:
        return None
    data = jsonlib.read(data[start + len(tagStr): end-1])
    if "currency" in data:
        return data["currency"]
    return None

def GetData(tripType, orig, dest, deptDate, retDate, proxy = None):
    searchURL = "https://www.bookryanair.com/SkySales/Search.aspx"
    refererURL = "https://www.bookryanair.com/SkySales/booking.aspx?culture=en-gb&lc=en-gb&cmpid2=Google"

    data = {"fromaction": "Search.aspx", "SearchInput$TripType": tripType,
                "SearchInput$Orig": orig,
                "SearchInput$Dest": dest,
                "SearchInput$DeptDate": deptDate,
                "SearchInput$RetDate": retDate,
                "SearchInput$IsFlexible": "on",
                "SearchInput$PaxTypeADT": 1,
                "SearchInput$PaxTypeCHD": 0,
                "SearchInput$PaxTypeINFANT": 0,
                "SearchInput$AcceptTerms": "on",
                "__EVENTTARGET": "SearchInput$ButtonSubmit",
                }

    resp = request_post_data(searchURL, data, referer = refererURL, proxy = proxy)
    if resp == None or len(resp) == 0:
        return None
    else:
        return resp

def GetPrice(data):
    price = 0.0
    for k,v in data["ADT"][1].items():
        price += float(v)
    return price

def ryanair_task_parser(content):
    result = {}
    result['para'] = None
    result['error'] = 0

    try:
        contents = content.split('&')
        dept_id = contents[0]
        dest_id = contents[1]
        dept_date = contents[2][:4] + '-' + contents[2][4:6] + '-' + contents[2][6:]
        ret_date = str(datetime.datetime.strptime(dept_date[2:], '%y-%m-%d') + datetime.timedelta(10)).split(' ')[0].strip()#do not use this value
    except Exception,e:
        logger.error('ryanairFlight: wrong content format with %s'%content)
        result['error'] = TASK_ERROR
        return result
    
    p = get_proxy(source = 'ryanairFlight')

    if p == None:
        result['error'] = PROXY_NONE
        return result

    trip_type = 'Oneway'
    page = GetData(trip_type, dept_id, dest_id, dept_date, ret_date, proxy = p)

    if page == None:
        invalid_proxy(proxy = p, source='ctripFlight')
        result['error'] = PROXY_INVALID
        return result

    data = ParsePage(page)
    if data == None:
        result['error'] = DATA_NONE
        return result

    currency = GetCurrency(page)
       
    allinfo = []
    data = jsonlib.read(data)
    for k, v in data.items():
        for one_day_flights in v:
            for one_day_flight in one_day_flights[1]:
                flight = Flight()
                flight.dept_day = one_day_flights[0]
                strs = one_day_flight[1].split("~")

                if len(strs) != 9:
                    continue
                flight.flight_no = strs[0].strip() + strs[1].strip()
                flight.dept_id = strs[4].strip()
                flight.dest_id = strs[6].strip()
                flight.airline = "ryanair"
                flight.source = "ryanair::ryanair"
                
                dept_time = datetime.datetime.strptime(strs[5], '%m/%d/%Y %H:%M')
                dest_time = datetime.datetime.strptime(strs[7], '%m/%d/%Y %H:%M')
                flight.dept_time = str(dept_time).replace(' ','T')
                flight.dest_time = str(dest_time).replace(' ','T')
                flight.stop = 0

                days = (dest_time - dept_time).days
                dur = (dest_time.hour - dept_time.hour) * 3600 + (dest_time.minute - dept_time.minute) * 60 + days * 86400

                flight.dur = dur
                flight.price = int(GetPrice(one_day_flight[4]))
                flight.currency = currency

                allinfo.append((flight.flight_no, flight.plane_no, flight.airline, flight.dept_id, \
                        flight.dest_id, flight.dept_day, flight.dept_time, flight.dest_time, \
                        flight.dur, flight.price, flight.tax, flight.surcharge, flight.currency, \
                        flight.seat_type, flight.source, flight.return_rule, flight.stop))

    result['para'] = allinfo
    if allinfo == []:
        result['para'] = DATA_NONE
    return result

def ryanair_request_parser(content):
    result = -1

    try:
        infos = content.split('|')
        flight_info = infos[0].strip()
        time_info = infos[1].strip()
        ticketsource = infos[2].strip()

        flight_no = flight_info.split('-')[0]
        dept_id,dest_id = flight_info.split('-')[1],flight_info.split('-')[2]

        dept_day,dept_hour = time_info.split('_')[0],time_info.split('_')[1]
        dept_date = dept_day[0:4] + '-' + dept_day[4:6] + '-' + dept_day[6:]

        orig_dept_time = dept_date + 'T' + dept_hour + ':00'
        ret_date = dept_date
    except Exception,e:
        logger.error('ryanairFlight: Wrong Content Format with %s'%content)
        return result

    trip_type = 'Oneway'
    page = GetData(trip_type, dept_id, dest_id, dept_date, ret_date, proxy = None)

    if page == None:
        return result

    data = ParsePage(page)
    if data == None:
        return result

    currency = GetCurrency(page)

    data = jsonlib.read(data)
    for k, v in data.items():
        for one_day_flights in v:
            for one_day_flight in one_day_flights[1]:
                flight = Flight()
                flight.dept_day = one_day_flights[0]
                strs = one_day_flight[1].split("~")

                if len(strs) != 9:
                    continue
                flight.flight_no = strs[0].strip() + strs[1].strip()
                dept_time = datetime.datetime.strptime(strs[5], '%m/%d/%Y %H:%M')
                dest_time = datetime.datetime.strptime(strs[7], '%m/%d/%Y %H:%M')
                flight.dept_time = str(dept_time).replace(' ','T')
                flight.dest_time = str(dest_time).replace(' ','T')
                flight.price = int(GetPrice(one_day_flight[4]))

                if flight.flight_no == flight_no and flight.dept_time == orig_dept_time:
                    result = flight.price
                    return result

    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 1:
        print "Usage: %s " %sys.argv[0]
        sys.exit()
        
    # 测试
    
    taskcontent = "MRS&CIA&20140612"
    result1 = ryanair_task_parser(taskcontent)

    print str(result1)

    content = "FR9796-MRS-CIA|20140612_16:15|ryanair::ryanair"

    result2 = ryanair_request_parser(content)

    print str(result2)
    
