#!/usr/bin/env python
#coding=UTF8

def temp(filename, thread_num):

    rfile = open(filename,'r')

    lines = []
    for line in rfile:
        lines.append(line)

    lines[12] = 'thread_num = ' + thread_num + '\n'

    wfile = open(filename,'w')
    for line in lines:
        wfile.write(line)

    wfile.close()

if __name__ == "__main__":

    import os
    import sys

    if len(sys.argv) < 3:
        print 'Usage: %s file_path thread_num'%sys.argv[0]
        sys.exit(-1)

    dir = sys.argv[1]
    thread_num = sys.argv[2]
    
    filelist = os.listdir(dir)
    for file in filelist:
        print file
        temp(dir+file, thread_num)
