from binascii import unhexlify, hexlify
from pycrate_mobile.NAS import *
from pycrate_asn1dir import RRCLTE
import binascii
import ast
from constant import *
from json_handler import *


class Communication:

    def __init__(self, ciph_algo, integ_algo):

        self.mib = ""
        self.sib1 = ""
        self.sib2 = ""
        self.sib3 = ""
        self.rrc_ul_msg = []
        self.rrc_dl_msg = [] 
        self.nas_ul_msg = [] 
        self.nas_dl_msg = [] 
        self.ciph_algo = ciph_algo
        self.integ_algo = integ_algo
        

    def add_rrc_msg(self, msg, is_uplink):

        if is_uplink:
            self.rrc_ul_msg.append(msg)
            
        else:
            self.rrc_dl_msg.append(msg)


    def add_nas_msg(self, msg, is_uplink):

        if is_uplink:
            self.nas_ul_msg.append(msg)
            # if get_key_value(msg.get_pdu(), "EMMAttachRequest"):
            #     print(msg.get_pdu())
            
        else:
            self.nas_dl_msg.append(msg)

            # if get_key_value(msg.get_pdu(), "EMMSecurityModeCommand"):
            #     print(msg.get_pdu())

    def set_mib_msg(self, msg):
        self.mib = msg

    def set_sib1_msg(self, msg):
        self.sib1 = msg

    def set_sib2_msg(self, msg):
        self.sib2 = msg

    def set_sib3_msg(self, msg):
        self.sib3 = msg

    def get_mib_msg(self):
        return self.mib
    
    def get_sib1_msg(self):
        return self.sib1
    
    def get_sib2_msg(self):
        return self.sib2
    
    def get_sib3_msg(self):
        return self.sib3

    def get_ciph_algo(self):
        return self.ciph_algo

    def get_integ_algo(self):
        return self.integ_algo
 

    def printer(self):
        print(self.mib.get_pdu())
        print(self.sib1.get_pdu())
        print(self.sib2.get_pdu())
        print(self.sib3.get_pdu())

        for msg in self.rrc_dl_msg:
            print(msg.get_pdu())

        for msg in self.nas_dl_msg:
            print(msg.get_pdu())

        for msg in self.rrc_ul_msg:
            print(msg.get_pdu())

        for msg in self.nas_ul_msg:
            print(msg.get_pdu())


    def find_enb_sec_algo(self):
        
        ciph_algo = None
        integ_algo = None
        for rrc_msg in self.rrc_dl_msg:
            
            if  get_key_value(rrc_msg.get_pdu(), "securityModeCommand")!= None:
                
                #print(rrc_msg.get_pdu())
                ciph_algo = get_key_value(rrc_msg.get_pdu(), "cipheringAlgorithm")
                integ_algo = get_key_value(rrc_msg.get_pdu(), "integrityProtAlgorithm")

        return ciph_algo, integ_algo
    

    def find_epc_sec_algo(self):

        ciph_algo = None
        integ_algo = None
        for nas_msg in self.nas_dl_msg:
            
            if  get_key_value(nas_msg.get_pdu(), "EMMSecurityModeCommand")!= None:

                ciph_algo = get_key_value(nas_msg.get_pdu(), "CiphAlgo")
                integ_algo = get_key_value(nas_msg.get_pdu(), "IntegAlgo")

        ciph_algo = "eea" + str(ciph_algo)
        integ_algo = "eia" + str(integ_algo)
        return ciph_algo, integ_algo


