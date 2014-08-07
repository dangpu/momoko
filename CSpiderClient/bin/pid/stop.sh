#!/bin/bash

CURR_PATH=`cd $(dirname $0);pwd;`
cd $CURR_PATH

if [ $# -ne 1 ]; then
    echo "Usage: stop.sh pid_file"
    exit
fi

PID=`cat $1`

echo "kill "$PID

kill $PID
