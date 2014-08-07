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

def GetData(tripType, orig, dest, deptDate, retDate):
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

    p = get_proxy()
    p = '221.181.104.11:8080'
    resp = request_post_data(searchURL, data, referer = refererURL, proxy = p,Accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
    if resp == None or len(resp) == 0:
        #invalid_proxy(p)
        pass
    else:
        return resp
    return resp

def GetPrice(data):
    price = 0.0
    for k,v in data["ADT"][1].items():
        price += float(v)
    return price

def ryanair_request_parser(content):
    try:
        infos = content.split('|')
        flight_info = infos[0].strip()
        time_info = infos[1].strip()
        ticketsource = infos[2].strip()

        flight_no = flight_info.split('-')[0]
        dept_id,dest_id = flight_info.split('-')[1],flight_info.split('-')[2]

        #date：20140510，time：09:10
        dept_day,dept_hour = time_info.split('_')[0],time_info.split('_')[1]

        dept_date = dept_day[0:4] + '-' + dept_day[4:6] + '-' + dept_day[6:]#2014-05-10

        orig_dept_time = dept_date + 'T' + dept_hour + ':00'

        ret_date = dept_date

        #ret_date = str(datetime.datetime.strptime(dept_date[2:], '%y-%m-%d') + datetime.timedelta(1)).split(' ')[0].strip()#do not use this value
    except Exception,e:
        logger.error('wrong content format with %s'%content)
    
    trip_type = 'Oneway'
    page = GetData(trip_type, dept_id, dest_id, dept_date, ret_date)
    data = ParsePage(page)
    if data == None:
        return -1

    currency = GetCurrency(page)
     
    result = -1
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
                #flight.stop = 0

                #days = (dest_time - dept_time).days
                #dur = (dest_time.hour - dept_time.hour) * 3600 + (dest_time.minute - dept_time.minute) * 60 + days * 86400

                #flight.dur = dur
                flight.price = int(GetPrice(one_day_flight[4]))
                #flight.currency = currency
                
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
    
    content = "FR293-STN-DUB|20140510_20:30|ryanair::ryanair"
    result = ryanair_request_parser(content)

    print result
    
