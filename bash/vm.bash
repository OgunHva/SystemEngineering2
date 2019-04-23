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

echo "add or remove container? write (add) or (remove)"

#expecting user input
read count

#if input is "add" and the integer is not higher than 255 
#then echo the results and send the int back to the var.txt
if [ "$count" == "add" ] && [ "$counter" != "$MAX" ]; then
	echo $ipaddr$counterup
	echo $counterup > var.txt
	#docker run -itd --name worker$counterup -v /mnt/hgfs/testFolder:/textfiles dabb
	docker run -itd --name worker$counterup progrium/stress --cpu 2 --io 1 --vm 2 --vm-bytes 128M
elif [ "$count" == "idle" ] && [ "$counter" != "$MAX" ]; then
	echo $ipaddr$counterup
	echo $counterup > var.txt
	docker run -itd --name worker$counterup -v /mnt/hgfs/testFolder:/textfiles dabb	
elif [ "$count" == "remove" ] && [ "$counter" != "$MIN" ]; then
	echo $ipaddr$counter
	echo $counterdown > var.txt
    docker rm -f worker$counter
else
	echo "the IP range must be between 1 and 255"
fi
