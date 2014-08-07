#!/usr/bin/env python
#coding=UTF8

'''
    @author:nemo
    @date:2014-03-28
    @desc:
        验证wegoFlight的数据
'''

import time
from datetime import datetime
import re
import requests
from common.logger import logger
from common.common import get_proxy, invalid_proxy
from util.crawl_func import crawl_single_page
from common.class_common import Flight

section_pat = re.compile(r'<section class="card js-card"(.*?)</section>',re.S)
flight_no_pat = re.compile(r' data-route-id="(.*?)">',re.S)
airline_name_pat = re.compile(r'<span class="airline-name">(.*?)</span>',re.S)
departure_code_pat = re.compile(r'<div class="segment-departure-code">(.*?)</div>',re.S)
arrival_code_pat = re.compile(r'<div class="segment-arrival-code">(.*?)</div>',re.S)
departure_time_pat = re.compile(r'<div class="fl-from"><strong>(.*?)</strong>')
arrival_time_pat = re.compile(r'<div class="fl-to"><strong>(.*?)</strong>')
flight_duration_pat = re.compile(r'<span class="duration">(.*?)</span>')
tickets_info_pat = re.compile(r'<div class="fare-option">(.*?)target="_blank">',re.S)
tickets_links_pat = re.compile(r'<a class="button external sponsor-book-button js-deeplink" href="(.*?)" ')
day_pat = re.compile(r'(\d*?)d')
hour_pat = re.compile(r'(\d*?)h')
min_pat = re.compile(r'(\d*?)m')
page_pat = re.compile(r'<span>个报价中</span>的<strong>(.*?)</strong>')
tickets_price_pat = re.compile(r'data-price-usd="(.*?)</strong></span>')
stops_pat = re.compile(r'_')
tickets_web_pat = re.compile(r'<img src="http://(.*?).gif" />',re.S)

def get_url(dept_id, arri_id, outbound_date):
    outbound_date_1 = outbound_date[:4]    #get year
    outbound_date_2 = outbound_date[5:7]     #get
    outbound_date_3 = outbound_date[-2:]   #get day
    outbound_date = outbound_date_3 + '%2F' + outbound_date_2 + '%2F' + outbound_date_1

    """
    url = 'http://www.wego.cn/flights/search?departure_code=' + dept_id + '&departure_city=true&arrival_code='\
    + arri_id + '&arrival_city=false&triptype=' + triptype + '&outbound_date=' + outbound_date + \
        '&inbound_date=&adults_count=' + str(adults_count) + \
        '&children_count=' + str(children_count) + '&cabin=economy'"""

    url = 'http://www.wego.cn/flights/search?departure_code=' + dept_id + '&departure_city=true&arrival_code='\
    + arri_id + '&arrival_city=false&triptype=oneway&outbound_date=' + outbound_date + \
        '&inbound_date=&adults_count=1&children_count=0&cabin=economy'
    return url

def get_search_id(url):
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    try:
        req = requests.get(url, headers = hdr).url
        url_res_pat = re.compile(r'search/(.*?)\?arrival_code')
        if url_res_pat != []:
            url_res = url_res_pat.findall(req)[0]
            return url_res
        else :
            return ""
    except Exception,e:
        print "Get_search_id Error: %s" %str(e)
        return ""
    
def get_trip_id(dept_id, dest_id, dept_time):
    trip_id = dept_id + '%3A' + dest_id + '%3A' + dept_time
    return trip_id

def get_start_url(search_id, trip_id):
    start_url = 'http://www.wego.cn/flights/search/show_listings?search_id=' + search_id + \
        '&trip_id=' + trip_id + '&fares_query_type=route'
    return start_url

def get_flight_url(search_id, trip_id, page_num):
    url_list = []
    for num in range(int(round((float(page_num))))):
        flight_url = 'http://www.wego.cn/flights/search/show_listings?search_id=' + search_id + \
        '&trip_id=' + trip_id + '&fares_query_type=route&per_page=30&page=' + str(num + 1)
        url_list.append(flight_url)
    return url_list

def parser(content):
    #get section
    all_info = []
    flights = []

    section = section_pat.findall(content)

    for temp in section:
        every_flight = []

        #get flight number
        flights_temp = flight_no_pat.findall(temp)[0].split(':')
        if len(flights_temp) == 1:
            flight_string1 = flights_temp[0]
            flight_num = flight_string1[:flight_string1.find('-')]
        elif len(flights_temp) >= 2:
            flight_num2 = ''
            for flight_temp_aplha in flights_temp:
                flight_num2 = flight_num2 + '_' + flight_temp_aplha[:flight_temp_aplha.find('-')]
            flight_num = flight_num2
        every_flight.append(flight_num[1:])

        #get plane number
        every_flight.append('')

        #get airline name
        airline_name = airline_name_pat.findall(temp)[0]
        every_flight.append(airline_name)

        #get departure code
        departure_code = departure_code_pat.findall(temp)
        every_flight.append(departure_code[0])

        #get arrival code
        arrival_code = arrival_code_pat.findall(temp)
        arrival_code_length = len(arrival_code)
        every_flight.append(arrival_code[arrival_code_length-1])

        #get departure time
        departure_time_temp = departure_time_pat.findall(temp)
        dep_time = '2014 ' + departure_time_temp[0][4:].replace(',','')
        departure_time = str(datetime.strptime(dep_time,'%Y %d %b %I:%M %p')).replace(' ','T')
        every_flight.append(str(departure_time))

        #get arrival time
        arrival_time_temp = arrival_time_pat.findall(temp)
        arrival_time_length = len(arrival_time_temp)
        arr_time = '2014 ' + arrival_time_temp[arrival_time_length-1][4:].replace(',','')
        arrival_time = str(datetime.strptime(arr_time, '%Y %d %b %I:%M %p')).replace(' ','T')
        every_flight.append(str(arrival_time))

        #get flight duration
        flight_dur = []
        #day_pat = re.compile(r'(\d*?d)\s*?()')

        flight_duration = flight_duration_pat.findall(temp)
        for each_time in flight_duration:
            day_num = day_pat.findall(each_time)
            hour_num = hour_pat.findall(each_time)
            min_num = min_pat.findall(each_time)
            if day_num != []:
                day_num_temp = int(day_num[0])
            else:
                day_num_temp = 0

            if hour_num != []:
                hour_num_temp = int(hour_num[0])
            else:
                hour_num_temp = 0

            if min_num != []:
                min_num_temp = int(min_num[0])
            else:
                min_num_temp = 0

            flight_dur = day_num_temp * 86400 + hour_num_temp * 3600 + min_num_temp * 60

        every_flight.append(flight_dur)

        """
        #get waiting time
        waiting_time_pat = re.compile(r'<div class="flight-leg2 fl-layover">(.*?)</div>')
        waiting_time = waiting_time_pat.findall(temp)
        """

        #get tax
        tax = -1.0
        every_flight.append(tax)

        #get surcharge
        surcharge = -1.0
        every_flight.append(surcharge)

        #get currency
        currency = "CNY"
        every_flight.append(currency)

        #get seat type
        seat_type = '经济舱'
        every_flight.append(seat_type)

         #get return rule
        return_rule = ''
        every_flight.append(return_rule)

        tickets = []
        tickets_info = tickets_info_pat.findall(temp)

        for each_ticket in tickets_info:
            ticket = []
            #get tickets price
            tickets_price_temp = tickets_price_pat.findall(each_ticket)[0]
            m = tickets_price_temp.find('>') + 1
            ticket_price = tickets_price_temp[m:].replace(',','')
            ticket.append(ticket_price)

            #get ticket source
            ticket_web = tickets_web_pat.findall(each_ticket)[0]
            blnum = ticket_web.rfind('/')
            dnum = ticket_web.rfind('.')
            ticket_web_name = ticket_web[blnum+1:dnum].replace('-','_')
            m = ticket_web_name.find('.')
            if m > 0:
                ticket_web_name = ticket_web_name[:m]
            ticket.append('wego::' + ticket_web_name)

            #get others tickets links
            ticket_link = tickets_links_pat.findall(each_ticket)[0]
            ticket.append(ticket_link)
            tickets.append(ticket)
        every_flight.append(tickets)

        #get stops
        stops_temp = stops_pat.findall(every_flight[0])
        stops = len(stops_temp)
        every_flight.append(stops)

        #get update time
        update_time = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
        every_flight.append(update_time)

        all_info.append(every_flight)

    for x in all_info:
        for y in range(len(x[13])):
            flight = Flight()
            flight.flight_no = x[0]
            flight.plane_no = 'NULL'#x[1]
            flight.airline = x[2]
            flight.dept_id = x[3]
            flight.dest_id = x[4]
            flight.dept_time = x[5]
            flight.dest_time = x[6]
            flight.dur = x[7]
            flight.price = x[13][y][0]
            flight.tax = x[8]
            flight.surcharge = x[9]
            flight.currency = x[10]
            flight.seat_type = x[11]
            flight.source = x[13][y][1]
            flight.return_rule = 'NULL'#x[12]
            #flight.book_url = 'http://www.wego.cn' + x[13][y][2]
            flight.stop = x[14]
            
            if 'T' in flight.dept_time:
                flight.dept_day = flight.dept_time.split('T')[0]
            else:
                pass
        

            flight_t = (flight.flight_no,flight.plane_no,flight.airline,flight.dept_id,flight.dest_id,\
                             flight.dept_day,flight.dept_time,flight.dest_time,flight.dur,flight.price,\
                             flight.tax,flight.surcharge,flight.currency,flight.seat_type,flight.source,\
                             flight.return_rule,flight.stop)
            flights.append(flight_t)
    return flights


def pageParser(content):
    if len(content) < 200:
        logger.error( '[Error in PageParser] [content.len = ' + str(len(content)) + ']')
        return 0

    page_num_temp = ''
    page_num = 0
    try:
        page_num_temp = page_pat.findall(content)[0]
    except Exception,e:
        logger.error( "page_num_temp Error: %s" %str(e))
        return page_num
    try:
        if int(page_num_temp) % 30 == 0:
            page_num = int(page_num_temp) / 30
        else:
            page_num = int(page_num_temp) / 30 + 1
    except Exception,e:
        logger.error( "pageParser Error: %s" %str(e))
    return page_num

def wego_request_parser(content):

    result = -1
    
    try:
        infos = content.split('|')
        flight_info = infos[0].strip()
        time_info = infos[1].strip()
        ticketsource = infos[2].strip()

        flight_no = flight_info.split('-')[0]
        dept_id,arr_id = flight_info.split('-')[1],flight_info.split('-')[2]

        #date：20140510，time：09:10
        dept_day,dept_hour = time_info.split('_')[0],time_info.split('_')[1]

        dept_date = dept_day[0:4] + '-' + dept_day[4:6] + '-' + dept_day[6:]#2014-05-10
        dept_min = 60 * int(dept_hour.split(':')[0]) + int(dept_hour.split(':')[1]) - 30
        if dept_min < 0:
            dept_min = 0
        dept_time = dept_date + 'T' + dept_hour + ':00'
    except Exception,e:
        logger.error('wegoFlight Content Error: cannot extract information from %s'%content)
        return result

    #获取代理
    p = get_proxy()
    
    #获取初始url
    url_temp = get_url(dept_id,arr_id,dept_date)
    search_id = get_search_id(url_temp)

    if search_id == '':
        logger.error('Search_Id Error: get Search_Id failed')
        return result

    trip_id = get_trip_id(dept_id,arr_id,dept_date)
    
    #使用初始url，获取要爬取的页面，page表示一共有多少页
    start_url = get_start_url(search_id,trip_id) + '&outbound_departure_day_time_min=' + str(dept_min)
    content_temp = crawl_single_page(start_url,proxy = p, n=1, Host="www.wego.cn", Accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
    if content_temp == "":
        logger.error('Proxy Error: htmlcontent is null with proxy: %s'%p)
        invalid_proxy(p)
        return result

    page_num = 0 
    page_num = pageParser(content_temp)
    page_num_get = 0

    if  page_num == 0:
        logger.info('Parser Error: cannot find flights with %s - %s'%(dept_id,arr_id))
        return result
    
    #拼出要爬取的urls
    url_list = get_flight_url(search_id,trip_id,page_num)
    paras = []
    for url in url_list:
        #time.sleep(1)
        htmlcontent = crawl_single_page(url+'&outbound_departure_day_time_min=' + str(dept_min), n=1, proxy = p, Host="www.wego.cn", Accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
        if htmlcontent != "":
            paras = parser(htmlcontent)#将爬取的页面提取出flight信息
            for para in paras:
                if para[3] == dept_id and para[4] == arr_id and para[6] == dept_time and para[0] == flight_no and para[14] == ticketsource:
                    result = para[9]
                    logger.info('update price successful from wego by ticketsource %s'%ticketsource)
                    return result
        else:
            continue
    
    logger.info('update price failed from wego by %s'%content)

    return result

if __name__ == "__main__":

    content = 'IB8977_BA7052_BA1342&VLC&LBA&2014-04-20T18:50:00&wego::ebookers'

    result = wego_request_parser(content)

    print result
