#!/bin/bash

#ip address of the workers
ipaddr="172.17.0."

#reading the var.txt file into the variable counter
read counter < var.txt

counterup=$((counter+1))
counterdown=$((counter-1))

#min and max variables
MIN="1"
MAX="255"

cpuperc=$(docker stats worker$counterup --no-stream --format "{\"container\":\"{{ .Container }}\",\"cpu\":\"{{ .CPUPerc }}\"}" | jq -r '.cpu')
cpuperc=${cpuperc%????}
#echo $cpuperc

stime="3"
end=$((SECONDS+20))
echo $count
while true do
	if [ "$cpuperc" -lt "1" ] && [ $SECONDS -lt $end ]; then
		sleep $stime
		echo "Worker state is Idle: Shutting down Worker$counter"
		echo $counterdown > var.txt
		echo $ipaddr$counter
		echo $cpuperc
		docker rm -f worker$counter			
	elif [ "$cpuperc" -gt "50" ]; then
		sleep $stime
		echo "This worker is performing above 50%"
		echo "adding a new worker"
		echo $cpuperc
	else
		echo "This is unexpected..."
		sleep $stime
	fi
done
