#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2014-02-23
    @author: devingong
    @desc:
        
'''

import sys
import urllib
import urllib2
import time
from logger import logger

TIME_OUT = 30

def form_cookie_str(cookie):
    '''
        将dict拼装成cookie格式
        @param cookie: cookie内容，存放再dict中
        @return: 返回拼装好得字符串
    '''
    return ";".join([k+"="+v for k,v in cookie.items()])

def parse_set_cookie(headers, cookie):
    '''
        从HTTP headers中解析COOKIE
        @params headers: HTTP headers
        @param cookie: 保持解析后的cookie信息
    '''
    if headers == None:
        return
    for header in headers:
        strs = header.split(":", 1)
        if len(strs) != 2 or strs[0] != "Set-Cookie":
            continue
        strs = strs[1].split(";")
        for s in strs:
            temp = s.strip().split("=")
            if len(temp) == 2:
                cookie[temp[0]] = temp[1]

# crawl a single page, if failed try n times at most
def crawl_single_page(url, n=2, referer = None, proxy = None, cookie = {}, **headers):
     
    #handler=urllib2.HTTPHandler(debuglevel=1)
    #opener = urllib2.build_opener(handler) 
    #urllib2.install_opener(opener)
    req = urllib2.Request(url)

    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('X-Requested-With','XMLHttpRequest')
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116')
    if len(cookie) > 0:
        req.add_header("Cookie", form_cookie_str(cookie))
    if proxy != None:
        req.set_proxy(proxy, "http")
    
    if referer:
        req.add_header('Referer', referer)    
    
    if headers:        
        for k in headers.keys():            
            req.add_header(k,headers[k])    

    response = ''
    i = 0
    while i < n and len(response) < 1:#10:
        logger.info("trying " + str(i + 1) + " th time crawling " + url)
        i += 1
        try:
            resp = urllib2.urlopen(req, timeout = TIME_OUT)
            if resp != None:
                # 处理COOKIE
                parse_set_cookie(resp.info().headers, cookie)
            response = resp.read()
        except urllib2.HTTPError, e:
            logger.error('HTTPError: ' + str(e.code))
        except Exception, e:
            logger.error('Error: ' + str(e))
        
        if len(response) > 30:
            break
    return response

# request ajax data
def request_post_data(url, data, n=2, referer=None, cookie=None, proxy = None, **headers):
    logger.info("crawling " + url + '?' + str(data))
    
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('X-Requested-With','XMLHttpRequest')
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116')
    if proxy != None:
        req.set_proxy(proxy, "http")

    if referer:
        req.add_header('Referer', referer)    
    
    if cookie:
        req.add_header('Cookie', cookie)
    
    if headers:        
        for k in headers.keys():            
            req.add_header(k,headers[k])    

    params = urllib.urlencode(data)
    response = ''
    i = 0
    while i < n and len(response) < 10:
        logger.info("trying " + str(i + 1) + " th time crawling " + url)
        i += 1
        try:
            response = urllib2.urlopen(req, params, timeout = TIME_OUT).read()
        except urllib2.HTTPError, e:
            logger.error('HTTPError: ' + str(e.code))
        except Exception, e:
            logger.error('Error: ' + str(e))
            
        if len(response) > 30:
            break
    
    return response

if __name__=='__main__':
    data = {'action':'ajaxmaplist','page':6,'id':20,'typename':'city'}
    s = request_post_data('http://place.qyer.com/ajax.php', data)
    #print s
    
    s = crawl_single_page('http://www.sina.com.cn/')
    #print s
