#!/bin/bash
sudo ip netns delete ue1
sudo ip netns add ue1
export UE_VAR=ue
sudo -E .././build/srsue/src/srsue --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 > ./ue_logger 2>&1
