#!/bin/bash

killall -9 lt-HttpServer
sleep 1
ulimit -c unlimited
nohup ./HttpServer ../conf/validate_server.cfg 2>&1 1>> log &
#./LYRoute ../conf/server.cfg 

