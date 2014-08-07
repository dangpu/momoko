#!/usr/bin/env python
#coding=utf8

'''
    @author: nemo
    @date: 2014-06-09
    @desc:
        东方航空单程机票解析
'''

import re
import time
import sys
import random
from common.crawler import UrllibCrawler
import json
from common.class_common import Flight, EachFlight
from util.crawl_func import request_post_data
from common.logger import logger
from common.common import get_proxy, invalid_proxy

reload(sys)
sys.setdefaultencoding('utf-8')

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

AIRPORT_CITY_CN_DICT = {'CPH': '哥本哈根', 'LIN': '米兰', 'AGB': '奥格斯堡', 'BGO': '卑尔根', 'HEL': '赫尔辛基', \
        'NAP': '那不勒斯', 'LIS': '里斯本', 'NAY': '北京', 'BOD': '波尔多', 'FNI': '尼姆', 'AGP': '马拉加', \
        'PEK': '北京', 'SXB': '斯特拉斯堡', 'SXF': '柏林', 'LYS': '里昂', 'LBA': '利兹', 'HAJ': '汉诺威', \
        'HAM': '汉堡', 'MRS': '马赛', 'BFS': '贝尔法斯特', 'LPL': '利物浦', 'LHR': '伦敦', 'SVQ': '塞维利亚', \
        'VIE': '维也纳', 'BVA': '巴黎', 'MAD': '马德里', 'LEJ': '莱比锡', 'MAN': '曼彻斯特', 'TSF': '威尼斯', \
        'FLR': '佛罗伦萨', 'BER': '柏林', 'RTM': '鹿特丹', 'VLC': '瓦伦西亚', 'SZG': '萨尔茨堡', 'OSL': '奥斯陆', \
        'AMS': '阿姆斯特丹', 'BUD': '布达佩斯', 'STO': '斯德哥尔摩', 'TRN': '都灵', 'BLQ': '博洛尼亚', \
        'PRG': '布拉格', 'GRX': '格拉纳达', 'SHA': '上海', 'OXF': '牛津', 'PSA': '比萨', 'MXP': '米兰', 'LCY': '伦敦', \
        'INN': '因斯布鲁克', 'ANR': '安特卫普', 'OPO': '波尔图', 'BCN': '巴塞罗那', 'LUX': '卢森堡', \
        'GLA': '格拉斯哥', 'MUC': '慕尼黑', 'LUG': '卢加诺', 'CGN': '科隆', 'BSL': '巴塞尔', 'PMF': '米兰', \
        'PVG': '上海', 'SEN': '伦敦', 'NUE': '纽伦堡', 'VRN': '维罗纳', 'FCO': '罗马', 'FRA': '法兰克福', \
        'WAW': '华沙', 'DUS': '杜塞尔多夫', 'LTN': '伦敦', 'CDG': '巴黎', 'MMX': '马尔默', 'ORY': '巴黎', \
        'BRU': '布鲁塞尔', 'EDI': '爱丁堡', 'BRS': '布里斯托尔', 'BRN': '伯尔尼', 'BRE': '不莱梅', \
        'CIA': '罗马', 'TXL': '柏林', 'VCE': '威尼斯', 'STN': '伦敦', 'GVA': '日内瓦', 'GOA': '热那亚', \
        'KLV': '卡罗维发利', 'STR': '斯图加特', 'GOT': '哥德堡', 'ZRH': '苏黎世', 'BHD': '贝尔法斯特', \
        'NCE': '尼斯', 'BHX': '伯明翰', 'NCL': '纽卡斯尔', 'LGW': '伦敦', 'ARN': '斯德哥尔摩'}

AIRPORT_CITY_DICT = {'CPH':'CPH','LIN':'MIL','AGB':'AGB','BGO':'BGO','HEL':'HEL','NAP':'NAP','LIS':'LIS','BOD':'BOD','FNI':'FNI','AGP':'AGP','SXB':'SXB',\
        'SXF':'BER','LYS':'LYS','LBA':'LBA','HAJ':'HAJ','HAM':'HAM','MRS':'MRS','BFS':'BFS','LPL':'LPL','LHR':'LON','SVQ':'SVQ','VIE':'VIE','BVA':'PAR',\
        'MAD':'MAD','BRU':'BRU','MAN':'MAN','TSF':'VCE','FLR':'FLR','BER':'BER','RTM':'RTM','VLC':'VLC','SZG':'SZG','OSL':'OSL','AMS':'AMS','BUD':'BUD',\
        'STO':'STO','TRN':'TRN','BLQ':'BLQ','PRG':'PRG','GRX':'GRX','OXF':'OXF','PSA':'PSA','MXP':'MIL','LCY':'LON','INN':'INN','ANR':'ANR','OPO':'OPO',\
        'BCN':'BCN','LUX':'LUX','GLA':'GLA','MUC':'MUC','LUG':'LUG','CGN':'CGN','BSL':'BSL','PMF':'MIL','SEN':'LON','NUE':'NUE','VRN':'VRN','FCO':'ROM',\
        'FRA':'FRA','WAW':'WAW','DUS':'DUS','LTN':'LON','CDG':'PAR','MMX':'MMA','ORY':'PAR','LEJ':'LEJ','EDI':'EDI','BRS':'BRS','BRN':'BRN','BRE':'BRE',\
        'CIA':'ROM','TXL':'BER','VCE':'VCE','STN':'LON','GVA':'GVA','GOA':'GOA','KLV':'KLV','STR':'STR','GOT':'GOT','ZRH':'ZRH','BHD':'BFS','LGW':'LON',\
        'BHX':'BHX','NCL':'NCL','NCE':'NCE','ARN':'STO','PEK':'BJS','PVG':'SHA','SHA':'SHA','NAJ':'BJS','CAN':'CAN','SZX':'SZX'}

AIRPORT_COUNTRY_DICT = {'CPH': 'DK', 'LIN': 'IT', 'AGB': 'DE', 'BGO': 'NO', 'HEL': 'FI', 'NAP': 'IT', 'LIS': 'PT', 'BOD': 'FR', 'FNI': 'FR', 'AGP': 'ES', \
        'SXB': 'FR', 'SXF': 'DE', 'LYS': 'FR', 'LBA': 'GB', 'HAJ': 'DE', 'HAM': 'DE', 'MRS': 'FR', 'BFS': 'GB', 'LPL': 'GB', 'LHR': 'GB', 'SVQ': 'ES', \
        'VIE': 'AT', 'BVA': 'FR', 'MAD': 'ES', 'BRU': 'BE', 'MAN': 'GB', 'TSF': 'IT', 'FLR': 'IT', 'BER': 'DE', 'RTM': 'NL', 'VLC': 'ES', 'SZG': 'AT', \
        'OSL': 'NO', 'AMS': 'NL', 'BUD': 'HU', 'STO': 'SE', 'TRN': 'IT', 'BLQ': 'IT', 'PRG': 'CZ', 'GRX': 'ES', 'OXF': 'GB', 'PSA': 'IT', 'MXP': 'IT', \
        'LCY': 'GB', 'INN': 'AT', 'ANR': 'BE', 'OPO': 'PT', 'BCN': 'ES', 'LUX': 'LU', 'GLA': 'GB', 'MUC': 'DE', 'LUG': 'CH', 'CGN': 'DE', 'BSL': 'CH', \
        'PMF': 'IT', 'SEN': 'GB', 'NUE': 'DE', 'VRN': 'IT', 'FCO': 'IT', 'FRA': 'DE', 'WAW': 'PL', 'DUS': 'DE', 'LTN': 'GB', 'CDG': 'FR', 'MMX': 'SE', \
        'ORY': 'FR', 'LEJ': 'DE', 'EDI': 'GB', 'BRS': 'GB', 'BRN': 'CH', 'BRE': 'DE', 'CIA': 'IT', 'TXL': 'DE', 'VCE': 'IT', 'STN': 'GB', 'GVA': 'CH', \
        'GOA': 'IT', 'KLV': 'CZ', 'STR': 'DE', 'GOT': 'SE', 'ZRH': 'CH', 'BHD': 'GB', 'LGW': 'GB', 'BHX': 'GB', 'NCL': 'GB', 'NCE': 'GR', 'ARN': 'SE', \
        'PEK': 'CN', 'NAY': 'CN', 'PVG': 'CN', 'SHA': 'CN', 'SZX': 'CN', 'CAN': 'CN'}

CN_AIRPORT = ['NAY','PEK','PVG','SHA','SZX','CAN']

SearchURL = 'http://easternmiles.ceair.com/booking/flight-search!doFlightSearch.shtml?rand=%s'
RefererURL = 'http://easternmiles.ceair.com/flight/%s-%s-%s_CNY.html' #sha-gva-140627

def hm_to_sec(hm):
    '''
        13(h):55(min) -> 13 * 3600 + 55 * 60
    '''
    
    try:
        h, m = int(hm.split(':')[0]), int(hm.split(':')[1])
        
    except Exception,e:
        return 0

    sec = h * 3600 + m * 60

    return sec

def standard_timeformatter(orig_time):
    '''
        2014-06-17 13:55 -> 2014-06-17T13:55:00
    '''

    return orig_time.replace(' ','T') + ':00'


def getPostData(dept_id,dest_id,dept_date):
    
    postdata = None

    try:
        postdata = {'tripType':'OW','adtCount':1,'chdCount':0,'infCount':0,'currency':'CNY','sortType':'t'}
        postdata['segmentList'] = []

        segmentInfo = {'deptCdTxt':AIRPORT_CITY_CN_DICT[dept_id],'deptCd':dept_id+'#','deptNation':AIRPORT_COUNTRY_DICT[dept_id],\
                'deptRegion':'CN','deptCityCode':AIRPORT_CITY_DICT[dept_id],\
                'arrCd':dest_id+'#','arrCdTxt':AIRPORT_CITY_CN_DICT[dest_id],'arrNation':AIRPORT_COUNTRY_DICT[dest_id],'arrRegion':'EU',\
                'arrCityCode':AIRPORT_CITY_DICT[dest_id],'deptDt':dept_date}
        
        if dept_id in CN_AIRPORT:
            segmentInfo['deptRegion'] = 'CN'
        else:
            segmentInfo['deptRegion'] = 'EU'

        if dest_id in CN_AIRPORT:
            segmentInfo['arrRegion'] = 'CN'
        else:
            segmentInfo['arrRegion'] = 'EU'

        postdata['segmentList'].append(segmentInfo)

    except Exception,e:
        print str(e)
        return None
    import json

    return {'searchCond':json.dumps(postdata)}

def ceair_page_parser(content):
    
    flights = {}
    tickets = []

    infos = json.loads(content[content.find('{'):])
    
    if infos['resultMsg'] != '':

        return tickets, flights

    currency = infos['currency']
    all_flights = infos['tripItemList'][0]['airRoutingList']

    for one_flight in all_flights:
        flight_info = one_flight['flightList']

        flight = Flight()
        flight.source = 'ceair::ceair'
        flight.stop = len(flight_info) - 1
        flight.currency = currency

        flight_nos = []
        plane_types = []
        airlines = []
        
        durings = []
        wait_times = []
        
        flight.dept_id = flight_info[0]['deptCd']
        flight.dest_id = flight_info[-1]['arrCd']
        flight.dept_time = standard_timeformatter(flight_info[0]['deptTime'])
        flight.dest_time = standard_timeformatter(flight_info[-1]['arrTime'])
        flight.dept_day = flight_info[0]['deptTime'].split(' ')[0]
        
        for item in flight_info:

            eachflight = EachFlight()

            eachflight.flight_no = item['flightNo']
            eachflight.airline = '东方航空'
            eachflight.plane_no = item['acfamily']
            eachflight.dept_id = item['deptCd']
            eachflight.dest_id = item['arrCd']
            eachflight.dept_time = standard_timeformatter(item['deptTime'])
            eachflight.dest_time = standard_timeformatter(item['arrTime'])
            eachflight.dur = hm_to_sec(item['duration'])

            eachflight.flight_key = eachflight.flight_no + '_' + eachflight.dept_id + '_' + eachflight.dest_id

            flights[eachflight.flight_key] = (eachflight.flight_no, eachflight.airline, eachflight.plane_no, eachflight.dept_id, eachflight.dest_id, eachflight.dept_time, eachflight.dest_time, eachflight.dur)

            flight_nos.append(eachflight.flight_no)
            plane_types.append(eachflight.plane_no)
            airlines.append(eachflight.airline)

            durings.append(eachflight.dur)
            wait_times.append(hm_to_sec(item['stayTime']))

        flight.flight_no = ''
        for flight_no in flight_nos:
            flight.flight_no = flight.flight_no + flight_no + '_'
        flight.flight_no = flight.flight_no[:-1]

        flight.plane_no = ''
        for plane_type in plane_types:
            flight.plane_no = flight.plane_no + plane_type + '_'
        flight.plane_no = flight.plane_no[:-1]

        flight.airline = ''
        for airline in airlines:
            flight.airline = flight.airline + airline + '_'
        flight.airline = flight.airline[:-1]

        flight.dur = 0
        for during in durings:
            flight.dur = flight.dur + during
        
        for wait_time in wait_times:
            flight.dur = flight.dur + wait_time

        if one_flight['priceDisp']['economy'] != '':
            flight.seat_type = '经济舱'
            flight.price = int(one_flight['priceDisp']['economy'])

            flight_tuple = (flight.flight_no,flight.plane_no,flight.airline,flight.dept_id,flight.dest_id,flight.dept_day,\
                    flight.dept_time,flight.dest_time,flight.dur,flight.price,flight.tax,flight.surcharge,\
                    flight.currency,flight.seat_type,flight.source,flight.return_rule,flight.stop)

            tickets.append(flight_tuple)

        if one_flight['priceDisp']['business'] != '':
            flight.seat_type = '商务舱'
            flight.price = int(one_flight['priceDisp']['business'])
            flight_tuple = (flight.flight_no,flight.plane_no,flight.airline,flight.dept_id,flight.dest_id,flight.dept_day,\
                    flight.dept_time,flight.dest_time,flight.dur,flight.price,flight.tax,flight.surcharge,\
                    flight.currency,flight.seat_type,flight.source,flight.return_rule,flight.stop)

            tickets.append(flight_tuple)
    return tickets, flights

def ceair_task_parser(content):
    
    #初始化参数
    #返回para，改版后返回result
    result = {}
    result['para'] = {'ticket':[], 'flight':{ } }
    result['error'] = 0

    #解析字符串
    try:
        infos = content.strip().split('&')
        dept_id = infos[0]  #机场三字码
        dest_id = infos[1]  #机场三字码
        day, month, year = infos[2][6:], infos[2][4:6], infos[2][0:4]
        dept_date = year+'-'+month+'-'+day
        dept_date_url = year[-2:] + month + day #140627

    except Exception, e:
        logger.error('ceairFlight: Wrong Content Format with %s'%content)
        result['error'] = TASK_ERROR
        return result

    if AIRPORT_CITY_DICT.has_key(dept_id) == False or AIRPORT_CITY_DICT.has_key(dest_id) == False:
        logger.warning('ceairFlight: airport not in AIRPORT_CITY_DICT')
        result['error'] = DATA_NONE
        return result

    p = get_proxy(source = 'ceairFlight')

    if p == None:
        result['error'] = PROXY_NONE
        return result

    postdata = getPostData(dept_id,dest_id,dept_date)

    if postdata == '':
        result['error'] = UNKNOWN_TYPE
        return result
    
    rand = str(random.random())
    referer = RefererURL%(AIRPORT_CITY_DICT[dept_id].lower(), AIRPORT_CITY_DICT[dest_id].lower(), dept_date_url)
    searchurl = SearchURL%str(rand)

    #uc = crawler.UrllibCrawler()
    uc = UrllibCrawler()

    uc.get(referer)

    html = uc.post(searchurl, postdata, html_flag = True)

    tickets, flights = ceair_page_parser(html)
    if tickets == []:
        result['error'] = DATA_NONE
        return result

    result['para']['ticket'] = tickets
    result['para']['flight'] = flights 

    return result

def ceair_request_parser(content):
    
    result = -1

    return result

if __name__ == "__main__":

    content = 'PEK&LHR&20140627'

    result = ceair_task_parser(content)

    print result
