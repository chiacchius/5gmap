#!/bin/bash
#echo "Starting UE..."
rm -rf my_pipe
pkill srsue
pkill srsenb
sleep 1
sudo python3 runner.py
