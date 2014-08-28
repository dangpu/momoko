#!/bin/bash

CURR_PATH=`cd $(dirname $0);pwd;`
cd $CURR_PATH

killall -9 lt-HttpServer
sleep 1
ulimit -c unlimited
nohup ./HttpServer ../conf/server.cfg2 1> log 2>&1 &
#nohup python ../master/python/update.py 1> ../master/python/log 2>&1 &
#./LYRoute ../conf/server.cfg 

