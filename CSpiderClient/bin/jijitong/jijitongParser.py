#! /usr/bin/env python
#coding=UTF8
"""
    @author:fangwang
    @date:2014-04-13
    @desc:jijitong parser
"""

import sys
import json
from common.logger import logger
from common.class_common import Flight, EachFlight
from util.crawl_func import request_post_data, crawl_single_page
from common.common import get_proxy, invalid_proxy
import time
import datetime
import cookielib
import urllib2
import urllib
import random

reload(sys)
sys.setdefaultencoding('utf-8')

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
        "NCE": "尼斯", "BHX": "伯明翰", "NCL": "纽卡斯尔", "LGW": "伦敦", "ARN": "斯德哥尔摩","CAN":"广州","SZX":"深圳"}
city_dict_pinyin = {"CPH": "gebenhagen", "LIN": "milan", "AGB": "aogesibao", "BGO": "beiergen", "HEL": "heerxinji", "NAP": "nabulesi", \
        "LIS": "lisiben", "NAY": "beijing", "BOD": "boerduo", "FNI": "nimu", "AGP": "malajia", "PEK": "beijing", "SXB": "sitelasibao", \
        "SXF": "bolin", "LYS": "liang", "LBA": "lizi", "HAJ": "hannuowei", "HAM": "hanbao", "MRS": "masai", "BFS": "beierfasite", "LPL": "liwupu", \
        "LHR": "lundun", "SVQ": "saiweiliya", "VIE": "weiyena", "BVA": "bali", "MAD": "madeli", "LEJ": "laibixi", "MAN": "manchesite", "TSF": "weinisi", \
        "FLR": "fuluolunsa", "BER": "bolin", "RTM": "lutedan", "VLC": "walunxiya", "SZG": "saercibao", "OSL": "aosilu", "AMS": "amusitedan", \
        "BUD": "budapeisi", "STO": "sidegeermo", "TRN": "duling", "BLQ": "boluoniya", "PRG": "bulage", "GRX": "gelanada", "SHA": "shanghai", \
        "OXF": "niujin", "PSA": "bisa", "MXP": "milan", "LCY": "lundun", "INN": "yinsibuluke", "ANR": "anteweipu", "OPO": "boertu", "BCN": "basailuona", \
        "LUX": "lusenbao", "GLA": "gelasige", "MUC": "munihei", "LUG": "lujianuo", "CGN": "kelong", "BSL": "basaier", "PMF": "milan", "PVG": "shanghai", \
        "SEN": "lundun", "NUE": "niulunbao", "VRN": "weiluona", "FCO": "luoma", "FRA": "falankefu", "WAW": "huasha", "DUS": "dusaierduofu", "LTN": "lundun", \
        "CDG": "bali", "MMX": "maermo", "ORY": "bali", "BRU": "bulusaier", "EDI": "aidingbao", "BRS": "bulisituoer", "BRN": "boerni", "BRE": "bulaimei", \
        "CIA": "luoma", "TXL": "bolin", "VCE": "weinisi", "STN": "lundun", "GVA": "rineiwa", "GOA": "renaya", "KLV": "kaluoweifali", "STR": "situjiate", \
        "GOT": "gedebao", "ZRH": "sulishi", "BHD": "beierfasite", "NCE": "nisi", "BHX": "bominghan", "NCL": "niukasier", "LGW": "lundun", "ARN": "sidegeermo",\
        "CAN":"guangzhou","SZX":"shenzhen"}

accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
FIRST_URL = 'http://www.jijitong.com/%s-%s.html?%s'
SECOND_URL = 'http://www.jijitong.com/handle/SeachHandler.ashx?t%s'
PRICE_URL = 'http://www.jijitong.com/Handle/PolicyHandler.ashx?t%s'

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25

def jijitong_task_parser(taskcontent):
    result = {}
    result['para'] = {'ticket':[], 'flight':{}}
    result['error'] = 0

    taskcontent.encode('utf-8')
    try:
        dept_city_zh,dept_city_en,dest_city_zh,dest_city_en,dept_day_temp = \
                taskcontent.strip().split('&')[0],  \
                taskcontent.strip().split('&')[1],  \
                taskcontent.strip().split('&')[2],  \
                taskcontent.strip().split('&')[3],  \
                taskcontent.strip().split('&')[4]
        dept_day = dept_day_temp[:4] + '-' + dept_day_temp[4:6] + '-' + dept_day_temp[6:]
    except Exception,e:
        logger.error('jijitongFlight:Wrong Content Format with %s'%taskcontent)
        result['error'] = TASK_ERROR
        return result
    
    p = get_proxy(source='jijitongFlight')
    if p == None:
        result['error'] = PROXY_NONE
        return result

    first_url = FIRST_URL % (dept_city_en,dest_city_en,dept_day_temp)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    resp = crawl_single_page(first_url,proxy=p, \
         Accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', n = 1)

    if resp.find('404错误') < 0:
        url = get_url(dept_city_zh,dest_city_zh,dept_day)
        page = crawl_single_page(url, proxy = p, referer = first_url)

        if page != '' and len(page) > 300:
            post_data = get_post_data(page, dept_day)
            price_url = PRICE_URL%str(time.time()*1000)

            price_page = request_post_data(price_url, data=post_data, referer=first_url, \
                                           n=1, proxy=p)
            price_dict = parsePrice(price_page)
            #print price_dict
            time.sleep(5)
            flights = parse_page(page, price_dict)
            result['para'] = flights
        else:
            result['error'] = PROXY_INVALID
            return result
    else:
        result['error'] = DATA_NONE
        return result

    return result


def get_url(dept_city_zh,dest_city_zh,dept_day,dest_day=''):
    dept_city_zh = dept_city_zh.encode('utf-8')
    dest_city_zh = dest_city_zh.encode('utf-8')
    dept_city = urllib2.quote(dept_city_zh)
    dest_city = urllib2.quote(dest_city_zh)
 
    url = 'http://www.jijitong.com/handle/FlightHandler.ashx?t' + str(random.random()) + \
            '&fromCity=' + dept_city + '&toCity=' + dest_city + '&fromDate=' + dept_day + \
            '&toDate=' + dest_day + '&adtCount=1&chdCount=0&class=Y&stops=2&currency=CNY' + \
            '&vendors=&vcode=&_=' + str(int(time.time() * 1000))

    return url 


def jijitong_request_parser(content):

    result = -1

    return result
    
    
def parse_page(content, price_dict):

    flights = {}
    tickets = []
    result = {'ticket':tickets, 'flight':flights}

    try:
        json_temp = json.loads(content)
    except:
        return result

    if json_temp['Status'] == 'SUCCESS':
        for each_flight_json in json_temp['datalist']:
            flight = Flight()
            try:
                flight.flight_no = each_flight_json['Key']
                flight.stop = int(each_flight_json['OW'])
                flight.price = price_dict[flight.flight_no]
                #error price
                flight.tax = each_flight_json['AIP'][0]['TX']
                flight.dept_id = each_flight_json['ODO'][0]['OL']
                flight.dest_id = each_flight_json['ODO'][-1]['DL']
                flight.dept_time = each_flight_json['ODO'][0]['DD'] + ':00'
                flight.dest_time = each_flight_json['ODO'][-1]['AD'] + ':00'
                flight.currency = 'CNY'
                
                flight.source = 'jijitong::jijitong'
                flight.seat_type = '经济舱'
                flight.dept_day = flight.dept_time.split('T')[0]

                flight_num = len(flight.flight_no.split('_'))

                if flight_num == 1:
                    dur_A_temp = each_flight_json['ODO'][0]['ET']
                    flight.dur = int(dur_A_temp) * 60
                else:
                    dur_A_temp = 0
                    dur_A_temp2 = 0
                    for dept_content in each_flight_json['ODO'][:flight_num]:
                        dur_A_temp += int(dept_content['ET']) * 60

                    for x in range(1,flight_num):
                        #print x
                        dept_time_str = each_flight_json['ODO'][x-1]['AD']
                        #print dept_time_str
                        dest_time_str = each_flight_json['ODO'][x]['DD']
                        #print dest_time_str
                        dur_A_temp2 += durCal(dept_time_str, dest_time_str)
                        #print dur_A_temp2
                    flight.dur = dur_A_temp + dur_A_temp2

                plane_no = ''
                airline = ''
                for each_json_temp in each_flight_json['ODO']:

                    plane_no = plane_no + each_json_temp['EQ'] + '_'
                    airline = airline + each_json_temp['COA'] + '_'

                    try:
                        eachflight = EachFlight()
                        eachflight.flight_no = each_json_temp['MA']
                        eachflight.dept_id = each_json_temp['OL']
                        eachflight.dest_id = each_json_temp['DL']
                        eachflight.airline = each_json_temp['COA']
                        eachflight.plane_no = each_json_temp['EQ']
                        eachflight.dept_time = each_json_temp['DD'] + ':00'
                        eachflight.dest_time = each_json_temp['AD'] + ':00'
                        eachflight.dur = int(each_json_temp['ET']) * 60

                        eachflight.flight_key = eachflight.flight_no + '_' + eachflight.dept_id + '_' + eachflight.dest_id

                        eachflight_tuple = (eachflight.flight_no, eachflight.airline, eachflight.plane_no, eachflight.dept_id, \
                                eachflight.dest_id, eachflight.dept_time, eachflight.dest_time, eachflight.dur)
                        flights[eachflight.flight_key] = eachflight_tuple
                        #print eachflight_tuple
                    except Exception, e:
                        print str(e)
                        continue

                flight.plane_no = plane_no[:-1]
                flight.airline = airline[:-1]
                flight_tuple = (flight.flight_no, flight.plane_no, flight.airline, flight.dept_id, \
                        flight.dest_id, flight.dept_day, flight.dept_time, flight.dest_time, \
                        flight.dur, flight.price, flight.tax, flight.surcharge, flight.currency, \
                        flight.seat_type, flight.source, flight.return_rule, flight.stop) 

                tickets.append(flight_tuple)
            except Exception,e:
                logger.error('Can not parse flight info!' + str(e))
                continue
    else:
        return result

    result['flight'] = flights
    result['ticket'] = tickets

    return result


def validate_page(content, flight_no, orig_dept_time):
    result = -1

    json_temp = json.loads(content)
    if json_temp['Status'] == 'SUCCESS':
        for each_flight_json in json_temp['datalist']:
            flight = Flight()
            try:
                flight.flight_no = each_flight_json['Key']
                flight.price = each_flight_json['AIP'][0]['EA']
                flight.dept_time = each_flight_json['ODO'][0]['DD']

                dept_time = int(time.mktime(datetime.datetime.strptime(flight.dept_time,'%Y-%m-%dT%H:%M').timetuple()))
                flight.dept_time = flight.dept_time + ':00'

                if flight.flight_no == flight_no and flight.dept_time == orig_dept_time:
                    result = flight.price
                    return result
            except Exception,e:
                continue

    else:
        return result

    return result


def get_post_data(content, dept_day):
    post_data = {}
    try:
        flight_json = json.loads(content)
    except Exception, e:
        logger.error(('Loading flight json failed error: ' + str(e)))
        return post_data

    value = '<base>'
    value += '<arr>' + flight_json['TC'] + '</arr>'
    passengernum = 0
    AdultCount = 1
    ChildCount = 0
    passengernum = AdultCount + ChildCount
    value += '<PassengerNum>' + str(passengernum) + '</PassengerNum>'
    value += '<chdPassengerNum>' + str(ChildCount) + '</chdPassengerNum>'
    value += '<dep>' + flight_json['FC'] + '</dep>'
    value += '<sdate>' + dept_day + '</sdate>'
    value += '<bdate></bdate>'
    value += '<listitem>'

    BaseAirCode = ''
    #print flight_json
    for each_flight_json in flight_json['datalist']:
        govalue = ''
        backvalue = ''
        goishaveCon = 0
        backishaveCon = 0
        goishavegat = 0
        backishavegat = 0
        goishaveCountry = 0
        backishaveCountry = 0
        gokey = ''
        backkey = ''
        price = ''
        tax = ''
        BackPrice = ''
        NucPrice = ''

        chdprice = '0'
        chdtax = '0'
        chdBackPrice = '0'
        chdNucPrice = '0'

        BaseAirCode = each_flight_json['VC']
        for price_json in each_flight_json['AIP']:
            if price_json['PQ'] == 'ADT':
                tax = price_json['TX']
                price = price_json['EA']
                BackPrice = price_json['BP']
                NucPrice = price_json['TN']
            else:
                chdtax = price_json['TX']
                chdprice = price_json['TA']
                chdBackPrice = price_json['BP']
                chdNucPrice = price_json['TN']

        tempvalue = 'HKH,MFM,TPE,TSA,KHH,HSZ,CYI,GNI,HCN,HSZ,HUN'
        goindex = 0
        goquanzhong = 0
        backcount = 0

        for each_part_json in each_flight_json['ODO']:
            f = each_flight_json['ODO'].index(each_part_json)
            #print f
            #print '^_^'
            if each_part_json['M'] == 0 or each_part_json['M'] == '0':
                gokey += each_part_json['MA'] + '_'
                govalue += each_part_json['OL'] + '_' + each_part_json['DL'] + '_' + \
                    each_part_json['OA'] + '_' + each_part_json['MA']  + '_' + each_part_json['RC'] + '^'
                tempquanzhong = getItineraryFlags(each_part_json['OL'], each_part_json['OLCRY'], \
                                                  each_part_json['OLCT'], each_part_json['DL'], \
                                                  each_part_json['DLCRY'], each_part_json['DLCT'], f)
                #print tempquanzhong
                #print '***********'
                if goquanzhong < tempquanzhong:
                    goquanzhong = tempquanzhong
                    goindex = f

                #go_key = each_part_json['OL'] + '_' + each_part_json['OLCRY'] + '_' + each_part_json['OLCT']

            elif each_part_json['M'] == 1 or each_part_json['M'] == '1':
                backcount += 1

        backindex = 0
        backjishu = 0
        backquanzhong = 0

        if backcount > 0:
            for each_part_json in each_flight_json['ODO']:
                if each_part_json['M'] == '1' or each_part_json['M'] == 0:
                    backkey += each_part_json['MA'] + '_'
                    backvalue += each_part_json['DL'] + '_' + each_part_json['OL'] + '_' + \
                        each_part_json['OA'] + '_' + each_part_json['MA'] + '_' + \
                        each_part_json['RC'] + '^'
                    tempquanzhong = getItineraryFlags(each_part_json['OL'], each_part_json['OLCRY'], \
                                                      each_part_json['OLCT'], each_part_json['DL'], \
                                                      each_part_json['DLCRY'], each_part_json['DLCT'], \
                                                      backcount-backjishu)
                    if backquanzhong < tempquanzhong:
                        backquanzhong = tempquanzhong
                        backindex = backjishu
                    #print str(tempquanzhong) + 'temp'
                    backjishu += 1


        goAirCode = ''
        gofirstCode = ''
        golastCode = ''
        goPrimary = ''
        backfirstCode = ''
        backlastCode = ''
        backPrimary = ''
        BackAirCode = ''
        govalue = govalue[0:govalue.rfind('^')]

        #print govalue

        govaluelist = govalue.split('^')
        #print govaluelist

        for i in range(0, len(govaluelist)):
            if i == goindex:
                gotempvalue = govaluelist[i].split('_')
                #print gotempvalue
                goPrimary = gotempvalue[0] + '_' + gotempvalue[1] + '_' + gotempvalue[4] + \
                    '_' + gotempvalue[3][0:2] + '_' + gotempvalue[3]
                goAirCode = gotempvalue[3][0:2]

                if i > 0:
                    gotempvalue1 = govaluelist[i - 1].split('_')
                    gofirstCode = gotempvalue1[0] + '_' + gotempvalue1[3][0:2]

                if (i + 1 < len(govaluelist)):
                    gotempvalue2 = govaluelist[i+1].split('_')
                    golastCode = gotempvalue2[1] + '_' + gotempvalue2[3][0:2]
                break

        if backcount > 0:
            backvalue = backvalue[0: backvalue.rfind('^')]
            backvaluelist = backvalue.split('^')
            #print backvaluelist
            for i in range(len(backvaluelist)-1, 0, -1):
                #print i
                #print backindex
                backindex = 1
                if i == backindex:
                    backtempvalue = backvaluelist[i].split('_')
                    backPrimary = backtempvalue[0] + '_' + backtempvalue[1] + '_' + \
                        backtempvalue[4] + '_' + backtempvalue[3][0:2] + '_' + \
                        backtempvalue[3]
                    BackAirCode = backtempvalue[3][0:2]

                    if i > 0:
                        backtempvalue1 = backvaluelist[i-1].split('_')
                        backlastCode = backtempvalue1[1] + '_' + \
                            backtempvalue1[3][0:2]
                    if (i+1 < len(backvaluelist)):
                        backtempvalue2 = backvaluelist[i+1].split('_')
                        backfirstCode = backtempvalue2[0] + '_' + backtempvalue2[3][0:2]
                    break
        #start
        value += '<item><key>'
        key = gokey[0:gokey.rfind('_')] + '^' + backkey[0:backkey.rfind('_')]
        value += key + '</key>'
        value += '<goAirCode>' + BaseAirCode + '</goAirCode>'
        value += '<price>' + price + '</price>'
        value += '<tax>' + tax + '</tax>'
        value += '<BackPrice>' + BackPrice + '</BackPrice>'
        value += '<NucPrice>' + NucPrice + '</NucPrice>'

        if ChildCount > 0:
            if chdprice == '0':
                chdprice = price
            if chdtax == '0':
                chdtax = tax

            value += '<chdprice>' + chdprice + '</chdprice>'
            value += '<chdtax>' + chdtax + '</chdtax>'
        else:
            value += '<chdprice>0</chdprice>'
            value += '<chdtax>0</chdtax>'

        value += '<chdBackPrice>' + chdBackPrice + '</chdBackPrice>'
        value += '<chdNucPrice>' + chdNucPrice + '</chdNucPrice>'
        value += '<BackAirCode>' + BackAirCode + '</BackAirCode>'

        if (BackAirCode == '' and goAirCode == BaseAirCode) or (BackAirCode != '' and goAirCode != ''\
                and BaseAirCode == goAirCode and goAirCode == BackAirCode):
            value += '<gofirstCode>' + gofirstCode + '</gofirstCode>'
            value += '<golastCode>' + golastCode + '</golastCode>'
            value += '<goPrimary>' + goPrimary + '</goPrimary>'
            value += '<backfirstCode>' + backfirstCode + '</backfirstCode>'
            value += '<backlastCode>' + backlastCode + '</backlastCode>'
            value += '<backPrimary>' + backPrimary + '</backPrimary>'
        else:
            value += '<gofirstCode></gofirstCode>'
            value += '<golastCode></golastCode>'
            value += '<goPrimary></goPrimary>'
            value += '<backfirstCode></backfirstCode>'
            value += '<backlastCode></backlastCode>'
            value += '<backPrimary></backPrimary>'
        value += '</item>'

    value += '</listitem>'
    value += '</base>'

    post_data['value'] = value

    guid = flight_json['FN']
    post_data['guid'] = guid
    post_data['type'] = 'GetJsdPolicy'

    return post_data


CrossContinent = 0x80
CrossCountry = 0x40
CrossGangAoTai = 0x20
IsChinese = 0x10
GangAoTai = "HKG,MFM,TPE,TSA,KHH,HSZ,CYI,GNI,HCN,HSZ,HUN"


def getItineraryFlags(orgPort, orgCountry, orgContinent, dstPort, dstCountry, dstContinent, reverseIndex):
    flags = 0

    if GangAoTai.find(orgPort) < 0:
        orgGAT = True
    else:
        orgGAT = False

    if (not orgGAT):
        orgCountry = 'CN'

    orgCN = (orgGAT) and (orgCountry == 'CN')

    if GangAoTai.find((dstPort)) < 0:
        dstGAT = True
    else:
        dstGAT = False

    if (not dstGAT):
        dstCountry = 'CN'

    dstCN = (dstGAT) and (dstCountry == 'CN')

    if orgContinent != dstContinent:
        flags = flags | CrossContinent

    if orgCountry != dstCountry:
        flags = flags | CrossCountry

    if (orgGAT ^ dstGAT):
        flags = flags | CrossGangAoTai

    if (orgCN or dstCN):
        flags = flags | IsChinese

    return flags



def parsePrice(content):
    price_dict = {}

    try:
        price_json = json.loads(content)
    except Exception, e:
        logger.error('Loading price failed with error: ' + str(e))
        return price_dict

    for each_price in price_json:
        price_dict[each_price['key'].replace('/','_')] = each_price['price']

    return price_dict


def durCal(dept_time_str,dest_time_str):
    dept_time = 0
    try:
        if len(dept_time_str) < 17:
            dept_time = int(time.mktime(datetime.datetime.strptime(dept_time_str, \
                '%Y-%m-%dT%H:%M').timetuple()))
        else:
            dept_time_str = dept_time_str + ':00'
            if dept_time == 0:
                dept_time = int(time.mktime(datetime.datetime.strptime(dept_time_str, \
                    '%Y-%m-%dT%H:%M:%S').timetuple()))
    except Exception, e:
        logger.info('warning: dept_time format error! ' + str(e))

    #print dept_time
    dest_time = 0
    try:
        dest_time = int(time.mktime(datetime.datetime.strptime(dest_time_str, \
                '%Y-%m-%dT%H:%M').timetuple()))
        dest_time_str = dest_time_str + ':00'
        if dest_time == 0:
            dest_time = int(time.mktime(datetime.datetime.strptime(dest_time_str, \
                    '%Y-%m-%dT%H:%M:%S').timetuple()))
    except Exception, e:
        logger.info('warning: dept_time format error! ' + str(e))

    #print dest_time
    if dept_time == 0 or dest_time == 0:
        return 0

    dur = dest_time - dept_time

    return dur


if __name__ == '__main__':

    taskcontent = '北京&beijing&巴黎&bali&20140703'

    result1 = jijitong_task_parser(taskcontent)
    print result1
    try:
        tickets = result1['para']['ticket']
        flights = result1['para']['flight']
        for x in tickets:
            print x

        for y in flights:
            print flights[y]
    except:
        print 'haha'

    #content = 'SU201_SU2462-PEK-CDG|20140605_02:30|jijitong::jijitong'

    #result2 = jijitong_request_parser(content)

    #print str(result2)
