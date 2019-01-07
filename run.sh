#!/bin/bash
PATH=$PATH:/d/Python/Envs/douban
export PATH
for((i=1; i<5; i++))
do 
	/d/Python/Envs/douban/Scripts/python.exe main.py
	read
	echo "this is $i time"
done
read
