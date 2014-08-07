#!/usr/bin/env python
#coding=UTF-8
'''
    @author: devin
    @desc: 抓取航班数据
'''

import time
import random
import Crawler
import jsonlib
from common import *
from storage import *
from lxml import etree
from urlparse import urljoin
import re

SCHEDULE_URL = "http://flights.ctrip.com/schedule/"
INTER_SCHEDULE_URL = "http://flights.ctrip.com/international/schedule/"

URL_PATTERN = re.compile("([\w]{3})[.|-]([\w]{3}).html$")

html_parser = etree.HTMLParser()

def GetPage(url):
    while True:
        p = GetProxy()
        page = Crawler.CrawlSinglePage(url, proxy=p)
        if len(page) > 10:
            break
        InvalidProxy(p)
    return page

def GetScheduleCities(url):
    cities = set()
    page = GetPage(url)
    tree = etree.HTML(page)
    
    nodes = tree.xpath("//a[@href]")
    for node in nodes:
        href = node.get("href")
        if href.startswith("/schedule/"):
            start = href.rfind("/") + 1
            end = href.find(".", start)
            cities.add( href[start: end].lower() )

    return cities

def GetInterScheduleCities(url):
    cities = set()
    page = GetPage(url)
    tree = etree.HTML(page)
    
    nodes = tree.xpath("//*[@class='schedule_detail_list clearfix']//a[@href]")
    for node in nodes:
        href = node.get("href")
        end = href.find("-")
        cities.add( href[:end].lower() )

    return cities

def GetCity(url):
    m = URL_PATTERN.search(url)
    if m != None:
        return m.group(1), m.group(2)
    return "", ""

def GetRoutes(url, city, routes):
    print url
    page = GetPage(url)
    tree = etree.HTML(page)
    
    nodes = tree.xpath("//a[@href]")
    for node in nodes:
        href = node.get("href")
        #if href.startswith("http://flights.ctrip.com/"):
        orig, dest = GetCity(href)
        if len(orig) > 0 and len(dest) > 0 and (orig == city or dest == city):
            print orig, dest
            if orig not in routes:
                routes[orig] = set()
            routes[orig].add(dest)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage: %s outputfile" %sys.argv[0]
        sys.exit()

    routes = {}
    cities =  GetScheduleCities(SCHEDULE_URL)
    #print "\n".join(cities)
    print "GetScheduleCities ", len(cities)
    for city in cities:
    #    GetRoutes(SCHEDULE_URL + city + "..html", city, routes)
    #    GetRoutes(SCHEDULE_URL + "." + city + ".html", city, routes)
        GetRoutes(INTER_SCHEDULE_URL + city.upper() + "-in.html", city, routes)
        GetRoutes(INTER_SCHEDULE_URL + city.upper() + "-out.html", city, routes)

    cities = GetInterScheduleCities(INTER_SCHEDULE_URL)
    for city in cities:
        GetRoutes(INTER_SCHEDULE_URL + city.upper() + "-in.html", city, routes)
        GetRoutes(INTER_SCHEDULE_URL + city.upper() + "-out.html", city, routes)

    ofile = open(sys.argv[1], "w+")
    for k, v in routes.iteritems():
        ofile.write("%s\t%s\n" %(k, "\t".join(v)))
    ofile.close()

