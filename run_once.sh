#!/bin/bash
PATH=$PATH:/d/Python/Envs/douban
export PATH
/d/Python/Envs/douban/Scripts/python.exe main.py
sleep 15
cp -r /C/ProgramData/MySQL/"MySQL Server 8.0"/Data/douban/. /I/backup/data/test_shutdown/
sleep 150
shutdown now
