#!/usr/bin/env python
#coding=UTF-8
'''
    @author: devin
    @desc: 抓取航班数据
'''

import Crawler
from common import *
from storage import *

PLANE_URL = "http://webresource.c-ctrip.com/code/js/resource/jmpinfo_tuna/CraftType_gb2312.js"

def GetPage(url):
    while True:
        p = GetProxy()
        page = Crawler.CrawlSinglePage(url, proxy=p)
        if len(page) > 10:
            break
        InvalidProxy(p)
    return page

def GetPlanes(url):
    planes = []
    page = GetPage(url)
    page = page.decode("GBK").encode("UTF-8")
    start = page.find('"') + 1
    end = page.find('"', start)

    strs = page[start:end].split("@")
    for s in strs:
        temp = s.split("|")
        if len(temp) < 5:
            continue
        plane = Plane()
        plane.plane_no = temp[0]
        plane.name = temp[1]
        plane.type = temp[2]
        plane.min_seats = temp[3]
        plane.max_seats = temp[4]
        
        planes.append(plane)
        
    return planes


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 1:
        print "Usage: %s" %sys.argv[0]
        sys.exit()

    planes = GetPlanes(PLANE_URL)
    for plane in planes:
        print plane
        AddPlane(plane)
