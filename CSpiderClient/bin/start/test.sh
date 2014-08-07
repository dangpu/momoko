#!/bin/bash

CURR_PATH=`cd $(dirname $0);pwd;`
cd $CURR_PATH

export PYTHONPATH=$PYTHONPATH:../../lib

nohup python ../slave.py ../../conf/conf9.ini 1>../../logs/slave_test.log 2>../../logs/slave_test_err.log &
echo $! > ../pid/pid9

