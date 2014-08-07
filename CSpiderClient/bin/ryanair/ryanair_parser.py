#!/usr/bin/env python
#coding=UTF8
'''
    @author: devin
    @desc: 抓取机票数据
'''

import datetime
import jsonlib
import parser
from common.common import get_proxy, invalid_proxy
from util.crawl_func import request_post_data

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

    # 如果抓起失败，换一个代理IP，然后重试
    for i in range(3):
        p = get_proxy()
        resp = request_post_data(searchURL, data, referer = refererURL, proxy = p)
        if resp == None or len(resp) == 0:
            invalid_proxy(p)
        else:
            return resp
    return resp

def GetPrice(data):
    price = 0.0
    for k,v in data["ADT"][1].items():
        price += float(v)
    return price

def Parse(trip_type, orig, dest, dept_date, ret_ate):
       page = GetData(trip_type, orig, dest, dept_date, ret_ate)
       data = ParsePage(page)
       if data == None:
           return False

       currency = GetCurrency(page)
       
       tasks = []
       data = jsonlib.read(data)
       for k, v in data.items():
           for one_day_flights in v:
               for one_day_flight in one_day_flights[1]:
                   ticket = Ticket()
                   ticket.dept_day = one_day_flights[0]
                   
                   strs = one_day_flight[1].split("~")
                   if len(strs) != 9:
                       continue

                   # flight info
                   ticket.flight = Flight()
                   ticket.flight.flight_no = strs[0].strip() + strs[1].strip()
                   ticket.flight.orig_id = strs[4].strip()
                   ticket.flight.dest_id = strs[6].strip()
                   ticket.flight.airlines = "ryanair"
                   ticket.source = "ryanair"
                   
                   ticket.dept_time = datetime.datetime.strptime(strs[5], '%m/%d/%Y %H:%M')
                   ticket.reac_time = datetime.datetime.strptime(strs[7], '%m/%d/%Y %H:%M')
                   ticket.remain_tickets = one_day_flight[5]
                   ticket.price = GetPrice(one_day_flight[4])
                   ticket.currency = currency
                   logger.info(ticket.flight.orig_id + " " + ticket.flight.dest_id + " " + ticket.dept_day + " " + str(ticket.price)) 
                   
                   task = FlightPriceTask()
                   task.task_id = FlightPriceTask.FormatTaskID(ticket.flight.orig_id, ticket.flight.dest_id, ticket.dept_day)
                   tasks.append((task, -1))
                   # 更新机票信息
                   UpdateTickets([ticket])

       return tasks

class RyanairParser(parser.Parser):
    def __init__(self):
        pass
    
    def parse(self, task):
        strs = task.content.split(" ")
        if len(strs) != 5:
            return ""
        tickets = Parse(strs[0], strs[1], strs[2], strs[3], strs[4])
                    
    def request(self, task):
        print task
        strs = task.content.split(" ")
        if len(strs) != 5:
            return ""
        tickets = Parse(strs[0], strs[1], strs[2], strs[3], strs[4])
        return jsonlib.write(tickets)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 1:
        print "Usage: %s " %sys.argv[0]
        sys.exit()
        
    # 测试
    from common.task import Task
    from common.task import RequestTask
    
    ryanair_parser = RyanairParser()
    
    task = Task()
    task.source = "ryanair"
    task.content = "OneWay STN DUB 2014-05-10 2014-05-25"
    ryanair_parser.parse(task)
    
    task = RequestTask()
    task.content = "OneWay STN DUB 2014-04-20 2014-04-25"
    task.source = "ryanair"
    print ryanair_parser.request(task)

