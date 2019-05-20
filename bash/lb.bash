#!/bin/bash

ipaddr="145.168.0."

read counter < var.txt

counterup=$((counter+1))
counterdown=$((counter - 1))
MIN="2"
MAX="254"
stime="1"
end=$((SECONDS+20))
end2=$((SECONDS+20))
tag=$( tail -n 1 /etc/hosts )


while true
do
	echo "this is counter: $counter"
	tagW=$( tail -n 1 /home/hadoop/hadoop/etc/hadoop/workers)
	cpuperc=$(docker stats worker$counter --no-stream --format "{\"container\":\"{{ .Container }}\",\"cpu\":\"{{ .CPUPerc }}\"}" | jq -r '.cpu')
	cpuperc=${cpuperc%????}
	sleep $stime
	echo $cpuperc > cpu.txt
	read cpupercc < cpu.txt
	echo "CPUPERCCC: $cpupercc from worker$counter"
	if [ "$cpupercc" -lt 1 ] && [ "$counter" != "$MIN" ]; then
		while true;
		do
			echo "end: $end"
			if [ "$SECONDS" -lt $end ]; then
				echo "Worker$counter state is Idle: Shutting down at $end seconds: $SECONDS"
				echo "CPU IS IDLE: $cpupercc"
				sleep $stime
			else
				docker rm -f worker$counter
				ssh-keygen -f "/home/hadoop/.ssh/known_hosts" -R worker$counter
				echo "tagW: $tagW"
				if [[ $tagW == "worker$counter" ]]; then
					sed -i '$ d' /home/hadoop/hadoop/etc/hadoop/workers
					echo "testingggggg: worker$counter"
				elif [[ $tagW == "worker2" ]]; then
					echo "EMINEEEEEEEEE"
				else
					echo "Hadoopconfig: Cannot remove worker2"
				fi
				echo $counterdown > var.txt
				counter=$(($counter - 1))
				end=$((SECONDS+120))
				break
			fi
		done
	elif [ "$cpupercc" -gt 50 ] && [ "$counter" != "$MAX" ]; then
		while true
		do
			echo "end2: $end2"
			if [ "$SECONDS" -lt $end ]; then
				echo "Worker$counter is performing above 50%: adding a new worker..."
				echo "CPU LOAD: $cpupercc"
				sleep $stime
			else
				echo $counterup > var.txt
				counter=$(($counter+1))
				docker run -itd --name worker$counterup --hostname worker$counterup --add-host node-master:172.16.45.151 --network localnet -v /home/hadoop/hadoop/etc/hadoop:/home/hadoop/hadoop/etc/hadoop dabbhadoop
				sshpass -f password.txt ssh-copy-id -i /home/hadoop/.ssh/id_rsa.pub hadoop@worker$counterup
				start-dfs.sh
				end=$((SECONDS+10))
				break
			fi
		done
	else
		echo "Status: idle..."
		sleep $stime
	fi
done
