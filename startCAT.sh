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
		/home/telewizoor/Project/hamlib-4.6.2/tests/rigctld -m 1046 -r /dev/ttyUSB0 -s 38400 &
		# dummy rig for log4om2 one way communication
		/home/telewizoor/Project/hamlib-4.6.2/tests/rigctld -t 4534 &
		sleep 5
		/usr/bin/python3 /home/telewizoor/Project/gqrx-hamlib-piSdr/gqrx-hamlib.py > /home/telewizoor/Desktop/logPythonHamlib.txt 2>&1
	fi
	sleep 1
done
