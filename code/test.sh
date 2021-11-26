for fp in $(seq 0.0 .05 0.9)
do
	screen -dm python3 stop-and-wait.py -r -p 8000 -fs 1472  -plr $fp -rtt 0.004 -t 0.0044 -c 679
	python3 stop-and-wait.py -s -p 8000 -c 10 -t 0.0044 -fs 1472 -ip 127.0.10.1  -plr $fp -rtt 0.004 -c 679 >> sw_time
	pkill screen

done
