#! /usr/bin/env python 
#coding=UTF8

"""
    @author:fangwang
    @date:2014-04-17
    @desc:Crawl the website that need cookie
"""

import time
import urllib
import urllib2
import cookielib
from logger import logger

TIME_OUT = 30

def first_time_crawl(url, proxy = None):
    
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))             
    urllib2.install_opener(opener)

    req = urllib2.Request(url)
    
    req.add_header('Content-Type', 'text/html; charset=UTF-8')
    req.add_header('User-Agent', \
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36')
    req.add_header('Accept', \
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    req.add_header('Accept-Language', 'zh-CN,zh;q=0.8,en;q=0.6')
    req.add_header('Cache-Control', 'max-age=0')
    if proxy != None:
        req.set_proxy(proxy,'http')

    try:
        resp = urllib2.urlopen(req)
        logger.info('Crawl ' + url + ' success!')
    except urllib2.HTTPError, e:
        logger.error('HTTPError: ' + str(e.code))
    except Exception, e:
        logger.error('Error: ' + str(e))


def crawl_single_page(url, proxy = None, n = 1, min_page_len = 3000):
    req = urllib2.Request(url)

    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36')
    req.add_header('Cache-Control', 'max-age=0')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    if proxy != None:
        req.set_proxy(proxy, 'http')

    response = ''
    i = 0
    while i < n :
        logger.info('trying ' + str(i + 1) + ' th time crawling ' + url)
        i += 1
        try:
            resp = urllib2.urlopen(req, timeout = TIME_OUT)
            response = resp.read()
            print len(response)
        except urllib2.HTTPError, e:
            logger.error('HTTPError: ' + str(e.code))
        except Exception, e:
            logger.error('Error: ' + str(e))
        
        if len(response) > min_page_len:
            break
    return response


def crawl_with_cookie(first_url, second_url, n=1, proxy = None):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    req = urllib2.Request(first_url)

    req.add_header('Content-Type', 'text/html; charset=UTF-8')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    req.add_header('Accept-Language', 'zh-CN,zh;q=0.8,en;q=0.6')
    req.add_header('Cache-Control', 'max-age=0')
    if proxy != None:
        req.set_proxy = (proxy, 'http')

    try:
        resp = urllib2.urlopen(req)
        logger.info('Crawl ' + first_url + ' success!')
    except urllib2.HTTPError, e:
        logger.error('HTTPError: ' + str(e.code))
    except Exception, e:
        logger.error('Error: ' + str(e))

    req = urllib2.Request(second_url)

    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36')
    req.add_header('Cache-Control', 'max-age=0')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    if proxy != None:
        req.set_proxy(proxy, 'http')

    response = ''
    i = 0
    while i < n and len(response) < 3000:
        logger.info('trying ' + str(i + 1) + ' th time crawling ' + second_url)
        i += 1
        try:
            resp = urllib2.urlopen(req, timeout = TIME_OUT)
            response = resp.read()
        except urllib2.HTTPError, e:
            logger.error('HTTPError: ' + str(e.code))
        except Exception, e:
            logger.error('Error: ' + str(e))
                                                                             
        if len(response) > 3000:
            break
    return response


def with_cookie_crawler(first_url, second_url, proxy, min_page_len = 3000):
    first_time_crawl(url = first_url, proxy = proxy)
    response = crawl_single_page(url = second_url, proxy = proxy, min_page_len = min_page_len)

    return response


if __name__ == '__main__':
    first_url = 'http://www.biyi.cn/'
    second_url = 'http://www.biyi.cn/SearchResultsList.aspx?languageCode=CS&currencyCode=CNY&destination=place:Paris&radius=0km&checkin=2014-04-27&checkout=2014-04-28&Rooms=1&adults_1=2&pageSize=15&pageIndex=0&sort=Popularity-desc&showSoldOut=false&scroll=0&mapState=expanded%3D0&r=0.48774764402257809'
    proxy = '221.182.89.234:63000'
    #first_time_crawl(first_url, proxy = proxy)
    #page = crawl_single_page(second_url,proxy)
    #page = crawl_with_cookie(first_url,second_url,proxy=proxy)
    page = with_cookie_crawler(first_url, second_url, proxy)
    print len(page)
