#! /usr/bin/env python
#coding=UTF8

"""
    @author:fangwang
    @date:2014-04-13
    @desc: crawl and parse 17u web content
"""

import json
import time
import re
import sys
import urllib
from common.logger import logger
from util.crawl_func import crawl_single_page
#from slave_common import get_proxy
from common.class_common import Flight
from common.common import get_proxy, invalid_proxy

reload(sys)
sys.setdefaultencoding('utf-8')

city_dict = {'CPH': 'CPH', 'LIN': 'MIL', 'AGB': 'AGB', 'BGO': 'BGO', 'HEL': 'HEL', 'NAP': 'NAP', 'LIS': 'LIS', 'NAY': 'BJS', 'BOD': 'BOD', \
        'FNI': 'FNI', 'AGP': 'AGP', 'PEK': 'BJS', 'SXB': 'SXB', 'SXF': 'BER', 'LYS': 'LYS', 'LBA': 'LBA', 'HAJ': 'HAJ', 'HAM': 'HAM', 'MRS': 'MRS', \
        'BFS': 'BFS', 'LPL': 'LPL', 'LHR': 'LON', 'SVQ': 'SVQ', 'VIE': 'VIE', 'BVA': 'PAR', 'MAD': 'MAD', 'LEJ': 'LEJ', 'MAN': 'MAN', 'TSF': 'VCE', \
        'FLR': 'FLR', 'BER': 'BER', 'RTM': 'RTM', 'VLC': 'VLC', 'SZG': 'SZG', 'OSL': 'OSL', 'AMS': 'AMS', 'BUD': 'BUD', 'STO': 'STO', 'TRN': 'TRN', \
        'BLQ': 'BLQ', 'PRG': 'PRG', 'GRX': 'GRX', 'SHA': 'SHA', 'OXF': 'OXF', 'PSA': 'PSA', 'MXP': 'MIL', 'LCY': 'LON', 'INN': 'INN', 'ANR': 'ANR', \
        'OPO': 'OPO', 'BCN': 'BCN', 'LUX': 'LUX', 'GLA': 'GLA', 'MUC': 'MUC', 'LUG': 'LUG', 'CGN': 'CGN', 'BSL': 'BSL', 'PMF': 'MIL', 'PVG': 'SHA', \
        'SEN': 'LON', 'NUE': 'NUE', 'VRN': 'VRN', 'FCO': 'ROM', 'FRA': 'FRA', 'WAW': 'WAW', 'DUS': 'DUS', 'LTN': 'LON', 'CDG': 'PAR', 'MMX': 'MMA', \
        'ORY': 'PAR', 'BRU': 'BRU', 'EDI': 'EDI', 'BRS': 'BRS', 'BRN': 'BRN', 'BRE': 'BRE', 'CIA': 'ROM', 'TXL': 'BER', 'VCE': 'VCE', 'STN': 'LON', \
        'GVA': 'GVA', 'GOA': 'GOA', 'KLV':'KLV', 'STR': 'STR', 'GOT': 'GOT', 'ZRH': 'ZRH', 'BHD': 'BFS', 'NCE': 'NCE', 'BHX': 'BHX', 'NCL': 'NCL', 'LGW': 'LON', 'ARN': 'STO'}

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

def tongcheng_request_parser(taskcontent):
    result = -1 

    taskcontent.encode('utf-8')

    try:
        info_list = taskcontent.split('|')
        flight_info = info_list[0]
        time_info = info_list[1]
        source = info_list[2]

        flight_no = flight_info.split('-')[0]
        dept_id = flight_info.split('-')[1]
        dest_id = flight_info.split('-')[2]

        dept_day = time_info.split('_')[0] #20140510
        dept_minute = time_info.split('_')[1] +':00' #18:30:00
        dept_city = city_dict[dept_id]
        dest_city = city_dict[dest_id]
        dept_city_cn = city_dict_cn[dept_id].encode('utf-8')
        dest_city_cn = city_dict_cn[dest_id].encode('utf-8')
    except Exception, e:
        logger.error('tongchengFlight: wrong content format with %s'%taskcontent + str(e))
        return -1 

    dept_date = dept_day[:4] + '-' + dept_day[4:6] + '-' +dept_day[6:] #2014-05-10
    dept_time = dept_date + 'T' + dept_minute
    
    #p = get_proxy()  
    url = get_url(dept_city_cn, dest_city_cn, dept_date, dept_city, dest_city)

    if url != '':
        page = crawl_single_page(url, proxy = None, Accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    else:
        return -1
    
    if page != '' and len(page) > 100:
        result = ParsePage(page,flight_no,dept_time)
    else:
        #invalid_proxy(p)
        return -1

    return result


def get_url(dept_city, dest_city, dept_date, dept_id, dest_id, proxy = None):
    parser_url = ''
    url_temp = 'http://www.ly.com/iflight/flightinterajax.aspx?action=SEARCHURL&airplaneInternatType=1&iOrgPort=' + dept_city + '&iArvPort=' + dest_city + '&idtGoDate=' + dept_date + '&idtBackDate=时间/日期&sel_inCabinType=Y&sel_inPassengersType=1&sel_inAdult=1&sel_inChild=0&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&iOrgPortMult=城市名&iArvPortMult=城市名&idtGoDateMult=时间/日期&callback=tc10805565235'

    page1 = crawl_single_page(url_temp, proxy=proxy, n=1,  Accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    
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
        logger.error('Can not get url temp 1!')
        return parser_url
    url_temp2 = 'http://www.ly.com' + url_temp1
    
    page2 = crawl_single_page(url_temp2,proxy = proxy, n=1, Accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    try:
        search_code = search_code_pat.findall(page2)[0]
    except Exception,e:
        logger.error('Can not get search code!' + str(e))
    
    parser_url = 'http://www.ly.com/iflight/AjaxHandler.ashx?action=GRADATIONQUERYFLIGHT&TravelType=0&Departure=' + dept_city + '&DepartureC=' + dept_id + '&Arrival=' + dest_city + '&ArrivalC=' + dest_id + '&DepartureDate=' + dept_date + '&ReturnDate=1900-01-01&AdultNum=1&ChildNum=0&CabinType=1&FlatType=1&PassengerType=1&pageCode=' + search_code + '&SearchGuid=&PreGuid=&userId=&isFirst=true'
    
    return parser_url


def ParsePage(content,flight_no,dept_time):
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
                    
                    flight.dept_time = time.strftime('%Y-%m-%d %H:%M:%S', \
                            time.localtime(float(str(dept_time_temp)[:-3]))).replace(' ','T')
                    flight.dest_time = time.strftime('%Y-%m-%d %H:%M:%S', \
                            time.localtime(float(str(dest_time_temp)[:-3]))).replace(' ','T')
                    flight.dept_day = flight.dept_time.split('T')[0]
                    flight.price = each_flight_json['FareInfo'][0]['TCPrice_Audlt']

                    if flight.flight_no == flight_no and flight.dept_time == dept_time:
                        result = flight.price
                        return result
                        
                except:
                    continue
        else:
            return -1
    return result

if __name__ == '__main__':

    taskcontent = 'SK525_LO286-ARN-WAW|20140530_07:55|tongcheng::tongcheng'

    result = tongcheng_request_parser(taskcontent)

    print str(result)
