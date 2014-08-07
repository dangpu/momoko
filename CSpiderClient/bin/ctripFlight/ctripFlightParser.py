#!/usr/bin/env python
#coding=UTF8
'''
    @author: devin
    @desc: 抓取机票数据
'''

import datetime
from util.crawl_func import crawl_single_page
from lxml import etree
import re
import jsonlib
import urllib
import parser
from common.logger import logger
from common.common import get_proxy, invalid_proxy
from common.class_common import Flight

import sys

percentPattern = re.compile("(\d+)%")
numPattern = re.compile("\d+")
alphanumericPattern = re.compile("\w+")
classPattern = re.compile("p_f16_\d")

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

CN_AIRPORTS = set(['wus', 'tcz', 'nlt', 'jnz', 'wux', 'mfm', 'lds', 'juz', 'szx', 'jng', 'llb', 'wuh', 'llf',  \
        'hjj', 'tsn', 'hzg', 'hak', 'jic', 'ngb', 'weh', 'hzh', 'wua', 'jiu', 'dqa', 'jiq', 'hrb', 'lzy', 'shp',  \
        'kca', 'lcx', 'dat', 'hia', 'lzo', 'dyg', 'dax', 'bav', 'xmn', 'ynj', 'jhg', 'ddg', 'dig', 'bpl', 'hyn',  \
        'sha', 'aeb', 'she', 'ynz', 'ynt', 'bpx', 'ten', 'nbs', 'htn', 'nzh', 'mdg', 'tvs', 'ljg', 'lnj', 'hld',  \
        'dlc', 'iqm', 'jgn', 'fug', 'ycu', 'dsn', 'dlu', 'foc', 'jgs', 'goq', 'lum', 'cgo', 'xfn', 'hsn', 'cgd', 'cgq',  \
        'hkg', 'ntg', 'wef', 'ctu', 'kry', 'tcg', 'yus', 'kji', 'sjw', 'aku', 'lzh', 'krl', 'aka', 'acx', 'xnn', 'txn',  \
        'kwe', 'kwl', 'rkz', 'dnh', 'jjn', 'bjs', 'zat', 'tgo', 'het', 'xic', 'wuz', 'chg', 'swa', 'yin', 'xil', 'yih',  \
        'yiw', 'kow', 'ngq', 'kgt', 'nkg', 'yzy', 'wnh', 'ckg', 'jmu', 'aqg', 'gys', 'hmi', 'wnz', 'jzh', 'cif', 'zhy',  \
        'cih', 'zha', 'aat', 'iqn', 'tna', 'can', 'jdz', 'erl', 'fuo', 'hek', 'lya', 'czx', 'khn', 'nng', 'ohe', 'hlh',  \
        'bhy', 'hdg', 'lyg', 'pzi', 'xuz', 'nny', 'mxz', 'tao', 'ava', 'khg', 'enh', 'nao', 'mig', 'lyi', 'jxa', 'sia',  \
        'csx', 'hgh', 'eny', 'wxn', 'inc', 'aog', 'kmg', 'tyn', 'sym', 'ybp', 'lxa', 'bsd', 'syx', 'zuh', 'uyn', 'ndg',  \
        'tpe', 'urc', 'gyu', 'thq', 'lhw', 'doy', 'hfe'])

AIRPORT_CITY_DICT = {'CPH':'CPH','LIN':'MIL','AGB':'AGB','BGO':'BGO','HEL':'HEL','NAP':'NAP','LIS':'LIS','BOD':'BOD','FNI':'FNI','AGP':'AGP','SXB':'SXB',\
                'SXF':'BER','LYS':'LYS','LBA':'LBA','HAJ':'HAJ','HAM':'HAM','MRS':'MRS','BFS':'BFS','LPL':'LPL','LHR':'LON','SVQ':'SVQ','VIE':'VIE','BVA':'PAR',\
                'MAD':'MAD','BRU':'BRU','MAN':'MAN','TSF':'VCE','FLR':'FLR','BER':'BER','RTM':'RTM','VLC':'VLC','SZG':'SZG','OSL':'OSL','AMS':'AMS','BUD':'BUD',\
                'STO':'STO','TRN':'TRN','BLQ':'BLQ','PRG':'PRG','GRX':'GRX','OXF':'OXF','PSA':'PSA','MXP':'MIL','LCY':'LON','INN':'INN','ANR':'ANR','OPO':'OPO',\
                'BCN':'BCN','LUX':'LUX','GLA':'GLA','MUC':'MUC','LUG':'LUG','CGN':'CGN','BSL':'BSL','PMF':'MIL','SEN':'LON','NUE':'NUE','VRN':'VRN','FCO':'ROM',\
                'FRA':'FRA','WAW':'WAW','DUS':'DUS','LTN':'LON','CDG':'PAR','MMX':'MMA','ORY':'PAR','LEJ':'LEJ','EDI':'EDI','BRS':'BRS','BRN':'BRN','BRE':'BRE',\
                'CIA':'ROM','TXL':'BER','VCE':'VCE','STN':'LON','GVA':'GVA','GOA':'GOA','KLV':'KLV','STR':'STR','GOT':'GOT','ZRH':'ZRH','BHD':'BFS','LGW':'LON',\
                'BHX':'BHX','NCL':'NCL','NCE':'NCE','ARN':'STO','PEK':'BJS','PVG':'SHA','SHA':'SHA','NAJ':'BJS','CAN':'CAN','SZX':'SZX'}

def GetFlightNo(s):
    '''
        提前航班号
    '''
    flight_str = "flight_"
    start = s.find(flight_str)
    if start != -1:
        return s[start + len(flight_str):]
    return None

def GetTextByXpath(node, path):
    '''
        获得指定path的文本
    '''
    strs = node.xpath(path)
    if len(strs) > 0:
        return "".join(strs).strip() 
    return ""

def GetAllText(node):
    '''
        获得节点下所有的文本
    '''
    strs = []
    for t in node.itertext():
        strs.append(t)
    return "".join(strs).strip()

def GetPunctualityRate(s):
    m = percentPattern.search(s)
    if m != None:
        return m.group(1)
    return None

def GetTax(s):
    strs = numPattern.findall(s)
    if len(strs) == 2:
        return strs[0],strs[1]
    return None, None

def GetAirportNo(s):
    s = s.strip()
    if len(s) >= 3:
        return s[-3:]
    return None

def GetNumber(s):
    '''
        获得字符串中的数字
    '''
    m = numPattern.search(s)
    if m != None:
        return m.group(0)
    return None

def GetAlphanumeric(s):
    '''
        获得字符串中的数字和字母
    '''
    m = alphanumericPattern.search(s)
    if m != None:
        return m.group(0)
    return None

def GetInterPricePage(queryLogTransNo, cookie, referer, proxy = None, use_proxy = True):
    priceURL = "http://flights.ctrip.com/international/GetSubstepSearchResults.aspx?IsJSON=T&queryLogTransNo=%s&QueryType=1&cityPairAirline=first&withDirectAirline=T&RdNo=2103213618&ind=347,359,356,370" % queryLogTransNo
    
    error = 0

    resp = crawl_single_page(priceURL, referer=referer, proxy = proxy, cookie = cookie)
    if resp == None or len(resp) == 0:
        if proxy != None:
            invalid_proxy(proxy=proxy, source='ctripFlight')
            logger.error('ctripFlight: Proxy Error: htmlcontent is null with proxy: %s'%p)
            error = INVALID_PROXY
    else:
        return resp, error

    return None, error

TaxPriceClasses = {"p_f16_9": 0, "p_f16_5": 1, "p_f16_2": 2, "p_f16_4": 3, "p_f16_3": 4,
                "p_f16_0": 5, "p_f16_6": 6, "p_f16_8": 7, "p_f16_7": 8, "p_f16_1": 9}
def GetPriceByClass(s, classes):
    s = urllib.unquote(s)
    strs = classPattern.findall(s) 
    price = 0
    for n in strs:
        price = price * 10 + classes[n]
    return price 

def ParseInterPage(page):
    '''
    '''
    error = 0
    try:
        data = jsonlib.read(page.decode("GBK", "ignore"))
    except Exception,e:
        logger.error('ctripFlight: Parser Error: cannot find flights')
        error = DATA_NONE
        return None, error

    allinfo = []

    for node in data["FlightList"]:
        dept_time = datetime.datetime.strptime(node["DepartTime"], '%Y-%m-%d %H:%M:%S')
        dept_time = str(dept_time).replace(' ','T',)
        dest_time = datetime.datetime.strptime(node["ArrivalTime"], '%Y-%m-%d %H:%M:%S') 
        dest_time = str(dest_time).replace(' ','T',)
        # 航班信息
        flight = Flight()
        flight.flight_no = ''
        flight.plane_no = ''
        flight.airline = ''
        dept_id_list = []

        for flightNode in node["FlightDetail"]:
            flight.flight_no = flight.flight_no + flightNode["FlightNo"] + '_'
            flight.airline = flight.airline + flightNode["AirlineName"] + '_'
            flight.plane_no = flight.plane_no + flightNode["CraftType"] + '_'
            dept_id_list.append(flightNode["DPort"])
            flight.dest_id = flightNode["APort"] 

        flight.stop = len(dept_id_list) - 1
        flight.dept_id = dept_id_list[0]
        flight.flight_no = flight.flight_no[:-1]
        flight.airline = flight.airline[:-1]
        flight.plane_no = flight.plane_no[:-1]

        flight.dept_time = dept_time
        flight.dest_time = dest_time
        flight.dept_day = flight.dept_time.split('T')[0]
        
        flight.price = int(node["Price"])
        flight.surcharge = int(GetPriceByClass(node["OilFeeImage"], TaxPriceClasses))
        flight.tax = int((GetPriceByClass(node["TaxImage"], TaxPriceClasses)))

        flight.dur = int(node["FlightTime"]) * 60 #飞行时长，s
        flight.currency = "CNY"
        flight.source = "ctrip::ctrip"
        flight.seat_type = node["ClassName"]

        allinfo.append((flight.flight_no,flight.plane_no,flight.airline,flight.dept_id,flight.dest_id,\
                flight.dept_day,flight.dept_time,flight.dest_time,flight.dur,flight.price,flight.tax,\
                flight.surcharge,flight.currency,flight.seat_type,flight.source,flight.return_rule,flight.stop))
        
    return allinfo, error

def ParsePage(tree):
    allinfo = []
    nodes = tree.xpath("//div[@class='search_box']")

    for node in nodes:
        # 航班信息
        flight = Flight()
        flight.flight_no = GetFlightNo(node.get("id"))
        strs = node.get("data").split("|")
        flight.dept_id = strs[2]
        flight.dest_id = strs[3]
        flight.airline = GetTextByXpath(node, "table[1]/tr/td[1]/div[1]/span/text()")
        flight.plane_no = GetAlphanumeric(GetAllText(node.xpath("table[1]/tr/td[1]/div[2]/span")[0]))
        
        airport_tax, fuel_surcharge = GetTax(GetTextByXpath(node, "table[1]/tr/td[5]/div[1]/text()"))

        priceNodes = node.xpath("table[@class='search_table']/tr")
        for priceNode in priceNodes:
            # 机票信息
            flight.dept_time = str(datetime.datetime.strptime(strs[0], '%Y-%m-%d %H:%M:%S')).replace(' ','T',)
            flight.dest_time = str(datetime.datetime.strptime(strs[1], '%Y-%m-%d %H:%M:%S')).replace(' ','T',)
            flight.dept_day = flight.dept_time.strftime('%Y-%m-%d')

            flight.price = int(GetTextByXpath(priceNode, "td[7]/span/text()"))
            flight.tax = int(airport_tax)
            flight.surcharge = int(fuel_surcharge)
            flight.currency = "CNY"
            flight.source = "ctrip::ctrip"
            flight.seat_type = GetAllText(priceNode.xpath("td[2]")[0])

            allinfo.append((flight.flight_no,flight.plane_no,flight.airline,flight.dept_id,flight.dest_id,\
                        flight.dept_day,flight.dept_time,flight.dest_time,flight.dur,flight.price,flight.tax,\
                        flight.surcharge,flight.currency,flight.seat_type,flight.source,flight.return_rule,flight.stop))

        
    return allinfo

def ValidateInterPage(page, params):
    try:
        data = jsonlib.read(page.decode("GBK", "ignore"))
    except Exception,e:
        return -1

    if len(params) != 2:
        #logger.info('params error')
        return -1

    for node in data["FlightList"]:
        dept_time = datetime.datetime.strptime(node["DepartTime"], '%Y-%m-%d %H:%M:%S')
        dept_time = str(dept_time).replace(' ','T',)
        dest_time = datetime.datetime.strptime(node["ArrivalTime"], '%Y-%m-%d %H:%M:%S') 
        dest_time = str(dest_time).replace(' ','T',)

        # 航班信息
        flight = Flight()
        flight.flight_no = ''
        flight.plane_no = ''
        flight.airline = ''
        dept_id_list = []

        for flightNode in node["FlightDetail"]:
            flight.flight_no = flight.flight_no + flightNode["FlightNo"] + '_'
            flight.airline = flight.airline + flightNode["AirlineName"] + '_'
            flight.plane_no = flight.plane_no + flightNode["CraftType"] + '_'
            dept_id_list.append(flightNode["DPort"])
            flight.dest_id = flightNode["APort"] 

        flight.dept_id = dept_id_list[0]
        flight.flight_no = flight.flight_no[:-1]
        flight.dept_time = dept_time
        flight.dest_time = dest_time
        flight.dept_day = flight.dept_time.split('T')[0]
        flight.price = int(node["Price"])
        if flight.flight_no == params[0] and flight.dept_time == params[1]:
            return flight.price

    return -1

def ctripFlight_task_parser(content):
    
    result = {}
    result['para'] = None
    result['error'] = 0

    #解析content
    try:
        contents = content.strip().split('&')
        dept_id = contents[0]
        dest_id = contents[1]
        dept_date = contents[2][:4] + '-' + contents[2][4:6] + '-' + contents[2][6:]
    except Exception,e:
        logger.info('ctripFlight: taskcontent error: %s'%str(e))
        result['error'] = TASK_ERROR
        return result
    
    trip_way = 'Oneway'

    searchURL = "http://flights.ctrip.com/booking/%s-%s-day-1.html?DCity1=%s&ACity1=%s&DDate1=%s&passengerQuantity=1&SendTicketCity=undefined&PassengerType=ADU&SearchType=S&RouteIndex=1&RelDDate=&RelRDate="
    interSearchURL = "http://flights.ctrip.com/international/ShowFareFirst.aspx?flighttype=S&relddate=%s&dcity=%s&acity=%s"

    is_inter = False
    searcURL = ""
    if dept_id.lower() in CN_AIRPORTS and dest_id.lower() in CN_AIRPORTS:
        searchURL = searchURL %(dept_id, dest_id, dept_id, dest_id, dept_date)
    else:
        searchURL = interSearchURL %(dept_date, dept_id, dest_id)
        is_inter = True
    refererURL = "http://flights.ctrip.com/booking/"
    cookie = {}

    p = get_proxy(source='ctripFlight')

    if p == None:
        result['error'] = PROXY_NONE
        return result

    resp = crawl_single_page(searchURL, proxy = p, cookie = cookie)
    if resp == None or len(resp) == 0:
        invalid_proxy(proxy = p, source='ctripFlight')
        logger.error('ctripFlight: Proxy Error: htmlcontent is null with proxy: %s'%p)
        result['error'] = PROXY_INVALID
        return result

    # 2. 解析页面
    tree = etree.HTML(resp)
    if is_inter or GetTextByXpath(tree, "//title/text()").endswith("携程国际机票"):
        # 国际机票
        queryLogTransNo = tree.xpath("//input[@id='queryLogTransNo']")[0].get("value")
        # 抓取机票价格页面 
        resp, result['error']= GetInterPricePage(queryLogTransNo, cookie, searchURL, p)
        if resp != None:
            result['para'], result['error'] = ParseInterPage(resp)

    else:   # 国内机票
        pass
        #return ParsePage(tree)

    return result

def ctripFlight_request_parser(content):

    result = -1

    try:
        infos = content.split('|')
        flight_info = infos[0].strip()
        time_info = infos[1].strip()
        ticketsource = infos[2].strip()

        flight_no = flight_info.split('-')[0]
        dept_id,dest_id = AIRPORT_CITY_DICT[flight_info.split('-')[1]],AIRPORT_CITY_DICT[flight_info.split('-')[2]]

        #date：20140510，time：09:10
        dept_day,dept_hour = time_info.split('_')[0],time_info.split('_')[1]

        dept_date = dept_day[0:4] + '-' + dept_day[4:6] + '-' + dept_day[6:]#2014-05-10

        orig_dept_time = dept_date + 'T' + dept_hour + ':00'
    except Exception,e:
        logger.info('ctripFlight: Wrong Content Format with %s'%content)
        return result
    
    params = [flight_no,orig_dept_time]

    trip_way = 'Oneway'
    searchURL = "http://flights.ctrip.com/booking/%s-%s-day-1.html?DCity1=%s&ACity1=%s&DDate1=%s&passengerQuantity=1&SendTicketCity=undefined&PassengerType=ADU&SearchType=S&RouteIndex=1&RelDDate=&RelRDate="
    interSearchURL = "http://flights.ctrip.com/international/ShowFareFirst.aspx?flighttype=S&relddate=%s&dcity=%s&acity=%s"

    is_inter = False
    searcURL = ""
    if dept_id.lower() in CN_AIRPORTS and dest_id.lower() in CN_AIRPORTS:
        searchURL = searchURL %(dept_id, dest_id, dept_id, dest_id, dept_date)
    else:
        searchURL = interSearchURL %(dept_date, dept_id, dest_id)
        is_inter = True
    refererURL = "http://flights.ctrip.com/booking/"
    cookie = {}

    resp = crawl_single_page(searchURL, proxy = None, cookie = cookie)

    if resp == None or len(resp) == 0:
        return result

    # 2. 解析页面
    try:
        tree = etree.HTML(resp)
    except Exception,e:
        return result

    if is_inter or GetTextByXpath(tree, "//title/text()").endswith("携程国际机票"):
        # 国际机票
        if len(tree.xpath("//input[@id='queryLogTransNo']")) > 0:
            queryLogTransNo = tree.xpath("//input[@id='queryLogTransNo']")[0].get("value")
            # 抓取机票价格页面 
            resp, error = GetInterPricePage(queryLogTransNo, cookie, searchURL, proxy = None)
            if resp == None:
                return result
            else:
                result = ValidateInterPage(resp, params)
                return result
    else:
        # 国内机票
        return result



if __name__ == "__main__":
    import sys
    if len(sys.argv) < 1:
        print "Usage: %s " %sys.argv[0]
        sys.exit()
    
    taskcontent = "BJS&PAR&20140602"
    result1 = ctripFlight_task_parser(taskcontent)
    print str(result1)

    requestcontent = "AF381-PEK-CDG|20140602_01:00|ctrip::ctrip"
    result2 = ctripFlight_request_parser(requestcontent)
    print str(result2)

