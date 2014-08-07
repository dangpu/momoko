#!/usr/bin/env python
#coding=UTF8

"""
    @author:fangwang
    @date:2014-06-11
    @desc: crawl and parse tongcheng flight data
"""

import json
import time
import re
import sys
import urllib
from time import sleep
import random

from common.logger import logger
from util.crawl_func import crawl_single_page
from common.class_common import Flight,EachFlight
from common.common import get_proxy, invalid_proxy
'''
from logger import logger
from crawl_func import crawl_single_page
from class_common import Flight,EachFlight
'''

reload(sys)
sys.setdefaultencoding('utf-8')

city_dict = {'CPH': 'CPH', 'LIN': 'MIL', 'AGB': 'AGB', 'BGO': 'BGO', 'HEL': 'HEL', 'NAP': 'NAP', \
        'LIS': 'LIS', 'NAY': 'BJS', 'BOD': 'BOD', 'FNI': 'FNI', 'AGP': 'AGP', 'PEK': 'BJS', \
        'SXB': 'SXB', 'SXF': 'BER', 'LYS': 'LYS', 'LBA': 'LBA', 'HAJ': 'HAJ', 'HAM': 'HAM', \
        'MRS': 'MRS', 'BFS': 'BFS', 'LPL': 'LPL', 'LHR': 'LON', 'SVQ': 'SVQ', 'VIE': 'VIE', \
        'BVA': 'PAR', 'MAD': 'MAD', 'LEJ': 'LEJ', 'MAN': 'MAN', 'TSF': 'VCE', 'FLR': 'FLR', \
        'BER': 'BER', 'RTM': 'RTM', 'VLC': 'VLC', 'SZG': 'SZG', 'OSL': 'OSL', 'AMS': 'AMS', \
        'BUD': 'BUD', 'STO': 'STO', 'TRN': 'TRN', 'BLQ': 'BLQ', 'PRG': 'PRG', 'GRX': 'GRX', \
        'SHA': 'SHA', 'OXF': 'OXF', 'PSA': 'PSA', 'MXP': 'MIL', 'LCY': 'LON', 'INN': 'INN', \
        'ANR': 'ANR ','OPO': 'OPO', 'BCN': 'BCN', 'LUX': 'LUX', 'GLA': 'GLA', 'MUC': 'MUC', \
        'LUG': 'LUG', 'CGN': 'CGN', 'BSL': 'BSL', 'PMF': 'MIL', 'PVG': 'SHA', 'SEN': 'LON', \
        'NUE': 'NUE', 'VRN': 'VRN', 'FCO': 'ROM', 'FRA': 'FRA', 'WAW': 'WAW', 'DUS': 'DUS', \
        'LTN': 'LON', 'CDG': 'PAR', 'MMX': 'MMA', 'ORY': 'PAR', 'BRU': 'BRU', 'EDI': 'EDI', \
        'BRS': 'BRS', 'BRN': 'BRN', 'BRE': 'BRE', 'CIA': 'ROM', 'TXL': 'BER', 'VCE': 'VCE', \
        'STN': 'LON', 'GVA': 'GVA', 'GOA': 'GOA', 'KLV': 'KLV', 'STR': 'STR', 'GOT': 'GOT', \
        'ZRH': 'ZRH', 'BHD': 'BFS', 'NCE': 'NCE', 'BHX': 'BHX', 'NCL': 'NCL', 'LGW': 'LON', \
        'ARN': 'STO'}

city_dict_cn = {"CPH": "哥本哈根", "LIN": "米兰", "AGB": "奥格斯堡", "BGO": "卑尔根", "HEL": "赫尔辛基", \
        "NAP": "那不勒斯", "LIS": "里斯本", "NAY": "北京", "BOD": "波尔多", "FNI": "尼姆", "AGP": "马拉加", \
        "PEK": "北京", "SXB": "斯特拉斯堡", "SXF": "柏林", "LYS": "里昂", "LBA": "利兹", "HAJ": "汉诺威", \
        "HAM": "汉堡", "MRS": "马赛", "BFS": "贝尔法斯特", "LPL": "利物浦", "LHR": "伦敦", "SVQ": "塞维利亚", \
        "VIE": "维也纳", "BVA": "巴黎", "MAD": "马德里", "LEJ": "莱比锡", "MAN": "曼彻斯特", "TSF": "威尼斯", \
        "FLR": "佛罗伦萨", "BER": "柏林", "RTM": "鹿特丹", "VLC": "瓦伦西亚", "SZG": "萨尔茨堡", "OSL": "奥斯陆", \
        "AMS": "阿姆斯特丹", "BUD": "布达佩斯", "STO": "斯德哥尔摩", "TRN": "都灵", "BLQ": "博洛尼亚", \
        "PRG": "布拉格", "GRX": "格拉纳达", "SHA": "上海", "OXF": "牛津", "PSA": "比萨", "MXP": "米兰", "LCY": "伦敦", \
        "INN": "因斯布鲁克", "ANR": "安特卫普", "OPO": "波尔图", "BCN": "巴塞罗那", "LUX": "卢森堡", \
        "GLA": "格拉斯哥", "MUC": "慕尼黑", "LUG": "卢加诺", "CGN": "科隆", "BSL": "巴塞尔", "PMF": "米兰", \
        "PVG": "上海", "SEN": "伦敦", "NUE": "纽伦堡", "VRN": "维罗纳", "FCO": "罗马", "FRA": "法兰克福", \
        "WAW": "华沙", "DUS": "杜塞尔多夫", "LTN": "伦敦", "CDG": "巴黎", "MMX": "马尔默", "ORY": "巴黎", \
        "BRU": "布鲁塞尔", "EDI": "爱丁堡", "BRS": "布里斯托尔", "BRN": "伯尔尼", "BRE": "不莱梅", \
        "CIA": "罗马", "TXL": "柏林", "VCE": "威尼斯", "STN": "伦敦", "GVA": "日内瓦", "GOA": "热那亚", \
        "KLV": "卡罗维发利", "STR": "斯图加特", "GOT": "哥德堡", "ZRH": "苏黎世", "BHD": "贝尔法斯特", \
        "NCE": "尼斯", "BHX": "伯明翰", "NCL": "纽卡斯尔", "LGW": "伦敦", "ARN": "斯德哥尔摩"}

url_pat1 = re.compile(r'tc10805565235\((.*?)\);"', re.S)
search_code_pat = re.compile(r'code:"(.*?)"', re.S)

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

CONTENT_LEN = 100

def tongcheng_task_parser(taskcontent):

    result = {}
    flight = {}
    ticket = []
    result['para'] = {'flight':flight,'ticket':ticket}
    result['error'] = 0

    taskcontent.encode('utf-8')

    try:
        info_list = taskcontent.split('&')

        dept_id, dest_id, dept_city, dest_city, dept_date_temp = info_list[0], info_list[1], info_list[2], info_list[3], info_list[4]
        dept_day = dept_date_temp[:4] + '-' + dept_date_temp[4:6] + '-' +dept_date_temp[6:]

    except Exception, e:
        logger.error('tongchengFlight,wrong content format with %s'%(taskcontent))
        result['error'] = TASK_ERROR
        return result

    p = get_proxy(source='tongchengFlight')
    #p = crawl_single_page('http://114.215.168.168:8086/proxy')
    #p = None

    if p == None:
        result['error'] = PROXY_NONE
        return result

    url = get_url(dept_city, dest_city, dept_day, dept_id, dest_id ,p)

    if url == 'proxy_forbidden':
        invalid_proxy(proxy = p, source='tongchengFlight')
        result['error'] = PROXY_FORBIDDEN
        return result

    if url != '':
        page = crawl_single_page(url, proxy = p)
        print page
    else:
        logger.error('tongchengFlight: Get url failed!')
        invalid_proxy(proxy = p, source='tongchengFlight')
        result['error'] = PROXY_INVALID
        return result

    if page != '' and len(page) > CONTENT_LEN:
        flights = ParsePage(page)
    else:
        logger.error('tongchengFlight: Crawl page failed!')
        invalid_proxy(proxy = p, source='tongchengFlight')
        result['error'] = PROXY_INVALID
        return result

    if flights != {'ticket':[], 'flight':{}}:
        flight = flights['flight']
        ticket = flights['ticket']

    else:
        print 'No result parsed'
        result['error'] = DATA_NONE

    try:
        next_url = get_next_url(page, url)
        next_page = crawl_single_page(next_url, proxy=p)
        print next_page
        if next_page != '' and len(next_page) > CONTENT_LEN:
            next_flights = ParsePage(next_page)
            next_flight = next_flights['flight']
            next_ticket = next_flights['ticket']
            flight.update(next_flight)
            ticket += next_ticket
        else:
            print 'Parse the next page failed'
    except Exception, e:
        print str(e)

    result['para']['flight'] = flight
    result['para']['ticket'] = ticket
    return result


def tongcheng_request_parser(content):

    result = -1
    content.encode('utf-8')

    try:
        info_list = content.split('|')
        flight_info = info_list[0]
        time_info = info_list[1]
        source = info_list[2]

        flight_no = flight_info.split('-')[0]
        dept_id = flight_info.split('-')[1]
        dest_id = flight_info.split('-')[2]

        dept_day = time_info.split('_')[0]
        dept_minute = time_info.split('_')[1] +':00'
        dept_city = city_dict[dept_id]
        dest_city = city_dict[dest_id]
        dept_city_cn = city_dict_cn[dept_id].encode('utf-8')
        dest_city_cn = city_dict_cn[dest_id].encode('utf-8')

        dept_date = dept_day[:4] + '-' + dept_day[4:6] + '-' +dept_day[6:]
        dept_time = dept_date + 'T' + dept_minute
    except Exception, e:
        logger.error('tongchengFlight: Wrong Content Format with %s'%content + str(e))
        return result

    url = get_url(dept_city_cn, dest_city_cn, dept_date, dept_city, dest_city)
    if url != '' and url != 'proxy_forbidden':
        page = crawl_single_page(url, proxy = None, Accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    else:
        return result

    if page != '' and len(page) > 100:
        result = ValidatePage(page,flight_no,dept_time)
        return result

    return result



def get_url(dept_city, dest_city, dept_date, dept_id, dest_id, proxy=None):
    parser_url = ''
    url_temp = 'http://www.ly.com/iflight/flightinterajax.aspx?action=SEARCHURL&airplaneInternatType=1&iOrgPort=' + \
               dept_city + '&iArvPort=' + dest_city + '&idtGoDate=' + dept_date + \
               '&idtBackDate=时间/日期&sel_inCabinType=Y&sel_inPassengersType=1&sel_inAdult=1&sel_inChild=0' + \
               '&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名' + \
               '&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名' + \
               '&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&callback=tc10805565235'

    page1 = crawl_single_page(url_temp, proxy=proxy,referer='http://www.ly.com')
    print page1

    try:
        num01 = page1.find('(')
        num02 = page1.rfind(')')
        json_content_temp = page1[num01+1:num02]
        json_temp1 = json.loads(json_content_temp)
        if json_temp1['state'] == 100:
            url_temp1 =  json_temp1['href']
        else:
            return parser_url
    except Exception,e:
        if page1.find('a5') != -1:
            parser_url = 'proxy_forbidden'
        return parser_url
    url_temp2 = 'http://www.ly.com' + url_temp1

    page2 = crawl_single_page(url_temp2,proxy = proxy, referer=url_temp2)
    #print page2
    try:
        search_code = search_code_pat.findall(page2)[0]
    except Exception,e:
        logger.error('tongchengFlight: Can not get search code!' + str(e))
        return parser_url

    parser_url = 'http://www.ly.com/iflight/AjaxHandler.ashx?action=GRADATIONQUERYFLIGHT&TravelType=0&Departure=' + \
                 dept_city + '&DepartureC=' + dept_id + '&Arrival=' + dest_city + '&ArrivalC=' + dest_id + \
                 '&DepartureDate=' + dept_date + '&ReturnDate=1900-01-01&AdultNum=1&ChildNum=0&CabinType=1&FlatType=1' \
                 + '&PassengerType=1&pageCode=' + search_code + '&JingJiaSearchGuid=&iid=' + str(random.random())

    return parser_url


def get_next_url(content, url_temp):
    next_url = ''
    try:
        if content != '' and len(content) > CONTENT_LEN:
            content_json = json.loads(content)
            guid_content = content_json['Guid']
            next_url = url_temp + '&PreGuid=' + guid_content + '&AssignQuery=TravelFusion'
        else:
            return next_url
    except Exception, e:
        print str(e)
        return next_url

    return next_url


def ParsePage(content):
    flight_dict = {}
    ticket_list = []
    flights = {'ticket':ticket_list, 'flight':flight_dict}

    try:
        if content != '' and len(content) > 100:
            content_json = json.loads(content)
        else:
            return  flights
    except Exception,e :
        logger.error('tongchengFlight:: Crawl this page failed' + str(e))
        return flights

    if 'OriginDestinationOption' in content_json.keys():
        for each_flight_json in content_json['OriginDestinationOption']:
            try:
                flight = Flight()

                flight_nums = len(each_flight_json['FlightSegment'])

                flight.flight_no = each_flight_json['FlightNos'].replace('-','_')
                flight.dept_id = each_flight_json['AirPorts'][:3]
                flight.dest_id = each_flight_json['AirPorts'][-3:]

                dept_time_tamp = each_flight_json['FlightSegment'][0]['DepartureDate'][6:-2]
                dest_time_tamp = each_flight_json['FlightSegment'][-1]['ArrivalDate'][6:-2]
                flight_time_json = each_flight_json['FlightSegment']

                #parse eachflight content
                for each_flight_content in flight_time_json:
                    try:
                        eachflight = EachFlight()
                        eachflight.airline = each_flight_content['AirCompanyName']
                        #print eachflight.airline
                        eachflight.dept_id = each_flight_content['DepartureAirport']
                        #print eachflight.dept_id
                        eachflight.dest_id = each_flight_content['ArrivalAirport']
                        #print eachflight.dest_id
                        #print each_flight_content['Equipment']
                        eachflight.plane_no = each_flight_content['Equipment']
                        eachflight.flight_no = each_flight_content['AirCompanyCode'] + each_flight_content['FlightNumber']
                        eachflight.flight_key = eachflight.flight_no + '_' + eachflight.dept_id + '_' + eachflight.dest_id
                        #print each_flight_content['ArrivalDate'][6:-2]
                        eachflight.dest_time = time.strftime('%Y-%m-%d %H:%M:%S', \
                                time.localtime(float(str(each_flight_content['ArrivalDate'][6:-2])[:-3]))).replace(' ','T')
                        eachflight.dept_time = time.strftime('%Y-%m-%d %H:%M:%S', \
                                time.localtime(float(str(each_flight_content['DepartureDate'][6:-2])[:-3]))).replace(' ','T')

                        fly_time_content = each_flight_content['FlyTime']
                        #print fly_time_content
                        if '小' not in  fly_time_content:
                            if '时' in fly_time_content:
                                if '分' in fly_time_content:
                                    hour_num_str = fly_time_content[:fly_time_content.find('时')]
                                    min_num_str = fly_time_content[fly_time_content.find('时')+1:fly_time_content.find('分')]
                                else:
                                    hour_num_str = fly_time_content[:fly_time_content.find('时')]
                            else:
                                hour_num_str = '0'
                                if '分' in fly_time_content:
                                    min_num_str = fly_time_content[:fly_time_content.find('分')]
                                else:
                                    min_num_str = '0'
                        else:
                            hour_num_str = fly_time_content[:fly_time_content.find('小')]

                            if '分' in fly_time_content:
                                min_num_str = fly_time_content[fly_time_content.find('时')+1:fly_time_content.find('分')]

                        eachflight.dur = int(hour_num_str) * 3600 + int(min_num_str) * 60

                        eachflight_tuple = (eachflight.flight_no, eachflight.airline, eachflight.plane_no, \
                            eachflight.dept_id, eachflight.dest_id, eachflight.dept_time, eachflight.dest_time, \
                            eachflight.dur)
                        flight_dict.update({eachflight.flight_key:eachflight_tuple})
                        #print eachflight_tuple
                    except Exception, e:
                        print 'Parse this flight with error: ' + str(e)
                        continue

                if flight_nums == 1:
                    time_str_temp = flight_time_json[0]['FlyTime'].encode('utf8')

                    str_num = time_str_temp.find('小')
                    if str_num < 0:
                        h_nums_str = time_str_temp[:time_str_temp.find('时')].strip()
                        m_nums_str = time_str_temp[time_str_temp.find('时')+3:time_str_temp.find('分')].strip()
                    else:
                        h_nums_str = time_str_temp[:time_str_temp.find('小时')].strip()
                        m_nums_str = time_str_temp[time_str_temp.find('小时')+6:time_str_temp.find('分')].strip()
                    flight.dur = 0
                    if h_nums_str != '':
                        flight.dur += int(h_nums_str) * 3600
                    if m_nums_str != '':
                        flight.dur += int(m_nums_str) * 60
                else:
                    flight.dur = 0
                    for i in range(flight_nums):
                        time_str_temp = flight_time_json[i]['FlyTime'].encode('utf8')

                        str_num = time_str_temp.find('小')
                        if str_num > 0:
                            h_nums_str = time_str_temp[:time_str_temp.find('小时')].strip()
                            m_nums_str = time_str_temp[time_str_temp.find('小时')+6:time_str_temp.find('分')].strip()
                        else:
                            h_nums_str = time_str_temp[:time_str_temp.find('时')].strip()
                            m_nums_str = time_str_temp[time_str_temp.find('时')+3:time_str_temp.find('分')].strip()
                        if h_nums_str != '':
                            flight.dur += int(h_nums_str) * 3600
                        if m_nums_str != '':
                            flight.dur += int(m_nums_str) * 60

                    for i in range(1,flight_nums):
                        dept_time_temp = each_flight_json['FlightSegment'][i]['DepartureDate'][6:-2]
                        dest_time_temp = each_flight_json['FlightSegment'][i-1]['ArrivalDate'][6:-2]
                        flight.dur += (int(dept_time_temp) - int(dest_time_temp)) / 1000
                flight.dept_time = time.strftime('%Y-%m-%d %H:%M:%S', \
                        time.localtime(float(str(dept_time_tamp)[:-3]))).replace(' ','T')
                flight.dest_time = time.strftime('%Y-%m-%d %H:%M:%S', \
                        time.localtime(float(str(dest_time_tamp)[:-3]))).replace(' ','T')
                flight.dept_day = flight.dept_time.split('T')[0]
                flight.source = 'tongcheng::tongcheng'
                flight.stop = int(flight_nums) - 1
                flight.currency = 'CNY'
                flight.price = each_flight_json['FareInfo'][0]['TCPrice_Audlt']
                flight.tax = each_flight_json['FareInfo'][0]['TaxPrice_Audlt']

                airline_temp = ''
                plane_no_temp = ''

                for i in range(flight_nums):
                    plane_no_temp = plane_no_temp + \
                            each_flight_json['FlightSegment'][i]['Equipment'] + '_'

                    airline_temp = airline_temp + \
                            each_flight_json['FlightSegment'][i]['AirCompanyName'] + '_'

                flight.plane_no = plane_no_temp[:-1]
                flight.airline = airline_temp[:-1]
                flight.seat_type = '经济舱'

                flight_tuple = (flight.flight_no, flight.plane_no, flight.airline, \
                        flight.dept_id, flight.dest_id, flight.dept_day, flight.dept_time, \
                        flight.dest_time, flight.dur, flight.price, flight.tax, \
                        flight.surcharge, flight.currency, flight.seat_type, \
                        flight.source, flight.return_rule, flight.stop)
                ticket_list.append(flight_tuple)
            except Exception, e:
                #logger.info('tongchengFlight: Parse this flight failed!' + str(e))
                continue
    else:
        logger.info('tongchengFlight: Parse Page Failed')
        return flights

    flights = {'flight':flight_dict, 'ticket':ticket_list}
    return flights


def ValidatePage(content,flight_no,dept_time):
    result = -1

    if content != '' and len(content) > 100:

        content_json = json.loads(content)
        if 'OriginDestinationOption' in content_json.keys():
            for each_flight_json in content_json['OriginDestinationOption']:
                try:
                    flight = Flight()

                    flight_nums = len(each_flight_json['FlightSegment'])

                    flight.flight_no = each_flight_json['FlightNos'].replace('-','_')

                    dept_time_temp = each_flight_json['FlightSegment'][0]['DepartureDate'][6:-2]
                    dest_time_temp = each_flight_json['FlightSegment'][-1]['ArrivalDate'][6:-2]

                    flight.dept_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(str(dept_time_temp)[:-3]))).replace(' ','T')
                    flight.dest_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(str(dest_time_temp)[:-3]))).replace(' ','T')
                    flight.dept_day = flight.dept_time.split('T')[0]
                    flight.price = each_flight_json['FareInfo'][0]['TCPrice_Audlt']

                    if flight.flight_no == flight_no and flight.dept_time == dept_time:
                        result = flight.price
                        return result
                except:
                    continue
        else:
            return result

    return result

if __name__ == '__main__':

    taskcontent = 'LON&PAR&伦敦&巴黎&20140802'

    result1 = tongcheng_task_parser(taskcontent)
    print str(result1)
    print len(result1['para']['ticket'])

    '''
    content = 'SU201_SU2458-PEK-CDG|20140602_02:30|tongcheng::tongcheng'

    result2 = tongcheng_request_parser(content)
    print str(result2)
    '''
