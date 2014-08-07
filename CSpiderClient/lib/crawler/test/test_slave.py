#!/usr/bin/env python
#coding=UTF8
'''
    @author: devin
    @time: 2014-02-23
    @desc:
        
'''
from crawler.controller.slave import Slave
from crawler.worker import Workers

def test():
    print "test"
    import time
    time.sleep(1)

def request(params):
    print params
    test()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print "Usage: %s host port master_host" % sys.argv[0]
        sys.exit()
    
    host, port = sys.argv[1], int(sys.argv[2])
    master_host = sys.argv[3]
    
    workers = Workers(None, test, 1)
    slave = Slave(host, port, master_host, workers)
    
    slave.register("/request", request)
    
    slave.run()

