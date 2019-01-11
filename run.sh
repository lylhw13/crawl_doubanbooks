#!/bin/bash
PATH=$PATH:/d/Python/Envs/douban
export PATH
for((i=1; i<=10000; i++))
do 
	/d/Python/Envs/douban/Scripts/python.exe main.py
	sleep 15
	cp -r /C/ProgramData/MySQL/"MySQL Server 8.0"/Data/douban/. /I/backup/data/test_$i/
	echo "this is $i time"
	sleep 15
done
