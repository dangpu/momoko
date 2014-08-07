#!/usr/bin/python
#--encoding:utf-8--
import time
import sys

def _ERROR(module_name, error_list):
    error_str = '[' + str(time.strftime('%Y-%m-%d %X', time.localtime())) + '] [ERROR in ' + module_name + ']'
    for i in xrange(0, len(error_list)):
        if type(error_list[i]).__name__ != 'str':
            _ERROR('_ERROR()', ['type error', str(i+1)+'th item\'s type = ' + type(error_list[i]).__name__])
            return
        error_str += ' [' + error_list[i] + ']'
    print error_str
    sys.stdout.flush()


def _INFO(module_name, info_list):
    info_str = '[' + str(time.strftime('%Y-%m-%d %X', time.localtime())) + '] [INFO in ' + module_name + ']'
    for i in xrange(0, len(info_list)):
        if type(info_list[i]).__name__ != 'str':
            _ERROR('_ERROR()', ['type error', str(i+1)+'th item\'s type = ' + type(info_list[i]).__name__])
            return
        info_str += ' [' + info_list[i] + ']'
    print info_str
    sys.stdout.flush()


if __name__=='__main__':
    _ERROR('server_log', ['error1', 'error2'])
    _ERROR('server_log', ['error1', 1])
    _INFO('server_log', ['error1', 'error2'])
    _INFO('server_log', ['error1', 1])
