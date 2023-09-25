#!/bin/bash
export UE_VAR=ue
if [ -n "$2" ] && [ -n "$3" ]; then
    sudo -E .././build/srsue/src/srsue "$1" "$2" --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 > ./ue_logger 2>&1
else
    sudo .././build/srsenb/src/srsenb --rf.device_name=zmq --rf.device_args="fail_on_disconnect=true,tx_port=tcp://*:2000,rx_port=tcp://localhost:2001,id=enb,base_srate=23.04e6" > ./enb_logger 2>&1 &
    sleep 3
    sudo ip netns delete ue1
    sudo ip netns add ue1
    sudo -E .././build/srsue/src/srsue "$1" --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1 > ./ue_logger 2>&1
fi

#sudo -E .././build/srsue/src/srsue "$1" --rf.device_name=zmq --rf.device_args="tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,id=ue,base_srate=23.04e6" --gw.netns=ue1

