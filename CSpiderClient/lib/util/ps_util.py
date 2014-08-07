#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2014-03-22
    @author: devin
    @desc:
        获取系统的相关信息
        主要包括CPU使用率、硬盘和网络IO的速度
'''

import psutil
import time

interval = 3

def bytes2human(n):  
    """ 
    >>> bytes2human(10000) 
    '9.8 K' 
    >>> bytes2human(100001221) 
    '95.4 M' 
    """  
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')  
    prefix = {}  
    for i, s in enumerate(symbols):  
        prefix[s] = 1 << (i+1)*10  
    for s in reversed(symbols):  
        if n >= prefix[s]:  
            value = float(n) / prefix[s]  
            return '%.2f %s' % (value, s)  
    return '%.2f B' % (n)  

def get_cpu_state():
    return {"cpu_percent": psutil.cpu_percent(interval)}

def get_mem_state():
    phymem = psutil.virtual_memory()  
    return {"used_mem_percent": phymem.percent, "free_mem": bytes2human(phymem.free)}  


def get_net_state():
    tot_before = psutil.net_io_counters()
    # sleep some time  
    time.sleep(interval)  
    tot_after = psutil.net_io_counters()  
    
    return {"net_send": bytes2human((tot_after.bytes_sent - tot_before.bytes_sent)/ interval), 
            "net_recv": bytes2human((tot_after.bytes_recv - tot_before.bytes_recv)/ interval)}


def get_disk_state():
    tot_before = psutil.disk_io_counters()
    # sleep some time  
    time.sleep(interval)  
    tot_after = psutil.disk_io_counters() 
    return {"disk_read": bytes2human((tot_after.read_bytes - tot_before.read_bytes)/ interval), 
            "disk_write": bytes2human((tot_after.write_bytes - tot_before.write_bytes)/ interval)}

def get_system_info():
    info = get_cpu_state()
    info = dict(info, **get_mem_state())
    info = dict(info, **get_net_state())
    info = dict(info, **get_disk_state())
        
    return info

if __name__ == "__main__":
    print get_system_info()
