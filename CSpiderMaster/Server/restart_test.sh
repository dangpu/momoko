#!/bin/bash

killall -9 lt-ichat_server_test
sleep 1
ulimit -c unlimited
nohup ./ichat_server_test ../conf/server_test.cfg 2>&1 1>>log.test &

