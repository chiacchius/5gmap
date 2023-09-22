from binascii import unhexlify, hexlify
from pycrate_mobile.NAS import *
from pycrate_asn1dir import RRCLTE
import binascii
import ast
from constant import *








def asn1_rrc_decode(link, bytes, file):
    
    if link == DOWNLINK:
        sch = RRCLTE.EUTRA_RRC_Definitions.DL_DCCH_Message
        sch.from_uper(unhexlify(bytes))
        
        file.write("RRC DOWNLINK\n")
        file.flush()
        file.write("------------- \n")
        file.flush()
        return sch.to_json()

    elif link == UPLINK: 
        sch = RRCLTE.EUTRA_RRC_Definitions.UL_DCCH_Message
        sch.from_uper(unhexlify(bytes))
        
        file.write("RRC UPLINK\n")
        file.flush()
        file.write("------------- \n")
        file.flush()
        return sch.to_json()


def asn1_nas_decode(link, bytes, file):
    
    if link == DOWNLINK:
        #print(sch.to_asn1())
        Msg, err = parse_NAS_MT(unhexlify(bytes))
        file.write("NAS DOWNLINK\n" + str(Msg.to_json()) + "\n ------------- \n")
        file.flush()
        return Msg.to_json()

    if link == UPLINK:
        #print(sch.to_asn1())
        Msg, err = parse_NAS_MO(unhexlify(bytes))
        file.write("NAS UPLINK\n" + str(Msg.to_json()) + "\n ------------- \n")
        file.flush()
        return Msg.to_json()

# def asn1_nas_decode(link, bytes, file):

#     Msg= ""
    
#     if link == DOWNLINK:
#         #print(sch.to_asn1())
#         Msg, err = parse_NAS_MT(unhexlify(bytes))
#         newMsg = get_NASMessage_if_SecHdr_is_2(str(Msg))
#         #print(type(Msg))
#         if newMsg!= None:
#             nas_message_binary_data = ast.literal_eval(newMsg)
#             hex_data = binascii.hexlify(nas_message_binary_data).decode()
            
#             Msg, err = parse_NAS_MT(unhexlify(hex_data))
            
#             #json_handler.parse_nas_message(Msg, Msg._name)
#             file.write("NAS DOWNLINK\n" + str(Msg) + "\n ------------- \n")
#             file.flush()
#             return Msg

#         else:
#             #json_handler.parse_nas_message(Msg, Msg._name)
#             file.write("NAS DOWNLINK\n" + str(Msg) + "\n ------------- \n")
#             file.flush()
#             return Msg
#             #show(Msg)
        

#     elif link == UPLINK: 
#         Msg, err = parse_NAS_MO(unhexlify(bytes))
#         newMsg = get_NASMessage_if_SecHdr_is_2(str(Msg))
#         #print(newMsg)
#         if newMsg!= None:
#             nas_message_binary_data = ast.literal_eval(newMsg)
#             #print(nas_message_binary_data)
#             hex_data = binascii.hexlify(nas_message_binary_data).decode()
#             Msg, err = parse_NAS_MO(unhexlify(hex_data))
            
#             #show(Msg)
#             #json_handler.parse_nas_message(Msg, Msg._name)
#             file.write("NAS UPLINK\n" + str(Msg) + "\n ------------- \n")
#             file.flush()
#             return Msg

#         else:
#             #show(Msg)
#             #json_handler.parse_nas_message(Msg, Msg._name)
#             file.write("NAS UPLINK\n" + str(Msg) + "\n ------------- \n")
#             file.flush()
#             return Msg


# def get_NASMessage_if_SecHdr_is_2(input_string):
    
#     sec_hdr_start = input_string.find("<SecHdr : 2")
#     if sec_hdr_start == -1:
#         sec_hdr_start = input_string.find("<SecHdr : 4")
#     if sec_hdr_start != -1:
#         nas_message_start = input_string.find("<NASMessage : ", sec_hdr_start)
#         if nas_message_start != -1:
#             nas_message_hex = input_string[nas_message_start + 14: -2].strip()
#             return nas_message_hex
    
#     return None