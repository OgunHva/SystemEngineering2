#!/bin/bash

#ip address of the workers
ipaddr="145.168.0."

#reading the var.txt file into the variable counter
read counter < var.txt

counterup=$((counter+1))
counterdown=$((counter-1))

#min and max variables
MIN="1"
MAX="254"
tag=$( tail -n 1 /etc/hosts )
tagW=$( tail -n 1 /home/hadoop/hadoop/etc/hadoop/workers)

echo "add or remove container? write (add) or (remove)"

#expecting user input
read count

#if input is "add" and the integer is not higher than 255 
#then echo the results and send the int back to the var.txt
if [ "$count" == "add" ] && [ "$counter" != "$MAX" ]; then
	echo "IP Address: $ipaddr$counterup"
	echo $counterup > var.txt
	#docker run -itd --name worker$counterup -v /mnt/hgfs/testFolder:/textfiles dabb
	docker run -itd --name worker$counterup --network localnet progrium/stress --cpu 2 --io 1 --vm 2 --vm-bytes 128M
elif [ "$count" == "idle" ] && [ "$counter" != "$MAX" ]; then
	if [[ $tag == *"worker"* ]]; then
		echo -e "$ipaddr$counterup \t worker$counterup" >> /etc/hosts
		echo "worker$counterup" >> /home/hadoop/hadoop/etc/hadoop/workers
	else
		echo "Do nothing"
	fi
	echo "IP Address: $ipaddr$counterup"
	echo $counterup > var.txt
	docker run -itd --name worker$counterup --network localnet -v /mnt/hgfs/testFolder:/textfiles dabbhadoop	
elif [ "$count" == "remove" ] && [ "$counter" != "$MIN" ]; then
	docker rm -f worker$counter
	echo "IP Address: $ipaddr$counter"
	echo $counterdown > var.txt
	if [[ $tag == *"worker"* ]]; then
		echo -e "Removed line in Hosts file: ipaddr$counter \t worker$counter"
		sed -i '$ d' /etc/hosts
	else
		echo "Do nothing"
	fi
	if [[ $tagW != "worker1" ]]; then
		sed -i '$ d' /home/hadoop/hadoop/etc/hadoop/workers
	else
		echo "Hadoopconfig: Cannot remove worker1"
	fi
else
	echo "the IP range must be between 1 and 255"
fi
