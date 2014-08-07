#!/usr/bin/env python
#coding=UTF-8
import lxml.etree as etree
import urllib2
import cookielib
import re
import string
import sys
from common.logger import logger
from common.common import get_proxy,invalid_proxy
from util.crawl_func import crawl_single_page
from common.airport_common import Airport
from common import class_common
reload(sys)
sys.setdefaultencoding('utf-8')



word_flightdate = ['m_flightdate']
word_parent_list = ['DATEFLIGHT']
word_list = ['FLIGHT','PRICES']
word_next_list = ['PRICE']
word_child_list = [('FLIGHTNO','DEPPORT','ARRPORT','DEPTIME',\
        'ARRTIME','PLANE','STOPNUMBER'),('ADULTPRICE','ADULTCN','ADULTYQ',\
            'ADULTXT', 'ADULTCURRENCY','CABINTYPE')]
# build tree of xml
TASK_ERROR = 12
PROXY_NONE = 21
PROXY_INVALID = 22
PROXY_FORBIDDEN = 23
DATA_NONE = 24
UNKNOWN_TYPE = 25
CONTENT_LEN = 100
proxy_url = 'http://114.215.168.168:8086/proxy?source=lutaoFlight'

class nanhang_flight(class_common.Flight):
    def __init__(self):
        class_common.Flight.__init__(self)
class nanhang_eachflight(class_common.EachFlight):
    def __init__(self):
        class_common.EachFlight.__init__(self)
def get_duration(dest_time, dest_id, dept_time,dept_id):
    try:
       dept_day = dept_time.split('T')[0].split('-')[2]
       dest_day = dest_time.split('T')[0].split('-')[2]
       dept_hour = dept_time.split('T')[1].split(':')[0]
       dest_hour = dest_time.split('T')[1].split(':')[0]
       dept_min = dept_time.split('T')[1].split(':')[1]
       dest_min = dest_time.split('T')[1].split(':')[1]
    except Exception,e:
        print e
    try:
       subHours = Airport[dest_id]['timezone'] - Airport[dept_id]['timezone']
    except KeyError, e:
        print e
        return -1
    else:
        dur = (((int(dest_day) - int(dept_day))*24 - subHours + (int(dest_hour) -int(dept_hour)))*60 + int(dest_min) - int(dept_min))*60
    return dur

def csair_task_parser(taskcontent):
  result = {}
  multi_ticket = []
  one_flight = {}
  result['para'] = {'flight':one_flight, 'ticket':multi_ticket}
  result['error'] = 0
  try:
      param_list = taskcontent.strip().split('&')
      url= 'http://b2c.csair.com/B2C40/detail-'+param_list[0]+param_list[1]+'-'+param_list[2]\
    +'-1-0-0-0-1-0-1-0-1-0.g2c'
  except:
      logger.info('url param is not valid\n')
      result['error'] = TASK_ERROR
      return result
  #Initial all params
  dic_flightdate = {}
  multi_price = []
  select_time = 0
  Flag1 = False
  Flag2 = False
  page_flag = False
  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
  urllib2.install_opener(opener)
  task_content_proxy = get_proxy(source='csairFlight')
  if task_content_proxy == None:
     result['error'] = PROXY_NONE
     return result
  html = crawl_single_page(url, proxy = task_content_proxy)
  if html == '' or html == None:
    result['error'] = PROXY_INVALID
    return result
  pattern = re.compile(r'\s*<FLIGHTS>\s*')
  match = pattern.search(html)
  if match and len(html) > CONTENT_LEN:
    dom =etree.fromstring(html)
    etree.tostring(dom)
    for ele in dom.iter():
         if ele.tag is not None:
           if ele.tag in  word_flightdate:
              #print ele.tag, ele.text
              dic_flightdate[ele.tag] = ele.text
           elif ele.tag in  word_parent_list:
            page_flag = True #node of DateFIGHT
            multi_flight = []
            Flight = nanhang_flight()
            select_time += 1
            flight_num = 0
            ticket_dur_list = []
            for word in ele:
              if word.tag in word_list[0]:             
                flight_num += 1
                dic_flight = {}
                EachFlight = nanhang_eachflight()
                for word_child in word:
                  if word_child.tag  in word_child_list[0]:
                    Flag1 = True
                    dic_flight[word_child.tag]= word_child.text #each flight
                if Flag1 == True:
                    try:
                       Flag1 = False
                       EachFlight.flight_no = dic_flight[word_child_list[0][0]]
                       EachFlight.dept_id = dic_flight[word_child_list[0][1]]
                       EachFlight.dest_id = dic_flight[word_child_list[0][2]]
                       EachFlight.flight_key = EachFlight.flight_no + '_' + EachFlight.dept_id + '_'+ EachFlight.dest_id
                       dept_time = dic_flight[word_child_list[0][3]]
                       EachFlight.dept_time = dept_time[0:10] +'T'+dept_time[-5:len(dept_time)]
                       dest_time = dic_flight[word_child_list[0][4]]
                       EachFlight.dest_time = dest_time[0:10] +'T'+dest_time[-5:len(dest_time)]
                       EachFlight.dur = get_duration(dest_time,EachFlight.dest_id, dept_time,EachFlight.dept_id)
                       EachFlight.dept_time = EachFlight.dept_time + ':00'
                       EachFlight.dest_time = EachFlight.dest_time+ ':00'
                       ticket_dur_list.append(EachFlight.dur)
                       EachFlight.airline = '南方航空公司'
                       EachFlight.plane_no =  dic_flight[word_child_list[0][5]]   # rebulid and compute flight
                    except KeyError,e:
                        print e
                    else:
                        one_flight[EachFlight.flight_key] = (EachFlight.flight_no, EachFlight.airline, EachFlight.plane_no,EachFlight.dept_id,EachFlight.dest_id,EachFlight.dept_time, EachFlight.dest_time,EachFlight.dur)
                        multi_flight.append((EachFlight.flight_key,EachFlight.flight_no, EachFlight.airline, EachFlight.plane_no,EachFlight.dept_id,EachFlight.dest_id,EachFlight.dept_time, EachFlight.dest_time,EachFlight.dur)) #list of multi flight
              elif word.tag in  word_list[1]:  
                multi_price = [] #node of price
                for word_child in word:
                  if word_child.tag in word_next_list:
                      dic_ticket = {}
                      for word_next_child in word_child:
                        if word_next_child.tag in word_child_list[1]:
                          Flag2 = True
                          dic_ticket[word_next_child.tag] = word_next_child.text
                      if Flag2 == True:
                          try:
                            Flag2 = False
                            Flight.price = string.atof(dic_ticket[word_child_list[1][0]])
                            Flight.tax = string.atof(dic_ticket[word_child_list[1][1]]) + string.atof(dic_ticket[word_child_list[1][2]]) + string.atof(dic_ticket[word_child_list[1][3]])
                            Flight.currency = dic_ticket[word_child_list[1][4]]
                            Flight.seat_type = dic_ticket[word_child_list[1][5]]
                            if Flight.seat_type == 'ECONOMY':
                              Flight.seat_type = '经济舱'
                            if Flight.seat_type =='BUSINESS':
                              Flight.seat_type = '商务舱'
                            if Flight.seat_type == 'FIRST':
                              Flight.seat_type = '头等舱'
                            if Flight.seat_type == 'PREMIUMECONOMY':
                              Flight.seat_type = '超经济舱'
                            Flight.return_rule = 'NULL'
                            Flight.stop = flight_num - 1
                            Flight.surcharge = -1
                            Flight.source = 'csair::csair'
                          except KeyError,e:
                              print e
                          else:
                              multi_price.append((Flight.price, Flight.tax, Flight.surcharge, Flight.currency,Flight.seat_type, Flight.source, Flight.return_rule, Flight.stop))
            if select_time is not 0:
               if multi_flight != []:
                 new_flight_no = []
                 Flight.fight_no = '_'.join([item[1] for item in multi_flight])
                 Flight.plane_no = '_'.join([item[3] for item in multi_flight])
                 Flight.airline = '_'.join([item[2]for item in multi_flight])
                 Flight.dept_id = multi_flight[0][4]
                 Flight.dest_id = multi_flight[len(multi_flight)-1][5]
                 Flight.dept_day = dic_flightdate[word_flightdate[0]][0:4]+'-'+ dic_flightdate[word_flightdate[0]][4:6]+'-'+dic_flightdate[word_flightdate[0]][6:8]
                 Flight.dept_time = multi_flight[0][6]
                 Flight.dest_time = multi_flight[len(multi_flight)-1][7]
                 Flight.dur = get_duration(Flight.dest_time,Flight.dest_id,Flight.dept_time,Flight.dept_id)
                 for i in range(len(multi_price)):
                   multi_ticket.append((Flight.fight_no,Flight.plane_no,Flight.airline,Flight.dept_id,Flight.dest_id,\
                     Flight.dept_day,Flight.dept_time, Flight.dest_time,Flight.dur, multi_price[i][0], multi_price[i][1],\
                     multi_price[i][2], multi_price[i][3],multi_price[i][4],multi_price[i][5],multi_price[i][6], multi_price[i][7]))
      # print every ticket and ervery flight
    if page_flag == True:
      print 'the num of tickets is '+ str(len(multi_ticket))
      result['error'] = 0
      return result
    else:
        result['error'] = UNKNOWN_TYPE
        return result
  else:
       if html.find('NEEDVERIFY') != -1:
           invalid_proxy(proxy=task_content_proxy,source='csairFlight')
           return {'para':{'flight':{},'ticket':[]},'error':PROXY_INVALID}
       else:
           return {'para':{'flight':{},'ticket':[]},'error':DATA_NONE}

def csair_request_parser(content):
    result = -1
    return result


'''if __name__ == '__main__':

    proxy_flag = False
    proxy = None
    taskcontent = 'PEK&PAR&20140730'
    result = csair_task_parser(taskcontent)
    if result['error'] == 0:
             proxy_flag = True
             try:
                 for item in result['para']['ticket']:
                     sql = 'insert into flight_test(flight_no,plane_no,airline,dept_id,dest_id,dept_day,dept_time,\
                     dest_time,dur,price,tax,surcharge,currency,seat_type,source,return_rule,stop) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                     params = (item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],int(item[8]),item[9],item[10],item[11],item[12],item[13],item[14],item[15],int(item[16]))
                     len_db = db.ExecuteSQL(sql,params)
                           #print len_db
                     if len_db is False:
                         print 'error of sql'
                 for key in result['para']['flight']:
                     dic_flight = result['para']['flight'][key]
                     sql = 'insert into  flight(flight_key,flight_no,airline,plane,dept_id,dest_id,dept_time,dest_time,dur) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                     params = (key,dic_flight[0],dic_flight[1],dic_flight[2],dic_flight[3],dic_flight[4],dic_flight[5],dic_flight[6],dic_flight[7])
                     len_db = db.ExecuteSQL(sql,params)
                     if len_db is  False:
                          print 'error of sql'
             except Exception,e:
                 print e

    else:
             proxy_flag = False'''

