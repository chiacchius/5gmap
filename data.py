from binascii import unhexlify, hexlify
from pycrate_mobile.NAS import *
from pycrate_asn1dir import RRCLTE
from constant import *
from json_handler import *


class Data:

    def __init__(self, pdu, msg_type, link):

        self.msg_type = msg_type
        if link != None:
            self.link = link

        if self.msg_type == "RRC":
            self.decode_rrc(pdu, self.link)

        elif self.msg_type == "NAS":
            self.decode_nas(pdu, self.link)

        elif self.msg_type == "MIB" or self.msg_type == "SIB1" or self.msg_type == "SIB2" or self.msg_type == "SIB3":
            self.pdu = pdu

    def decode_rrc(self, pdu, link):

        if link == DOWNLINK:
            sch = RRCLTE.EUTRA_RRC_Definitions.DL_DCCH_Message
            sch.from_uper(unhexlify(pdu))
            self.pdu = sch.to_json()

        else:
            sch = RRCLTE.EUTRA_RRC_Definitions.UL_DCCH_Message
            sch.from_uper(unhexlify(pdu))
            self.pdu = sch.to_json()


    def decode_nas(self, pdu, link):

        if link == DOWNLINK:
            Msg, err = parse_NAS_MT(unhexlify(pdu))
            sec_header_type = get_key_value(Msg.to_json(), "SecHdr")
            if isinstance(sec_header_type, str):
                if int(sec_header_type)==2 or int(sec_header_type)==4:
                    hex = get_key_value(Msg.to_json(), "NASMessage")
                    Msg, err = parse_NAS_MT(unhexlify(hex))
                    
        if link == UPLINK:
            Msg, err = parse_NAS_MO(unhexlify(pdu))
            sec_header_type = get_key_value(Msg.to_json(), "SecHdr")
            if isinstance(sec_header_type, str):
                if int(sec_header_type)==2 or int(sec_header_type)==4:
                    hex = get_key_value(Msg.to_json(), "NASMessage")
                    Msg, err = parse_NAS_MO(unhexlify(hex))
                    

        self.pdu = Msg.to_json()

    def get_pdu(self):
        return self.pdu


    def get_link(self):
        return self.link