#!/bin/sh   

keys=`(ps -ef |grep "slave" |grep -v "grep") | awk '{print $2}'`

for key in ${keys[*]}
do
    kill -9 $key
done
