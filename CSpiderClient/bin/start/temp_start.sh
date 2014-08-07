#!/bin/bash

CURR_PATH=`cd $(dirname $0);pwd;`
cd $CURR_PATH

export PYTHONPATH=$PYTHONPATH:../../lib

nohup python ../slave.py ../../conf/confall.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid1

