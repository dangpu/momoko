#!/usr/bin/env python
#coding=UTF8
'''
    @author: devin
    @time: 2014-02-22
    @desc:
        proxy 接口
'''
import abc

class Proxy(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def get_proxy(self, params):
        '''
            获得一个代理地址
        '''
        pass
    
    @abc.abstractmethod
    def update_proxy(self, params):
        '''
            更新代理
        '''
        pass
    
    def add_proxy(self, params):
        '''
            添加代理
        '''
        pass
    
    def del_proxy(self, params):
        '''
            删除代理
        '''
        pass
    
    @abc.abstractmethod
    def proxy_status(self, params):
        '''
            返回代理的状态信息
        '''
        pass
