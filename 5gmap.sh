#!/bin/bash
#echo "Starting UE..."
rm -rf my_pipe
sudo pkill srsue
sudo pkill srsenb
sleep 1
sudo python3 runner.py
