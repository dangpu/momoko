#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2014-03-22
    @author: devin
    @desc:
        
'''
import jsonlib
from util import http_client


proxy_client = http_client.HttpClientPool("114.215.168.168:8086")

def set_proxy_client(client):
    global proxy_client
    proxy_client = client

def get_proxy(source = None):
    if source != None:
        p = proxy_client.get("/proxy?source=%s"%source)
    else:
        p = proxy_client.get("/proxy?source=") 
    if len(p) < 7: 
        p = None
    return p

def invalid_proxy(proxy,source):
    if proxy != None:
        proxy_client.get("/update_proxy?status=Invalid&p=%s&source=%s"%(proxy,source))
