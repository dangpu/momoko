#!/bin/bash

CURR_PATH=`cd $(dirname $0);pwd;`
cd $CURR_PATH

export PYTHONPATH=$PYTHONPATH:../../lib

nohup python ../slave.py ../../conf/conf30.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid30

nohup python ../slave.py ../../conf/conf31.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid31

nohup python ../slave.py ../../conf/conf32.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid32

nohup python ../slave.py ../../conf/conf33.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid33

nohup python ../slave.py ../../conf/conf34.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid34

nohup python ../slave.py ../../conf/conf35.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid35

nohup python ../slave.py ../../conf/conf36.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid36

nohup python ../slave.py ../../conf/conf37.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid37

nohup python ../slave.py ../../conf/conf38.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid38

nohup python ../slave.py ../../conf/conf39.ini 1>../../logs/log2 2>../../logs/err.log2 &
echo $! > ../pid/pid39
