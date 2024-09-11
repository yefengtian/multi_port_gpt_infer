#!/bin/bash

nohup python multi_sh_kill_script.py "$@" > nohup.out 2>&1 &
echo $! > script.pid
echo "Script started with PID $(cat script.pid)"