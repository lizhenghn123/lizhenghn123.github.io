#!/bin/bash
	
time=0
pid=0
	
if [ $# -eq 1 ]; then
    time=$1
elif [ $# -eq 2 ]; then
    time=$1
    pid=$2
else
    echo "Usage: $0 seconds [pid]"
    exit 1
fi
	
#echo $time, $pid

if [ $pid -gt 0 ]; then
    perf record -a -g -p $pid -o perf.data &
else
    perf record -a -g -o perf.data &
fi
	
#perf record -a -g -o perf.data &

PID=`ps aux| grep "perf record"| grep -v grep| awk '{print $2}'`
	
if [ -n "$PID" ]; then
	sleep $time
	kill -s INT $PID
fi
	
# wait until perf exite
sleep 1
	
perf script -i perf.data &> perf.unfold
perl stackcollapse-perf.pl perf.unfold &> perf.folded
perl flamegraph.pl perf.folded >perf.svg
	
echo "Output : perf.svg"