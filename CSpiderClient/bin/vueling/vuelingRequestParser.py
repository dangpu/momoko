#! /usr/bin/env python
#coding=UTF8

import re
import time
import sys
from common.class_common import Flight
from util.crawl_func import request_post_data
from common.logger import logger
from common.common import get_proxy, invalid_proxy


reload(sys)
sys.setdefaultencoding('utf-8')

flight_no_pat = re.compile(r'<div class="wrap_icoPrice">(.*?)<label id="ControlGroupScheduleSelectView')
station_temp_pat = re.compile(r'<td class="routeCell">(.*?)<p><a href="#" class="openFlightDetail"', re.S)
dept_time_pat = re.compile(r'departureTime="(.*?).0000000')
dest_time_pat = re.compile(r'arrivalTime="(.*?).000000')
flight_num_pat = re.compile(r'connectionFlight="(.*?)"')
flight_time_pat = re.compile(r'<tr basicPriceRoute=".price.basictd label"(.*?)>', re.S)
price_pat = re.compile(r'price(.*?)</label><span class')

POST_DATA_STRING = 'CONTROLGROUPAVAILABILTYSEARCHINPUTSCHEDULESELECTVIEW$AvailabilityScheduleSelectView$'


def vueling_request_parser(content):
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

        req_dept_time = dept_date + 'T' + dept_hour + ':00'

    except Exception,e:
        logger.error('Parse taskcontent failed!' + str(e))
        return -1
    postdata = getPostData(dept_date,dept_id,dest_id)

    #获取代理
    #p = '116.228.55.217:8000'

    p = get_proxy()

    url = 'http://tickets.vueling.com/ScheduleSelect.aspx'
    Referer = 'http://tickets.vueling.com/ScheduleSelect.aspx'

    content = request_post_data(url,postdata,referer=Referer,proxy=p,\
            Accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")

    result = -1

    if content != '' and len(content) > 100:
        result = vuelingparser(content,flight_no,req_dept_time)
    else:
        invalid_proxy(p)
        logger.error('Get web content failed!')

    return result


def vuelingparser(content,flight_no,req_dept_time):
    #allinfos = []
    #get flight num
    flight_num_list = []
    flight_num_info_temp = flight_no_pat.findall(content)
    if flight_num_info_temp != []:
        for flight_num_info in flight_num_info_temp:
            flight_num_temp_1 = flight_num_info.find('|')
            flight_num_temp_2 = flight_num_info.rfind('~^')

            if flight_num_temp_2 > 0:
                flight_num = flight_num_info[flight_num_temp_1+1:flight_num_temp_1+8]\
                        .replace('~','') + '_' + \
                        flight_num_info[flight_num_temp_2+2:flight_num_temp_2+9].replace('~','')
            else:
                flight_num = flight_num_info[flight_num_temp_1+1:flight_num_temp_1+8].replace('~','')
            flight_num_list.append(flight_num)

        #get station information
        #set station_temp,dept_id and dest_id pattern
        dept_id_list = []
        dest_id_list = []
        station_temp = station_temp_pat.findall(content)
        for station_temp_a in station_temp:
            station_info = station_temp_a.replace('\n', '').replace(' ','')
            dept_id_num = station_info.find('):')
            dept_id = station_info[dept_id_num-3:dept_id_num]
            dest_id_num = station_info.rfind(')')
            dest_id = station_info[dest_id_num-3:dest_id_num]
            dept_id_list.append(dept_id)
            dest_id_list.append(dest_id)

        #get flight_time information
        #set dept_time,dest_time,flight_time pattern
        dept_time_list = []
        dest_time_list = []
        stops_list = []

        flight_time_temp = flight_time_pat.findall(content)
        for time_temp in flight_time_temp:
            dept_time = dept_time_pat.findall(time_temp)[0]
            dest_time = dest_time_pat.findall(time_temp)[0]
            flight_num = flight_num_pat.findall(time_temp)[0]
            dept_time_list.append(dept_time)
            dest_time_list.append(dest_time)
            stops_list.append(flight_num)

        #get each kind flight price
        price_list = []
        price_text = price_pat.findall(content)
        for price_temp in price_text:
            price_temp_num = price_temp.rfind('>') + 1
            each_price = price_temp[price_temp_num:-3].replace(',','.')
            price_list.append(each_price)

        #set seat_type
        seat_type_list = ['经济舱','超经济舱','公务舱']
        seat_type = []

        for i in range(len(price_list)):
            if i % 3 == 0:
                seat_type.append(seat_type_list[0])
            elif i % 3 == 1:
                seat_type.append(seat_type_list[1])
            else:
                seat_type.append(seat_type_list[2])

        flight_no_l,dept_id_l,dest_id_l,dept_time_l,dest_time_l,stops_l = [],[],[],[],[],[]
        for j in range(len(stops_list)):
            for k in range(3):
                flight_no_l.append(flight_num_list[j])
                dept_id_l.append(dept_id_list[j])
                dest_id_l.append(dest_id_list[j])
                dept_time_l.append(dept_time_list[j])
                dest_time_l.append(dest_time_list[j])
                stops_l.append(stops_list[j])

        for i in range(len(price_list)):
            flight = Flight()
            flight.flight_no = flight_no_l[i]
            flight.plane_no = 'NULL'
            flight.airline = 'vueling'
            flight.dept_id = dept_id_l[i]
            flight.dest_id = dest_id_l[i]
            flight.dept_time = dept_time_l[i]
            flight.dest_time = dest_time_l[i]

            dept_time_c = str(dept_time_l[i]).replace('T',',').replace('-',',').replace(':',',').split(',') + [0,0,0]
            dept_time_t = date_handle(dept_time_c)
            dest_time_c = str(dest_time_l[i]).replace('T',',').replace('-',',').replace(':',',').split(',') + [0,0,0]
            dest_time_t = date_handle(dest_time_c)
            flight.dur = int(time.mktime(dest_time_t)) - int(time.mktime(dept_time_t))
            flight.price = price_list[i]
            flight.dept_day = flight.dept_time[:10]
            flight.currency = 'EUR'
            flight.seat_type = seat_type[i]
            flight.source = 'vueling:vueling'
            flight.stop = stops_l[i]
            if flight.flight_no == flight_no and flight.dept_time == req_dept_time:
                return flight.price

        '''
            flight_tuple = (flight.flight_no, flight.plane_no, flight.airline, flight.dept_id, \
                    flight.dest_id, flight.dept_day, flight.dept_time, flight.dest_time, \
                    flight.dur, flight.price, flight.tax, flight.surcharge, flight.currency, \
                    flight.seat_type, flight.source, flight.return_rule, flight.stop)

            allinfos.append(flight_tuple)
        return allinfos
        '''
    else:
        return -1


def date_handle(list):
    for m in range(len(list)):
        list[m] = int(list[m])
    return tuple(list)


def getPostData(dept_time,dept_id,dest_id):
    dept_time_day = dept_time[-2:]
    dept_time_mh = dept_time[:-3]
    postdata = {
        '__EVENTTARGET':POST_DATA_STRING + 'LinkButtonNewSearch',
        POST_DATA_STRING + 'RadioButtonMarketStructure':'OneWay',
        POST_DATA_STRING + 'DropDownListMarketDay1':dept_time_day,
        POST_DATA_STRING + 'DropDownListMarketMonth1':dept_time_mh,
        POST_DATA_STRING + 'DropDownListPassengerType_ADT':'1',
        POST_DATA_STRING + 'DropDownListPassengerType_CHD':'0',
        POST_DATA_STRING + 'DropDownListPassengerType_INFANT':'0',
        POST_DATA_STRING + 'DropDownListSearchBy':'columnView',
        'departureStationCode1':dept_id,
        'arrivalStationCode1':dest_id,
    }
    return postdata

if __name__ == '__main__':
    content = 'VY8007-VY2286&ORY&XRY&2014-04-17T07:00:00&vueling::vueling'

    result = vueling_request_parser(content)

    print str(result)
