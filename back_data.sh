#!/bin/bash
PATH=$PATH:/d/Python/Envs/douban
export PATH
for((i=1; i<=10000; i++))
do 
	sleep 5000
	cp -r /C/ProgramData/MySQL/"MySQL Server 8.0"/Data/douban/. /I/backup/data/test_$i/
	echo "this is $i time"
done
