#!/bin/bash
while [ 1 ]
do
	if pgrep -x -f "gqrx-hamlib.py"
	then
		echo Already running
	else
		echo Re-running python script
		sudo pkill rigctld
		sudo pkill python3
		sudo pkill python
		# Find first available USB
		PORT=$(ls /dev/ttyUSB* 2>/dev/null | head -n 1)
		/home/telewizoor/Project/hamlib-4.6.2/tests/rigctld -m 1046 -r "$PORT" -s 38400 &
		sleep 3
		/usr/bin/python3 /home/telewizoor/Project/gqrx-hamlib-piSdr/gqrx-hamlib.py > /home/telewizoor/Desktop/logPythonHamlib.txt 2>&1
	fi
	sleep 2
done
