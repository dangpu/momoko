#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2014-02-22
    @author: devin
    @desc:
        实时请求接口
'''
import abc

class RealTimeRequest(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def get_result(self, params):
        '''
            请求结果
        '''
        pass
