import subprocess
import datetime
import time
import json_handler
import decoders
from utils import *
import CryptoMobile
from colorama import init, Fore, Back
import os
import signal
from constant import *
from communication import *
from data import *


Attach_proc_mex_dec = {}
enb_cipher_algo_supported = []
epc_cipher_algo_supported = []
enb_integ_algo_supported = []
epc_integ_algo_supported = []
preferred_algorithms = [None,None,None,None]



# ---------------------------------------------- Utilities ---------------------------------------------- #
def attach_ue(eea, eia):
    if eea is not None and eia is None:
        run_ue("eea", eea)
    elif eea is None and eia is not None:
        run_ue("eia", eia)

def run_ue(algo_type, algo_value):

    print(f"sudo ./5gmap_sim.sh --nas.{algo_type}=0,{algo_value}")
    command = f"sudo ./5gmap_sim.sh --nas.{algo_type}=0,{algo_value}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    os.mkfifo(PIPE_PATH)
    try:
        message = open(PIPE_PATH, 'r')
        if message.read() == SECURITY_MODE_REJECT:
            print(f"'Security Mode Reject' if try to attach with : '{algo_type}0' & '{algo_type}{algo_value}'")

        completed_ue_process = subprocess.run(KILL_UE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        completed_enb_process = subprocess.run(KILL_ENB, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    finally:
        os.remove(PIPE_PATH)
        time.sleep(5)



# def wait_ue_signal(eea, eia):


#     if (eea != None and eia == None):
#         #command = "./ue.sh --nas.eea='0," + str(eea) + "'"
#         #print("sudo ./5gmap_sim.sh --nas.eea=0," + str(eea))
#         command = "sudo ./5gmap_sim.sh --nas.eea=0," + str(eea)
#         process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         # Crea la pipe
#         #pipe_path = "./my_pipe"
#         os.mkfifo(PIPE_PATH)
#         try:
#             #print("Waiting for UE attach procedure finish")
#             message = open(PIPE_PATH, 'r')
#         finally:
#             if (message.read() == SECURITY_MODE_REJECT):
#                 print("'Security Mode Reject' if try to attach with : 'eea0' & 'eea" + str(eea) +"'")
            
#             # Esegui il comando di kill
#             completed_ue_process = subprocess.run(KILL_UE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#             completed_enb_process = subprocess.run(KILL_ENB, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#             os.remove(PIPE_PATH)
#             time.sleep(4)


#     elif (eea == None and eia != None):
#         #print("sudo ./5gmap_sim.sh --nas.eia=0," + str(eia))
#         command = "sudo ./5gmap_sim.sh  --nas.eia=0," + str(eia)
#         process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         # Crea la pipe
#         os.mkfifo(PIPE_PATH)
#         try:
#             #print("Waiting for UE attach procedure finish")
#             message = open(PIPE_PATH, 'r')
#         finally:
#             # Interrompi il processo
#             if (message.read() == SECURITY_MODE_REJECT):
#                 print("'Security Mode Reject' if try to attach with : 'eia0' & 'eia" + str(eia) +"'")

#             # Esegui il comando di kill
#             completed_ue_process = subprocess.run(KILL_UE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#             completed_enb_process = subprocess.run(KILL_ENB, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

#             os.remove(PIPE_PATH)
#             time.sleep(4)

       
def manage_messages(msg_sections, cyph_algos, integ_algos):


    communication = Communication(cyph_algos, integ_algos)
    
    for section_name, section_lines in msg_sections.items():

            if section_name=="UPLINK_RRC":

                for ex_message in section_lines:
                    #print(ex_message)
                    data = Data(ex_message, "RRC", UPLINK)
                    communication.add_rrc_msg(data, data.get_link())


            elif section_name=="DOWNLINK_RRC":
                for ex_message in section_lines:
                    data = Data(ex_message, "RRC", DOWNLINK)
                    communication.add_rrc_msg(data, data.get_link())


            elif section_name=="UPLINK_NAS":
                for ex_message in section_lines:
                    data = Data(ex_message, "NAS", UPLINK)
                    communication.add_nas_msg(data, data.get_link())

            elif section_name=="DOWNLINK_NAS":
                for ex_message in section_lines:
                    data = Data(ex_message, "NAS", DOWNLINK)
                    communication.add_nas_msg(data, data.get_link())

            else:
                
                data = Data(section_lines, section_name, None)
                
                if section_name == "MIB":
                    communication.set_mib_msg(data)

                if section_name == "SIB1":
                    communication.set_sib1_msg(data)

                if section_name == "SIB2":
                    communication.set_sib2_msg(data)

                if section_name == "SIB3":
                    communication.set_sib3_msg(data)

    
    return communication

def retrieve_cell_info(communication):
    
    sib1 = communication.get_sib1_msg().get_pdu()
    
    mcc = get_key_value(sib1, "mcc")
    mnc = get_key_value(sib1, "mnc")
    cellReservedForOperatorUse = get_key_value(sib1, "cellReservedForOperatorUse")
    trackingAreaCode = get_key_value(sib1, "trackingAreaCode")
    trackingAreaCode = int(trackingAreaCode, 2)
    cellIdentity = get_key_value(sib1, "cellIdentity")
    cellIdentity = int(cellIdentity, 2)
    intraFreqReselection = get_key_value(sib1, "intraFreqReselection")
    cellBarred = get_key_value(sib1, "cellBarred")
    
    print_cell_identity(mcc, mnc, cellReservedForOperatorUse, trackingAreaCode, cellIdentity, intraFreqReselection, cellBarred)

def manage_sec_algos(is_cipher_loop):

    enb_cipher_algo, enb_integ_algo  = communication.find_enb_sec_algo()
    epc_cipher_algo, epc_integ_algo  = communication.find_epc_sec_algo()
    # print("eNB cipher algo choice: ", enb_cipher_algo)
    # print("eNB integ algo choice: ", enb_integ_algo)
    # print("EPC cipher algo choice: ", epc_cipher_algo)
    # print("EPC integ algo choice: ", epc_integ_algo)
    if (enb_cipher_algo!=None and enb_cipher_algo not in enb_cipher_algo_supported) :
        enb_cipher_algo_supported.append(enb_cipher_algo)
    
    if (enb_integ_algo!=None and enb_integ_algo not in enb_integ_algo_supported) :
        enb_integ_algo_supported.append(enb_integ_algo)


    if (epc_cipher_algo!=None and epc_cipher_algo not in epc_cipher_algo_supported) :
        epc_cipher_algo_supported.append(epc_cipher_algo)
    
    if (epc_integ_algo!=None and epc_integ_algo not in epc_integ_algo_supported) :
        epc_integ_algo_supported.append(epc_integ_algo)
    
    if communication.get_ciph_algo() == None and preferred_algorithms[0] == None:
        preferred_algorithms[0] = enb_cipher_algo

    if communication.get_integ_algo() == None and preferred_algorithms[1] == None:
        preferred_algorithms[1] = enb_integ_algo

    if communication.get_ciph_algo() == None and preferred_algorithms[2] == None:
        preferred_algorithms[2] = epc_cipher_algo
       
    if communication.get_integ_algo() == None and preferred_algorithms[3] == None:
        
        preferred_algorithms[3] = epc_integ_algo
# -------------------------------------------------------------------------------------------------------- #



if __name__ == "__main__":

    current_time = datetime.datetime.now() 
    start = time.time()
    print(f"Starting 5GMap (https://github.com/chiacchius/5gmap) at {current_time.strftime('%Y-%m-%d %H:%M %Z')}")
    print("It may take several minutes.")
    print("""
╭─────────────────────────────────────────────────╮
│ .------.  ,----.  ,--.   ,--.  ,---.  ,------.  │
│ |  .--.' '  .-./  |   `.'   | /  O  \\ |  .--. ' │
│ '---. \\ |  | .---.|  |'.'|  ||  .-.  ||  '--' | │
│ .---' / '  '--'  ||  |   |  ||  | |  ||  | --'  │
│ `----'   `------' `--'   `--'`--' `--'`--'      │
╰─────────────────────────────────────────────────╯
""")
    
    #iterate over CIPHER ALGORITHMS
    for eea in range(1, CIPHER_ALGORITHMS):
        
        #wait_ue_signal(eea, None)
        attach_ue(eea, None)
        #file_path = "./5g_connection.txt" 
        msg_sections = parse_file(FILE_PATH)
        communication = manage_messages(msg_sections, [0, eea], None)
        if (eea==1):
            retrieve_cell_info(communication)
        manage_sec_algos(True)
    

    for eia in range(1, INT_ALGORITHMS):

        #wait_ue_signal(None, eia)
        attach_ue(None, eia)
        #file_path = "./5g_connection.txt" 
        msg_sections = parse_file(FILE_PATH)
        communication = manage_messages(msg_sections, None, [0, eia])
        manage_sec_algos(False)

    #cell_information_gathering()
    print_security_algo_supported(enb_cipher_algo_supported, enb_integ_algo_supported, epc_cipher_algo_supported, epc_integ_algo_supported, preferred_algorithms)
    end = time.time()
    execution_time = end - start
    print(f"Execution time: {execution_time} seconds")


        

    

