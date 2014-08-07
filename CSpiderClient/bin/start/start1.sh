#!/bin/bash

CURR_PATH=`cd $(dirname $0);pwd;`
cd $CURR_PATH

export PYTHONPATH=$PYTHONPATH:../../lib

nohup python ../slave.py ../../conf/conf1.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid1

nohup python ../slave.py ../../conf/conf2.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid2

nohup python ../slave.py ../../conf/conf3.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid3

nohup python ../slave.py ../../conf/conf4.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid4

nohup python ../slave.py ../../conf/conf5.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid5

#nohup python ../slave.py ../../conf/conf6.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid6

#nohup python ../slave.py ../../conf/conf7.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid7

#nohup python ../slave.py ../../conf/conf8.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid8

#nohup python ../slave.py ../../conf/conf9.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid9

#nohup python ../slave.py ../../conf/conf10.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid10
