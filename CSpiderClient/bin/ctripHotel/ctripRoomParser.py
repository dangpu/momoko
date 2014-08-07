#! /usr/bin/env python
#coding=UTF8

'''
    @author:fangwang
    @date:2014-05-13
    @desc: crawl and parse ctrip room data via API
'''

import sys
#sys.path.append('/home/workspace/wangfang/SpiderClient/bin/')
#sys.path.append('/home/workspace/wangfang/SpiderClient/lib/')
import datetime
import time
from suds.client import Client
from xml.dom import minidom
import hashlib
import re
from LOG import _ERROR, _INFO
from common.class_common import Room
from common.insert_db import InsertHotel_room

reload(sys)
sys.setdefaultencoding('utf8')

URL = 'http://openapi.ctrip.com/Hotel/OTA_HotelRatePlan.asmx?wsdl'

TASK_ERROR = 12

PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24

#pattern
hoteldesc_pat = re.compile(r'<HotelDescriptiveContent.*?</HotelDescriptiveContent>', re.S)

rateplans_pat = re.compile(r'<RatePlans H.*?</RatePlans>', re.S)
reverse_rateplans_pat = re.compile(r'>snalPetaR/<.*?snalPetaR<', re.S)
hotelcode_pat = re.compile(r'otelCode="(.+?)"', re.S)
rateplan_pat = re.compile(r'<RatePlan RatePlanCode.*?</RatePlan>', re.S)
roomcode_pat = re.compile(r'RatePlanCode="(.+?)"', re.S)
rate_pat = re.compile(r'<Rate Start.*?</Rate>', re.S)
rate_ses_pat = re.compile(r'Rate Start="(.+?)" End="(.+?)" Status="(.+?)"', re.S)

price_pat = re.compile(r'<BaseByGuestAmt AmountBeforeTax="(.+?)" CurrencyCode="(.+?)" NumberOfGuests="(.+?)" ListPrice="(.+?)" />')
price_pat2 = re.compile(r'<BaseByGuestAmt AmountBeforeTax="(.+?)" CurrencyCode="(.+?)" NumberOfGuests="(.+?)" />')
price_pat_3 = re.compile(r'<BaseByGuestAmt AmountBeforeTax="(.*?)" CurrencyCode="(.*?)" RateOverrideIndicator="(.*?)" NumberOfGuests="(.*?)" />')
extrafees_pat = re.compile(r'<Fee Code.*?</Fee>', re.S)
feecode_pat = re.compile(r'Code="(.+?)"', re.S)
feeamount_pat = re.compile(r'Amount="(.+?)"', re.S)
desc_pat = re.compile(r'<Description>.*?<Text>(.+?)</Text>.*?</Description>', re.S)
cancel_pat = re.compile(r'<AmountPercent Amount="(.*?)"')
meals_pat = re.compile(r'<MealsIncluded Breakfast="(.*?)"', re.S)
promotion_pat = re.compile(r'<RebatePromotion StartPeriod="(.+?)" EndPeriod="(.+?)".*?Amount="(.+?)".*?Code="(.+?)">', re.S)
room_type_pat = re.compile(r'</SellableProducts><Description Name="(.*?)" />',re.S|re.M)
room_type_pat2 = re.compile(r'</SellableProducts><Description Name="(.*?)"><Text>(.*?)</Text>', re.S)


def ctrip_room_parser(taskcontent):
    result = {}
    result['para'] = None
    result['error'] = 0

    try:
        check_in_temp,days_temp,hotel_id_content,city = taskcontent.split('&')[3],taskcontent.split('&')[0], \
        taskcontent.split('&')[1],taskcontent.split('&')[2]
    except Exception,e:
        _ERROR('ctrip_room_parser',['Parse taskcontent failed', str(e)])
        result['error'] = TASK_ERROR
        return result

    days = int(days_temp) - 1
    hotel_id_set = get_hotelid_set(hotel_id_content)
    check_in = check_in_temp[:4] + '-' + check_in_temp[4:6] + '-' + \
        check_in_temp[6:]
    check_out_temp = datetime.datetime(int(check_in_temp[:4]), int(check_in_temp[4:6]), \
                                       int(check_in_temp[6:]))
    check_out = str(check_out_temp + datetime.timedelta(days=days))[:10]

    client = getSoapClient(URL)

    #print hotel_id_set,check_in,check_out
    #time.sleep(5)
    room_list = getRatePlanByHotelCode(client,hotel_id_set,check_in,check_out,city)

    if room_list == [] or room_list == None:
        result['error'] = DATA_NONE = 24
        return result

    result['para'] = room_list
    return result

def ctrip_room_request_parser(content):

    result = -1

    return result


def get_hotelid_set(content):
    hotel_id_set = set([])
    if content == '' or len(content) < 1:
        return hotel_id_set

    hotel_id_list = content.split('-')
    for hotelid in hotel_id_list:
        hotel_id_set.add(hotelid)

    return hotel_id_set


def Signate(AllianceID, SID, SecretKey, TimeStamp, RequestType):
    return hashlib.md5((TimeStamp+AllianceID+hashlib.md5(SecretKey).hexdigest().upper()+SID+RequestType)).hexdigest().upper()


def getSoapClient(url):
    _INFO('', ['trying get soap client, url = ' + url])
    try:
        client = Client(url)
        _INFO('', ['Getting Soap Clent, Success'])
        #print client
    except Exception, e:
        _ERROR('', ['Getting Soap Clent, Failed'])
        sys.exit(-1)
    return client


def getRatePlanByHotelCode(client, hotelcode_set, from_date, to_date, city):
    AllianceID = '15951'
    SID = '439022'
    SecretKey = '4F3E7530-391A-45A3-829B-880FFBBC4264'
    TimeStamp = str(int(time.time()))
    RequestType = 'OTA_HotelSearch'
    Signature=Signate(AllianceID, SID, SecretKey, TimeStamp, RequestType)
    #print Signature

    req_xml = minidom.getDOMImplementation()
    dom = req_xml.createDocument(None, 'Request', None)
    root = dom.documentElement

    header = dom.createElement('Header')
    header.setAttribute('AllianceID', AllianceID)
    header.setAttribute('SID', SID)
    header.setAttribute('TimeStamp', TimeStamp)
    header.setAttribute('RequestType', RequestType)
    header.setAttribute('Signature', Signature)

    hotel_request = dom.createElement('HotelRequest')
    request_body = dom.createElement('RequestBody')
    request_body.setAttribute('xmlns:ns', 'http://www.opentravel.org/OTA/2003/05')
    request_body.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    request_body.setAttribute('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

    ns_ota_hsr = dom.createElement('ns:OTA_HotelRatePlanRQ')
    ns_ota_hsr.setAttribute('Version', '1.0')
    ns_ota_hsr.setAttribute('TimeStamp', '2012-05-01T00:00:00.000+08:00')

    ns_rate_plans = dom.createElement('ns:RatePlans')
    ns_rate_plan = dom.createElement('ns:RatePlan')
    ns_date_range = dom.createElement('ns:DateRange')
    ns_date_range.setAttribute('Start', from_date)
    ns_date_range.setAttribute('End', to_date)
    ns_rate_plan_candidates = dom.createElement('ns:RatePlanCandidates')

    for hotelcode in hotelcode_set:
        ns_rate_plan_candidate = dom.createElement('ns:RatePlanCandidate')
        ns_rate_plan_candidate.setAttribute('AvailRatesOnlyInd', 'false')
        ns_hotel_refs = dom.createElement('ns:HotelRefs')
        ns_hotel_ref = dom.createElement('ns:HotelRef')
        ns_hotel_ref.setAttribute('HotelCode', hotelcode)

        ns_hotel_refs.appendChild(ns_hotel_ref)
        ns_rate_plan_candidate.appendChild(ns_hotel_refs)
        ns_rate_plan_candidates.appendChild(ns_rate_plan_candidate)

    ns_rate_plan.appendChild(ns_date_range)
    ns_rate_plan.appendChild(ns_rate_plan_candidates)
    ns_rate_plans.appendChild(ns_rate_plan)
    ns_ota_hsr.appendChild(ns_rate_plans)

    request_body.appendChild(ns_ota_hsr)
    hotel_request.appendChild(request_body)
    root.appendChild(header)
    root.appendChild(hotel_request)

    xml_str = dom.toxml().decode('utf-8')

    room_list = []
    try:
        resp = client.service.Request(xml_str)
        resp = resp.__str__()

        _INFO('client.service.Request', ['hotelcode = ' + hotelcode + ', len = ' + str(len(resp))])

        room_list = parsePrice(resp, city)
        #print 'ok2'
        _INFO('ctripHotel::parsePrice',['Parsed ' + str(len(room_list)) + ' values'])
    except Exception, e:
        _ERROR('ctripHotel::getRatePlanByHotelCode', ['hotelcode = ' + str(hotelcode), str(e)])
        return room_list

    return room_list


def parsePrice(content_temp, city):
    all_price = []
    content = xmlescape(content_temp).replace('\n', '')

    #print content_temp
    try:
        each_hotel_content_list = rateplans_pat.findall(content)
        if len(each_hotel_content_list) == 0:
            return all_price
        _INFO('ctripHotel::parseRoom',['Parse price failed because of no hotel found'])
    except Exception, e:
        _ERROR('ctripHotel::parseRoom',['Parse price failed because of no hotel found',str(e)])

    for each_hotel_content in each_hotel_content_list:
        room = Room()

        try:
            room.source_hotelid = pattern_search(hotelcode_pat, each_hotel_content)
            if room.source_hotelid == 'NULL':
                _INFO('ctripHotel::parseRoom',['Cannot parse this hotel id'])
        except Exception, e:
            _ERROR('ctripHotel::parseRoom',['Cannot parse this hotel', str(e)])
        #print room.source_hotelid

        try:
            each_room_content_list = rateplan_pat.findall(each_hotel_content)
            if len(each_room_content_list) == 0:
                _ERROR('ctripHotel::parseRoom',['Parse this room failed'])
                return room_list
        except Exception, e:
            _ERROR('ctripHotel::parseRoom',['Parse this room failed',e])
            return room_list
        for each_room_content in each_room_content_list:
            #print each_room_content
            try:
                room.source_roomid = pattern_search(roomcode_pat,each_room_content)
            except Exception,e:
                _ERROR('ctripHotel::parseRoom',['Parse this room failed',str(e)])
                return room_list

            try:
                #print 'okkkkkkkkkkkkkkkkkkkkkkkkkkkkkk'
                room.room_type = room_type_pat.findall(each_room_content)[0]
            except:
                #print 'faillllllllllllllllleddddddddddddddddddd'
                try:
                    room_type_info = room_type_pat2.findall(each_room_content)[0]
                    #print '^^--^^'
                    room.room_type = room_type_info[0]
                    room.room_desc = room_type_info[1]
                except Exception, e:
                    _ERROR('ctripHotel::parseRoom',['Parse room type failed!', str(e)])
                    return room_list

            each_night_content_list = rate_pat.findall(each_room_content)
            if len(each_night_content_list) == 0:
                _ERROR('ctripHotel::parseRoom',['Parse this day content failed'])
                continue

            for each_night_content in each_night_content_list:
                #print each_night_content
                try:
                    [start_temp,end_temp,status] = pattern_search3(rate_ses_pat, each_night_content)
                    check_in_temp = start_temp.split(' ')[0]
                    check_in = datetime.datetime(int(check_in_temp.split('-')[0]), int(check_in_temp.split('-')[1]), \
                            int(check_in_temp.split('-')[2]))
                    room.check_in = str(check_in)[:10]
                    room.check_out = str(check_in + datetime.timedelta(days=1))[:10]
                    if status == 'Close':
                        _INFO('ctripHotel::parseRoom',['No room',room.check_in])
                        continue
                    try:
                        [room.price, room.currency,price_temp_name,room.occupancy] = pattern_search4(price_pat_3, each_night_content)
                    except Exception, e:
                        _ERROR('',[str(e)])

                    try:
                        if '加床' in each_night_content:
                            room.is_extrabed = 'Yes'
                        if '免费加床' in each_night_content:
                            room.is_extrabed_free = 'Yes'
                    except Exception, e:
                        _INFO('ctripHotel::parseRoom',['Parse extrabed info failed', str(e)])


                    try:
                        meals_info = pattern_search(meals_pat, each_night_content)

                        if meals_info == 'true':
                            room.has_breakfast = 'Yes'
                            room.is_breakfast_free = 'Yes'
                    except Exception, e:
                        _INFO('ctripHotel::parseRoom',['Parse breakfast info failed',str(e)])

                    try:
                        cancel_info = pattern_search(cancel_pat, each_night_content)
                        if cancel_info == '0.00':
                            room.is_cancel_free = 'Yes'
                    except Exception, e:
                        _INFO('ctripHotel::parseRoom',['Parse cancel info failed', str(e)])


                    room.source = 'ctrip'
                    room.real_source = 'ctrip'
                    room.city = city

                    room_tuple = (room.hotel_name, room.city, room.source, room.source_hotelid, \
                            room.source_roomid, room.real_source, room.room_type, room.occupancy, \
                            room.bed_type, room.size, room.floor, room.check_in, room.check_out, \
                            room.price, room.tax, room.currency, room.is_extrabed, room.is_extrabed_free, \
                            room.has_breakfast, room.is_breakfast_free, room.is_cancel_free, \
                            room.room_desc)
                    #print room_tuple
                    all_price.append(room_tuple)

                except Exception, e:
                    _ERROR('ctripHotel::parseRoom',['Parse check_in and check_out failed!', str(e)])
                    continue

    return all_price


def xmlescape(s):
    return s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&nbsp;', ' ').replace('#228;', 'a')


def pattern_search(pat, s):
    m = pat.search(s)
    if m:
        return m.group(1)
    else:
        return 'NULL'


def pattern_search2(pat, s):
    m = pat.search(s)
    if m:
        return [m.group(1), m.group(2)]
    else:
        return ['NULL', 'NULL']


def pattern_search3(pat, s):
    m = pat.search(s)
    if m:
        return [m.group(1), m.group(2), m.group(3)]
    else:
        return ['NULL', 'NULL', 'NULL']

def pattern_search4(pat, s):
    m = pat.search(s)
    if m:
        return [m.group(1), m.group(2), m.group(3), m.group(4)]
    else:
        return ['NULL', 'NULL', 'NULL', 'NULL']


def pattern_findall(pat, s):
    l = pat.findall(s)
    #print l
    ret = ''
    for i in xrange(0, len(l)):
        if len(l[i]) != 2:
            continue
        ret += l[i][1] + ':' + l[i][0] + '|'
    if len(ret) > 5:
        ret = ret[0:len(ret)-1]
        return ret
    else:
        return 'NULL'


def service_pattern_findall(pat, s):
    l = pat.findall(s)
    ret = ''
    for i in xrange(0, len(l)):
        if len(l[i]) != 3:
            continue
        ret += l[i][1] + '::' + l[i][0] + '::' + l[i][2] + '|'
    if len(ret) > 5:
        ret = ret[0:len(ret)-1]
        return ret
    else:
        return 'NULL'


def imgitem_pattern_findall(pat, s):
    l = pat.findall(s)
    ret = ''
    for i in xrange(0, len(l)):
        if len(l[i]) != 3:
            continue
        if len(l[i][2]) <= 0:
            ret += l[i][0] + '::NULL::' + l[i][1] + '|'
        else:
            ret += l[i][0] + '::' + l[i][2] + '::' + l[i][1] + '|'
    if len(ret) > 5:
        ret = ret[0:len(ret)-1]
        return ret
    else:
        return 'NULL'


def text_pattern_findall(pat, s):
    l = pat.findall(s)
    ret = ''
    for i in xrange(0, len(l)):
        if len(l[i]) != 2:
            continue
        dc = re.sub('\s', ' ', l[i][1])
        ret += l[i][0] + '::' + dc + '|'
    if len(ret) > 5:
        ret = ret[0:len(ret)-1]
        return ret
    else:
        return 'NULL'

def data_writer(room_list,taskcontent):
    if room_list == []:
        _ERROR('',['room_list.size == 0'])
        return

    try:
        InsertHotel_room(room_list)
        _INFO('',[taskcontent + ' [success]'])
        _INFO('',['with ' + str(len(room_list)) + ' values!'])
    except Exception, e:
        _ERROR('',[taskcontent + '[failed]'])
        _ERROR('',[str(e)])


if __name__ == '__main__':
    #each_content = '20140602&3&252238|252239|252233|252234|252235|252237|382220|318443|318354|318468&格但斯克'
    #taskcontent = '118292&20140602&2'
    fileHandle = open('ctriphotelcontent_20140601.txt','r')
    content = fileHandle.read()
    content_list = content.split('\n')
    for each_content in content_list[:20]:
        room_list = ctrip_room_parser(each_content)
        data_writer(room_list,each_content)
