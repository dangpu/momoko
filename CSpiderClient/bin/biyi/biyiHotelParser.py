#! /usr/bin/env python
#coding=UTF8

'''
    @author:fangwang
    @date:2014-04-20
    @desc: crawl and parse biyi hotel data
'''

import re
import json
import sys
sys.path.append('/home/workspace/spider/SpiderClient/bin/common/')
import datetime
import time
import random
from logger import logger
from common import get_proxy
from class_common import Hotel
from util.multi_times_crawler import with_cookie_crawler

reload(sys)
sys.setdefaultencoding('utf-8')

image_url_pat = re.compile(r"HC.SpriteGallery.addSlideShowPhoto\({'url': '(.*?)'", re.S|re.M)
address_pat = re.compile(r'<p class="hc_htl_intro_addr">(.*?)</p>', re.S|re.M)
desc_pat = re.compile(r'<p>(.*?)<div class="cDivBoth"></div>', re.S|re.M)
star_pat = re.compile(r'<span class="hc_htl_rating" title="(.*?)星级酒店">', re.S|re.M)
grade_pat = re.compile(r"itemprop='ratingValue' content='(.*?)'><span", re.S|re.M)
service_temp_pat = re.compile(r'<div class="hc_m_content">(.*?)<div class="cDiv"></div>', re.S|re.M)
each_service_pat = re.compile(r'<p>(.*?)</p>', re.S|re.M)


def biyi_hotel_parser(taskcontent):
    taskcontent = taskcontent.strip()
    taskcontent = taskcontent.encode('utf-8')
    try:
        hotel_id = taskcontent.strip().split('&')[0]
        print hotel_id
        hotel_name = taskcontent.strip().split('&')[1]
        print hotel_name
        map_info = taskcontent.strip().split('&')[2]
        city_name_zh = taskcontent.strip().split('&')[3]
        city_name_en = taskcontent.strip().split('&')[4]
        country_name_zh = taskcontent.strip().split('&')[5]
        check_in_day_temp = taskcontent.strip().split('&')[6]
    except Exception, e:
        logger.error('Can not parse taskcontent!' + str(e))
        return []
        
    check_in_day = check_in_day_temp[:4] + '-' + check_in_day_temp[4:6] + '-' + \
            check_in_day_temp[6:]
    
    check_out_day_temp = datetime.datetime(int(check_in_day_temp[:4]),int(check_in_day_temp[4:6]), \
            int(check_in_day_temp[6:]))
    check_out_day = str(check_out_day_temp  + datetime.timedelta(days = 1))[:10]
    
    first_url = 'http://www.biyi.cn/'
    url = get_url(hotel_name)
    
    if url != '':
        content = ''
        i = 0
        while i < 1 and len(content) < 3000:
            #p = None
            #p = get_proxy()
            p = '222.26.174.209:18186'
            i += 1
            sleep_time = int(random.uniform(5, 10))
            time.sleep(sleep_time)
            content = with_cookie_crawler(first_url=first_url, second_url=url, proxy=p)
            if len(content) > 3000:
                #print content
                #fout = open('biyiweb3.html','w')
                #fout.write(content)
                #fout.close()
                break

    if content != '' and len(content) > 3000:
        hotel_list = parsePage(content,hotel_id,hotel_name,city_name_zh,country_name_zh, \
                map_info)
        return hotel_list
        #print hotel_list
    else:
        return []


def parsePage(content,hotel_id,hotel_name,city_name_zh,country_name_zh,map_info):
    if content != '' and len(content) > 3000:
        hotel = Hotel()
        hotel.source_id = hotel_id
        hotel.hotel_name = hotel_name
        hotel.hotel_name_en = hotel_name
        hotel.source = 'biyi'
        hotel.map_info = map_info
        hotel.city = city_name_zh
        hotel.country = country_name_zh

        try:
            description_text = service_temp_pat.findall(content)[2]
            desc_temp = desc_pat.findall(description_text)[0]
            desc_num = desc_temp.find('</p>')
            if desc_num > 0:
                desc_temp = desc_temp[:desc_num]
            else:
                desc_temp = desc_temp
            hotel.description = desc_temp.replace('&amp;','&').replace('<br/><br/>','').replace("&#39;","'")
            #print hotel.description
        except Exception, e:
            logger.info('Can not parse hotel description!' + str(e))
            hotel.description = 'NULL'

        try:
            service_temp = service_temp_pat.findall(content)[3]
            #print 'service_temp:' + service_temp
            m = service_temp.find('入住日期')
            if m > 0:
                service_text = service_temp[:m]
            else:
                service_text = service_temp
            each_service = each_service_pat.findall(service_text)
            hotel_service_temp = ''
            if each_service != []:
                for each_service_content in each_service:
                    hotel_service_temp = hotel_service_temp + \
                            each_service_content.strip().replace(',','|') + '|'
            
            if len(hotel_service_temp) > 5:
                hotel.service = hotel_service_temp[:-1].replace(' ','')

                if '无线' in hotel.service or 'wifi' in hotel.service \
                        or 'WiFi' in hotel.service:
                            hotel.has_wifi = 'Yes'
                            hotel.is_wifi_free = 'Yes'

                if '停车' in hotel.service:
                    hotel.has_parking = 'Yes'

                if '免费停车' in hotel.service:
                    hotel.is_parking_free = 'Yes'
            else:
                hotel.service = 'NULL'
        except Exception, e:
            logger.info('Can not parse hotel description!' + str(e))
            hotel.service = 'NULL'
        
        try:
            star = star_pat.findall(content)[0]
            hotel.star = star
        except:
            logger.info('Cannot parse hotel star num!')
            hotel.star = -1.0

        try:
            grade_temp = grade_pat.findall(content)[0]
            hotel.grade = grade_temp
        except Exception, e:
            logger.info('Cannot parse hotel grade num!' +  str(e))
            hotel.grade = 'NULL'

        try:
            address_temp = address_pat.findall(content)[0]
            hotel.address = address_temp.strip()
        except Exception, e:
            logger.error('Can not parse hotel address!' + str(e))
            return []
 
        try:
            image_url_temp = image_url_pat.findall(content)
            #print image_url_temp
            image_url = ''
            if len(image_url_temp) > 0:
                for each_url in image_url_temp:
                    image_url = image_url + each_url.strip() + '|'
            if len(image_url) > 10:
                hotel.img_items = image_url[:-1]
            else:
                logger.info('Can not parse hotel image urls!')
                hotel.img_items = 'NULL'
        except Exception, e:
            logger.info('Cannot parse hotel image url!' + str(e))
            hotel.img_url = 'NULL'

        hotel_tuple = (hotel.hotel_name, hotel.hotel_name_en, hotel.source, \
                hotel.source_id, hotel.brand_name, hotel.map_info, hotel.address, \
                hotel.city, hotel.country, hotel.postal_code, hotel.star, \
                hotel.grade, hotel.has_wifi, hotel.is_wifi_free, hotel.has_parking, \
                hotel.is_parking_free, hotel.service, hotel.img_items, \
                hotel.description)
        
        return hotel_tuple


def get_url(hotel_name):
    url = ''
    url = 'http://www.biyi.cn/Hotel/' + hotel_name + '.htm'
    
    return url 


if __name__ == '__main__':
    #fileHandle = open('/home/workspace/spider/SpiderClient/bin/workload/workload_content/biyi/biyicontent_20140503.txt','r')
    #hotel_temp_list = fileHandle.reaedlines()
    #for x in hotel_temp_list:
    #    print x 
    #    time.sleep(5)
    taskcontent = '1180526&Le_Ville_del_Lido_Suite_Residence&12.373191,45.411504&威尼斯&Venice&意大利&20140501'
    
    biyi_hotel_parser(taskcontent)

