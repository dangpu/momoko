#!/bin/bash

CURR_PATH=`cd $(dirname $0);pwd;`
cd $CURR_PATH

export PYTHONPATH=$PYTHONPATH:../../lib

nohup python ../slave.py ../../conf/conf11.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid11

nohup python ../slave.py ../../conf/conf12.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid12

nohup python ../slave.py ../../conf/conf13.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid13

nohup python ../slave.py ../../conf/conf14.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid14

nohup python ../slave.py ../../conf/conf15.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid15

nohup python ../slave.py ../../conf/conf16.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid16

nohup python ../slave.py ../../conf/conf17.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid17

nohup python ../slave.py ../../conf/conf18.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid18

nohup python ../slave.py ../../conf/conf19.ini 1>../../logs/log 2>../../logs/err.log &
echo $! > ../pid/pid19

