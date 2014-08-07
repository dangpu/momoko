#!/usr/bin/env python
#coding=UTF8

'''
    修改conf.ini文件
'''

def add_parser(filename, parser):
    '''
        在parser中加入一个parser使之可以爬取对应的workload，前提是下面的parser信息列表中存在该parser
        parser@line10
    '''

    rfile = open(filename,'r')
    
    lines = []
    for line in rfile:
        lines.append(line)
    
    rfile.close()

    lines[9] += lines[9] + ' ' + parser

    wfile = open(filename,'w')

    for line in lines:
        wfile.write(line)

    wfile.close()

def add_source(filename, source):
    '''
        在source中加入一个source使之可以爬取对应的workload，前提是下面parser信息列表中存在该parser
        source@line11
    '''

    rfile = open(filename,'r')


    lines = []
    for line in rfile:
        lines.append(line)

    rfile.close()

    lines[10] += lines[10] + ' ' + parser

    wfile = open(filename,'w')

    for line in lines:
        wfile.write(line)

    wfile.close()

def add_parser_info(filename, parser_info):
    '''
        新加一个parser详细信息,加在文件结尾
    '''

    afile = open(filename,'a')

    for item in parser_info:
        afile.write('\n' + item)

    wfile.close()

if __name__ == "__main__":

    import os
    import sys

    if len(sys.argv) < 5:
        print 'Usage: %s parser source [parser_info] conf_dir'%sys.argv[0]
        sys.exit(-1)

    parser = sys.argv[1]
    source = sys.argv[2]
    parser_info = sys.argv[3]
    dir = sys.argv[4]

    #dir = os.getcwd()

    filelist = os.listdir(dir)

    for file in filelist:
        print file




