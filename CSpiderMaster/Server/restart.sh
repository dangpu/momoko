#!/bin/bash

killall -9 lt-HttpServer
sleep 1
ulimit -c unlimited
nohup ./HttpServer ../conf/server.cfg2 2>&1 1>> log &
nohup python ../master/python/update.py 1> ../master/python/log 2>&1 &
#./LYRoute ../conf/server.cfg 

