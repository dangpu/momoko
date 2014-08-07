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

reload(sys)
sys.setdefaultencoding('utf-8')

percentPattern = re.compile("(\d+)%")
numPattern = re.compile("\d+")
alphanumericPattern = re.compile("\w+")
classPattern = re.compile("p_f16_\d")

AIRPORT_CITY_DICT = {'CPH':'CPH','LIN':'MIL','AGB':'AGB','BGO':'BGO','HEL':'HEL','NAP':'NAP','LIS':'LIS','BOD':'BOD','FNI':'FNI','AGP':'AGP','SXB':'SXB',\
        'SXF':'BER','LYS':'LYS','LBA':'LBA','HAJ':'HAJ','HAM':'HAM','MRS':'MRS','BFS':'BFS','LPL':'LPL','LHR':'LON','SVQ':'SVQ','VIE':'VIE','BVA':'PAR',\
        'MAD':'MAD','BRU':'BRU','MAN':'MAN','TSF':'VCE','FLR':'FLR','BER':'BER','RTM':'RTM','VLC':'VLC','SZG':'SZG','OSL':'OSL','AMS':'AMS','BUD':'BUD',\
        'STO':'STO','TRN':'TRN','BLQ':'BLQ','PRG':'PRG','GRX':'GRX','OXF':'OXF','PSA':'PSA','MXP':'MIL','LCY':'LON','INN':'INN','ANR':'ANR','OPO':'OPO',\
        'BCN':'BCN','LUX':'LUX','GLA':'GLA','MUC':'MUC','LUG':'LUG','CGN':'CGN','BSL':'BSL','PMF':'MIL','SEN':'LON','NUE':'NUE','VRN':'VRN','FCO':'ROM',\
        'FRA':'FRA','WAW':'WAW','DUS':'DUS','LTN':'LON','CDG':'PAR','MMX':'MMA','ORY':'PAR','LEJ':'LEJ','EDI':'EDI','BRS':'BRS','BRN':'BRN','BRE':'BRE',\
        'CIA':'ROM','TXL':'BER','VCE':'VCE','STN':'LON','GVA':'GVA','GOA':'GOA','KLV':'KLV','STR':'STR','GOT':'GOT','ZRH':'ZRH','BHD':'BFS','LGW':'LON',\
        'BHX':'BHX','NCL':'NCL','NCE':'NCE','ARN':'STO','PEK':'BJS','PVG':'SHA','SHA':'SHA','NAJ':'BJS'}

def ReadToList(inputfile):
    data = []
    ifile = open(inputfile)
    for line in ifile:
        data.append(line.strip())
    ifile.close()
    return data

CN_AIRPORTS = set(ReadToList("../ctripFlight/cn_airport"))

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

def GetInterPricePage(queryLogTransNo, cookie, referer, proxy):#use_proxy = True):
    priceURL = "http://flights.ctrip.com/international/GetSubstepSearchResults.aspx?IsJSON=T&queryLogTransNo=%s&QueryType=1&cityPairAirline=first&withDirectAirline=T&RdNo=2103213618&ind=347,359,356,370" % queryLogTransNo
    
    #p = proxy
    p = None

    #if use_proxy:
        # 如果抓起失败，换一个代理IP，然后重试
    #for i in range(3):
        #p = get_proxy()
    resp = crawl_single_page(priceURL,n=1, referer=referer, proxy = p, cookie = cookie)
    if resp == None or len(resp) == 0:
        #invalid_proxy(p)
        pass
    else:
        return resp
        #logger.info('get price page successful')
    #else:
        #resp = crawl_single_page(searchURL, cookie = cookie)

    return 

TaxPriceClasses = {"p_f16_9": 0, "p_f16_5": 1, "p_f16_2": 2, "p_f16_4": 3, "p_f16_3": 4,
                "p_f16_0": 5, "p_f16_6": 6, "p_f16_8": 7, "p_f16_7": 8, "p_f16_1": 9}
def GetPriceByClass(s, classes):
    s = urllib.unquote(s)
    strs = classPattern.findall(s) 
    price = 0
    for n in strs:
        price = price * 10 + classes[n]
    return price 

def ParseInterPage(page,params):
    '''
    '''
    try:
        data = jsonlib.read(page.decode("GBK", "ignore"))
    except Exception,e:
        return -1

    if len(params) != 2:
        logger.info('params error')
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

        #flight.stop = len(dept_id_list)
        flight.dept_id = dept_id_list[0]
        flight.flight_no = flight.flight_no[:-1]
        #flight.airline = flight.airline[:-1]
        #flight.plane_no = flight.plane_no[:-1]

        flight.dept_time = dept_time
        flight.dest_time = dest_time
        flight.dept_day = flight.dept_time.split('T')[0]
        
        flight.price = int(node["Price"])
        #flight.surcharge = int(GetPriceByClass(node["OilFeeImage"], TaxPriceClasses))
        #flight.tax = int((GetPriceByClass(node["TaxImage"], TaxPriceClasses)))

        #flight.dur = int(node["FlightTime"]) * 60 #飞行时长，s
        #flight.currency = "CNY"
        #flight.source = "ctrip::ctrip"
        #flight.seat_type = node["ClassName"]

        if flight.flight_no == params[0] and flight.dept_time == params[1]:
            return flight.price

    return -1

def ParsePage(tree,params):
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

def ctripFlight_request_parser(content):

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
        logger.info('wrong content format with %s'%content)
        logger.info(str(e))
        return -1
    
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

    p = get_proxy()
    resp = crawl_single_page(searchURL, proxy = p, cookie = cookie)
    if resp == None or len(resp) == 0:
        invalid_proxy(p)
        return -1
    # 2. 解析页面
    try:
        tree = etree.HTML(resp)
    except Exception,e:
        logger.info('etree error: %s'%str(e))
        return -1

    if is_inter or GetTextByXpath(tree, "//title/text()").endswith("携程国际机票"):
        # 国际机票
        if len(tree.xpath("//input[@id='queryLogTransNo']")) > 0:
            queryLogTransNo = tree.xpath("//input[@id='queryLogTransNo']")[0].get("value")
            logger.info(queryLogTransNo)
        # 抓取机票价格页面 
            resp = GetInterPricePage(queryLogTransNo, cookie, searchURL,p )#use_proxy)
            return ParseInterPage(resp,params)#带参数做验证

    else:   # 国内机票
        return -1
        #return ParsePage(tree,params)#带参数做验证

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 1:
        print "Usage: %s " %sys.argv[0]
        sys.exit()
    
    content = "AF129&BJS&PAR&2014-05-10T09:05:00&ctrip::ctrip"
    content2 = "FN218&BJS&SHA&2014-05-10T20:50:00&ctrip::ctrip"
    result = ctripFlight_request_parser(content)
    #result2 = ctripFlight_request_parser(content2)
    print str(result)
    #print str(result2)

