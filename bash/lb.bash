#!/bin/bash

ipaddr="145.168.0."

read counter < var.txt

counterup=$((counter+1))
counterdown=$((counter - 1))
MIN="1"
MAX="254"
stime="1"
end=$((SECONDS+8))
end2=$((SECONDS+5))

while true
do
	echo "this is counter: $counter"
	cpuperc=$(docker stats worker$counter --no-stream --format "{\"container\":\"{{ .Container }}\",\"cpu\":\"{{ .CPUPerc }}\"}" | jq -r '.cpu')
	cpuperc=${cpuperc%????}
	sleep $stime
	echo $cpuperc > cpu.txt
	read cpupercc < cpu.txt
	echo "CPUPERCCC: $cpupercc from worker$counter"

	if [ "$cpupercc" -lt 1 ] && [ "$counter" != "$MIN" ]; then
		while true;
		do
			if [ "$SECONDS" -lt $end ]; then
				echo "Worker$counter state is Idle: Shutting down at $end seconds: $SECONDS"
				echo "CPU IS IDLE: $cpupercc"
				sleep $stime
			else
				docker rm -f worker$counter
				echo $counterdown > var.txt
				counter=$(($counter - 1))
				end=$((SECONDS+10))
				break
			fi
		done
	elif [ "$cpupercc" -gt 50 ] && [ "$counter" != "$MAX" ]; then
		while true
		do
			if [ "$SECONDS" -lt $end2 ]; then
				echo "Worker$counter is performing above 50%: adding a new worker..."
				echo "CPU LOAD: $cpupercc"
				sleep $stime
			else
				echo $counterup > var.txt
				counter=$(($counter+1))
				docker run -itd --name worker$counter -v /mnt/hgfs/testFolder:/textfiles dabb
				end2=$((SECONDS+10))
				break
			fi
		done
	elif [ "$counter" == "$MIN" ]; then
		echo $counterup > var.txt
		counter=$(($counter+1))
		docker run -itd --name worker$counter -v /mnt/hgfs/testFolder:/textfiles dabb
	else
		echo "This is unexpected..."
		sleep $stime
	fi
done
