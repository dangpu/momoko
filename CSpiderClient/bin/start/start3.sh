#!/bin/bash

CURR_PATH=`cd $(dirname $0);pwd;`
cd $CURR_PATH

export PYTHONPATH=$PYTHONPATH:../../lib

nohup python ../slave.py ../../conf/conf20.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid20

nohup python ../slave.py ../../conf/conf21.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid21

nohup python ../slave.py ../../conf/conf22.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid22

nohup python ../slave.py ../../conf/conf23.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid23

nohup python ../slave.py ../../conf/conf24.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid24

nohup python ../slave.py ../../conf/conf25.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid25

nohup python ../slave.py ../../conf/conf26.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid26

nohup python ../slave.py ../../conf/conf27.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid27

nohup python ../slave.py ../../conf/conf28.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid28

nohup python ../slave.py ../../conf/conf29.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid29
