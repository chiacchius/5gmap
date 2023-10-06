import zmq
from constant import *
import time

class Srsran_handle:

    def __init__(self):

        self.messagges = []
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.REP)
        self.receiver.bind("ipc:///tmp/my_ipc_endpoint")
        self.msg_complete_container = {}
        #self.receive_msg()
        self.rrc_uplink_messages = []
        self.rrc_downlink_messages = []
        self.nas_uplink_messages = []
        self.nas_downlink_messages = []


    def receive_msg(self):
        
        
        while True:
            #  Wait for next msg from srsran
            data_received = self.receiver.recv()
            self.receiver.send_string("Ack")
            try:
                    message = data_received.decode("utf-8")
                    self.parse_message(message)
            except: continue
            if message == ATTACHED or message == SECURITY_MODE_REJECT  or message == ATTACH_REJECT_13 or message == ATTACH_REJECT_14 or message==ATTACH_REJECT or message==RRC_CONN_REL:
                print("[5GMAP] " + message + "")
                break

            

        self.msg_complete_container["UPLINK_RRC"] = self.rrc_uplink_messages
        self.msg_complete_container["DOWNLINK_RRC"] = self.rrc_downlink_messages
        self.msg_complete_container["UPLINK_NAS"] = self.nas_uplink_messages
        self.msg_complete_container["DOWNLINK_NAS"] = self.nas_downlink_messages
        self.receiver.close()
        self.context.term()
        
        return self.msg_complete_container


    def parse_message(self, message):
        
        if message.startswith("MIB:"):
            self.msg_complete_container["MIB"] = message[4:]

        elif message.startswith("SIB1:"):
            self.msg_complete_container["SIB1"] = message[5:]

        elif message.startswith("SIB2:"):
            self.msg_complete_container["SIB2"] = message[5:]

        elif message.startswith("SIB3:"):
            self.msg_complete_container["SIB3"] = message[5:]

        elif message.startswith("UPLINK_RRC:"):
            self.rrc_uplink_messages.append(message[11:-2])

        elif message.startswith("DOWNLINK_RRC:"):
             self.rrc_downlink_messages.append(message[13:-2])
        
        elif message.startswith("UPLINK_NAS:"):
            self.nas_uplink_messages.append(message[11:-2])

        elif message.startswith("DOWNLINK_NAS:"):
            self.nas_downlink_messages.append(message[13:-2])


