#!/bin/bash
while [ 1 ]
do
	if pgrep -x -f "gqrx-hamlib-fldigi.py"
	then
		echo Already running
	else
		echo Re-running python script
		sudo pkill rigctld
		sudo pkill python3
		sudo pkill python
		/home/telewizoor/Project/hamlib-4.6.2/tests/rigctld -m 1046 -r /dev/ttyUSB0 -s 38400 &
		sleep 5
		/usr/bin/python3 /home/telewizoor/Project/gqrx-hamlib/gqrx-hamlib-fldigi.py > /home/telewizoor/Desktop/logPythonHamlib.txt 2>&1
	fi
	sleep 1
done

#sudo pkill rigctld
#sudo pkill python3
#sudo pkill python
#/home/telewizoor/Project/hamlib-4.6.2/tests/rigctld -m 1046 -r /dev/ttyUSB0 -s 38400 &
#sleep 5
#/usr/bin/python3 /home/telewizoor/Project/gqrx-hamlib/gqrx-hamlib-fldigi.py > /home/telewizoor/Desktop/logPythonHamlib.txt 2>&1

#if ps aux | grep | '[/]usr/bin/gqrx'
#then
#	echo Already running
#else
#	rigctld -m 1046 -r /dev/ttyUSB0 -s 9600 &
#	python /home/telewizoor/Project/gqrx-hamlib/gqrx-hamlib-fldigi.py > log.txt
#fi
