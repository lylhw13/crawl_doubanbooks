#!/bin/bash
PATH=$PATH:/d/Python/Envs/douban
export PATH
for((i=1; i<3; i++))
do 
	/d/Python/Envs/douban/Scripts/python.exe main.py
	sleep 30
	echo "this is $i time"
done
read
