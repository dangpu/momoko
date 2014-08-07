#coding:utf-8
#导入模块##
import urllib
import urllib2
import mechanize
import cookielib
import logging
import sys


user_agent_list = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36']


class MechanizeCrawler(object):
    '''
    A basic crawl tool using mechanize.
    automatic configuration, but only support get request, now.
    '''

    # init, referer, headers and proxy can be set here
    def __init__(self, referer = '', headers = {}, p = ''):
        self.debug = False

        self.br = mechanize.Browser()
        
        self.cj = cookielib.LWPCookieJar()
        self.br.set_cookiejar(self.cj)
        
        self.br.set_handle_equiv(True)
        self.br.set_handle_gzip(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)

        self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0')]

        #if self.debug:
        self.br.set_debug_http(True)
        self.br.set_debug_redirects(True)
        self.br.set_debug_responses(True)

        # add referer
        if len(referer) > 0 and referer != 'None' and referer != None and referer != 'NULL':
            self.br.addheaders += [('Referer', url), ]

        # add headers, referer can also be put here
        for keys in headers.keys():
            self.br.addheaders += [(key, headers[key]), ]

        # set proxy
        if len(p) > 0 and p != 'None' and p != None and p != 'NULL':
            self.br.set_proxies({'http': p})

    # set debug
    def set_debug(self, flag = False):
        self.debug = flag

    # get
    def get(self, url_base, paras = {}, html_flag = False):
        url = url_base
        
        for key in paras:
            url += key + '=' + paras[key] + '&'

        if len(url) > 0 and len(paras) > 0:
            url = url[0:-1]

        html = ''
        try:
            print url
            resp = self.br.open(url)
            if html_flag:
                html = resp.get_data()
                #html = self.br.response().read()
        except Exception, e:
            if self.debug:
                print e

        return html

    # post: which not be implemented
    def post(self, url_base, paras = {}, html_flag = False):
        pass

    # set referer individually
    def add_referer(self, url):
        self.br.addheaders += [('Referer', url), ]

    # set header individually
    def add_header(self, headers = {}):
        for key in headers:
            self.br.addheaders += [(key, headers[key]), ]

    # set proxy individually
    def set_proxy(self, p):
        self.br.set_proxies({'http': p})




class UrllibCrawler(object):
    '''
    A basic crawl tool using urllib and urllib2
    '''

    def __init__(self, referer = '', headers = {}, p = ''):
        self.debug = False
        self.cookie_processor = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())

        if self.debug:
            self.httpHandler = urllib2.HTTPHandler(debuglevel=1)
            self.httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
        else:
            self.httpHandler = urllib2.HTTPHandler(debuglevel=1)
            self.httpsHandler = urllib2.HTTPSHandler(debuglevel=1)


        if len(p) > 0 and p != 'None' and p != None and p != 'NULL':
            self.proxy_handle = urllib2.ProxyHandler({'http': p})
        else:
            self.proxy_handle = urllib2.ProxyHandler({})

        self.opener = urllib2.build_opener(self.proxy_handle, self.cookie_processor, self.httpHandler, self.httpsHandler)

    def set_debug(self, flag = False):
        self.debug = flag

    def get(self, url_base, paras = {}, html_flag = False):
        url = url_base
        
        for key in paras:
            url += key + '=' + paras[key] + '&'

        if len(url) > 0 and len(paras) > 0:
            url = url[0:-1]

        html = ''
        try:
            print url
            resp = self.opener.open(url)
            if html_flag:
                html = resp.read()
        except Exception, e:
            if self.debug:
                print e
                pass

        return html


    def post(self, url, paras = {}, html_flag = False):
        html = ''
        req = urllib2.Request(url)  
        datas = urllib.urlencode(paras)  
        try:
            print url
            resp = self.opener.open(req, datas)
            if html_flag:
                html = resp.read()
        except Exception, e:
            if self.debug:
                print e
                pass

        return html


    def add_referer(self, url):
        pass

    def add_header(self, headers = {}):
        pass

    def set_proxy(self, p):
        pass




if __name__ == '__main__':
    mc = MechanizeCrawler()
    
    
    #hd = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116'}
    #uc = UrllibCrawler(headers = hd)

    # test MechanizeCrawler
    '''
    print 'test MechanizeCrawler'
    url1 = 'http://www.ufeifan.com/s?flightType=2&tickType=ADT&personNum=1&childNum=0&directFlightsOnly=2&originCode=BJS_1&desinationCode=PAR_1&originDate=2014-06-25'
    url2 = 'http://www.ufeifan.com/s?national=false&flightType=2&tickType=ADT&personNum=1&originCode=BJS_1&desinationCode=PAR_1&originDate=2014-06-25&childNum=0&directFlightsOnly=2&lang=ZH&currency=CNY&country=CN&syn=true'
    url3 = 'http://www.ufeifan.com/s/keep?national=false&flightType=2&tickType=ADT&personNum=1&originCode=BJS_1&desinationCode=PAR_1&originDate=2014-06-25&childNum=0&directFlightsOnly=2&lang=ZH&currency=CNY&country=CN'
    url4 = 'http://www.ufeifan.com/s?national=false&flightType=2&tickType=ADT&personNum=1&originCode=BJS_1&desinationCode=PAR_1&originDate=2014-06-25&childNum=0&directFlightsOnly=2&lang=ZH&currency=CNY&country=CN&syn=true&flush=0.15403628842241823'

    mc = MechanizeCrawler()
    mc.set_debug(flag = True)
    mc.get(url1)
    mc.get(url2)
    mc.get(url3)
    html = mc.get(url4, html_flag = True)
    print len(html)
    import time
    time.sleep(5)
    print html
    print
    print '******************************************************************************************'
    print
    '''
    mc.set_debug(flag = True)
    mc.set_proxy(p = '183.91.27.133:8080')
    mc.get('http://www.csair.com/cn/index.shtml')
    #url1 = 'http://b2c.csair.com/B2C40/modules/booking/international/flightSelectDirect_inter.jsp'
    url2 = 'http://b2c.csair.com/B2C40/detail-PEKPAR-20140627-1-0-0-0-1-0-1-0-1-0.g2c'
    #mc.get(url1)
    html = mc.post(url2)
    print html
    print
    
    '''
    # test UrllibCrawler.get
    hd = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116'}
    uc = UrllibCrawler(headers = hd)
    uc.set_debug(flag = True)
    uc.get(url1)
    uc.get(url2)
    uc.get(url3)
    html = uc.get(url4, html_flag = True)
    print len(html)
    print
    print '******************************************************************************************'
    print
    
    # test UrllibCrawler.post
    # 东方航空
    print '东方航空'
    url1 = 'http://easternmiles.ceair.com/flight/sha-cdg-140626_CNY.html'
    url2 = 'http://easternmiles.ceair.com/booking/flight-search!doFlightSearch.shtml?rand=0.3444413504329352'
    uc.get(url1)
    datas = {'searchCond':'{"segmentList":[{"deptCdTxt":"上海","deptCd":"SHA#","deptNation":"CN","deptRegion":"CN","deptCityCode":"SHA","arrCd":"CDG#","arrCdTxt":"巴黎","arrNation":"FR","arrRegion":"EU","arrCityCode":"PAR","deptDt":"2014-06-26"}],"tripType":"OW","adtCount":1,"chdCount":0,"infCount":0,"currency":"CNY","sortType":"t"}'}
    html = uc.post(url2, datas, html_flag = True)
    print html
    print
    
    # 南方航空
    print '南方航空'
    url1 = 'http://b2c.csair.com/B2C40/modules/booking/international/flightSelectDirect_inter.jsp'
    url2 = 'http://b2c.csair.com/B2C40/detail-PEKPAR-20140627-1-0-0-0-1-0-1-0-1-0.g2c'
    uc.get(url1)
    html = uc.post(url2)
    print html
    print

    # 海南航空
    print '海南航空'
    url1 = 'http://et.hnair.com/'
    uc.get(url1)
    url2 = 'http://et.hnair.com/huet/bc10waiting.do'
    datas = {'preUrl':'www.hnair.com', 'dstCity':'MIL', 'returnDate':'2014-06-14', 'tripType':'ONEWAY', 'adultNum':'1', 'bookSeatClass':'E', 'childNum':'0', 'takeoffDate':'2014-06-25', 'orgCity':'PEK'}
    html = uc.post(url2, datas, html_flag = True)
    print html

    url3 = 'http://et.hnair.com/huet/bc10_av.do'
    datas = {'preUrl':'et.hnair.com', 'queryPassengerType':'0', 'dstCity':'MIL', 'returnDate':'2014-06-14', 'iscalendar':'true', 'tripType':'ONEWAY', 'adultNum':'1', 'bookSeatClass':'E', 'type':'on', 'childNum':'0', 'takeoffDate':'2014-06-25', 'orgCity':'PEK'}
    html = uc.post(url3, datas, html_flag = True)


    mc.get('http://et.airchina.com.cn/cn/index.shtml')
    url1 = 'http://et.airchina.com.cn/InternetBooking/AirLowFareSearchExternal.do?&tripType=OW&searchType=FARE&flexibleSearch=false&directFlightsOnly=false&fareOptions=1.FAR.X&outboundOption.originLocationCode=PEK&outboundOption.destinationLocationCode=FRA&outboundOption.departureDay=26&outboundOption.departureMonth=06&outboundOption.departureYear=2014&outboundOption.departureTime=NA&guestTypes[0].type=ADT&guestTypes[0].amount=1&guestTypes[1].type=CNN&guestTypes[1].amount=0&pos=AIRCHINA_CN&lang=zh_CN&guestTypes[2].type=INF&guestTypes[2].amount=0'
    html = mc.get(url1)
    print html

    print '******************************************************************************************
    url2 = 'http://et.airchina.com.cn/InternetBooking/AirFareFamiliesForward.do'
    html = mc.get(url2, html_flag = True)

    print html
    print
    '''
