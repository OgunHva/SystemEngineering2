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

cpuperc=$(docker stats worker$counter --no-stream --format "{\"container\":\"{{ .Container }}\",\"cpu\":\"{{ .CPUPerc }}\"}" | jq -r '.cpu')
cpuperc=${cpuperc%????}


stime="1"
end=$((SECONDS+8))
echo $count
while true 
do
	if [ "$cpuperc" -lt 1 ]; then
		while true
		do
			sleep $stime
			if [ "$SECONDS" -lt $end ]; then
				echo "Worker$counter state is Idle: Shutting down at $end seconds: $SECONDS"
				echo $cpuperc
			else
				docker rm -f worker$counter
				echo $counterdown > var.txt
				counter=$((counter-1))
				echo $counter
				end=$((SECONDS+8))
			fi
		done		
	elif [ "$cpuperc" -gt 50 ]; then
		sleep $stime
		if [ "$SECONDS" -lt 5 ]; then
			docker run -itd --name worker$counterup -v /mnt/hgfs/testFolder:/textfiles dabb
		else
			echo "Worker$counter is performing above 50%: adding a new worker..."
			echo $cpuperc
		fi
	else
		echo "This is unexpected..."
		sleep $stime
	fi
done

