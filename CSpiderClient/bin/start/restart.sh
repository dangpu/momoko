#!/bin/bash

CURR_PATH=`cd $(dirname $0);pwd;`
cd $CURR_PATH

sh kill.sh
sleep 60
sh allstart.sh
#sh temp_start.sh
