import subprocess
import datetime
import time
import threading
from utils import *
from colorama import init, Fore, Back
import os
from constant import *
from communication import *
from data import *
from srsran_handle import *
import queue



enb_cipher_algo_supported = []
epc_cipher_algo_supported = []
enb_integ_algo_supported = []
epc_integ_algo_supported = []
preferred_algorithms = [None,None,None,None]

# ---------------------------------------------- Utilities ---------------------------------------------- #

def attach_ue(eea, eia):
    if eea == 0 and eia is None:
        return run_ue("eea", None)
    if eea is not None and eia is None:
        return run_ue("eea", eea)
    elif eea is None and eia is not None:
        return run_ue("eia", eia)

def srsran_communication_handler(messagges):

    srsran_handle = Srsran_handle()
    msg_parsed = srsran_handle.receive_msg()
    messagges.put(msg_parsed)



def run_ue(algo_type, algo_value):
    
    messagges = queue.Queue()
    srsran_communication_manager = threading.Thread(target=srsran_communication_handler, args=(messagges, ))
    srsran_communication_manager.start()


    if REAL_TESTING:
        
        if algo_type == "eea" and algo_value == None:
            print(f"[5GMAP] Attaching with {algo_type} = 0")
            command = f"sudo ./5gmap_real.sh --nas.{algo_type}=0"

        else:
            print(f"[5GMAP] Attaching with {algo_type} = 0,{algo_value}")
            command = f"sudo ./5gmap_real.sh --nas.{algo_type}=0,{algo_value}"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    else:
        
        if algo_type == "eea" and algo_value == None:
            print(f"[5GMAP] Attaching with {algo_type} = 0")
            command = f"sudo ./5gmap_sim.sh --nas.{algo_type}=0"
        else:
            print(f"[5GMAP] Attaching with {algo_type} = 0,{algo_value}")
            command = f"sudo ./5gmap_sim.sh --nas.{algo_type}=0,{algo_value}"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    srsran_communication_manager.join()
    messagges_parsed = messagges.get()


    if REAL_TESTING:
        completed_ue_process = subprocess.run(KILL_UE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    else:

        completed_ue_process = subprocess.run(KILL_UE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        completed_enb_process = subprocess.run(KILL_ENB, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)



    time.sleep(5)
    return messagges_parsed





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

def manage_sec_algos(communication):

    enb_cipher_algo, enb_integ_algo  = communication.find_enb_sec_algo()
    epc_cipher_algo, epc_integ_algo  = communication.find_epc_sec_algo()
    if (enb_cipher_algo is not None and enb_cipher_algo not in enb_cipher_algo_supported) :
        print("[5GMAP] enb_cipher_algo = ",enb_cipher_algo)
        enb_cipher_algo_supported.append(enb_cipher_algo)
    
    if (enb_integ_algo is not None and enb_integ_algo not in enb_integ_algo_supported) :
        print("[5GMAP] enb_integ_algo = ",enb_integ_algo)
        enb_integ_algo_supported.append(enb_integ_algo)


    if (epc_cipher_algo is not None and epc_cipher_algo not in epc_cipher_algo_supported) :
        print("[5GMAP] epc_cipher_algo = ", epc_cipher_algo)
        epc_cipher_algo_supported.append(epc_cipher_algo)
    
    if (epc_integ_algo is not None and epc_integ_algo not in epc_integ_algo_supported) :
        print("[5GMAP] epc_integ_algo = ",epc_integ_algo)
        epc_integ_algo_supported.append(epc_integ_algo)
    
    if communication.get_ciph_algo() is None and preferred_algorithms[0] is None:
        preferred_algorithms[0] = enb_cipher_algo

    if communication.get_integ_algo() is None and preferred_algorithms[1] is None:
        preferred_algorithms[1] = enb_integ_algo

    if communication.get_ciph_algo() is None and preferred_algorithms[2] is None:
        preferred_algorithms[2] = epc_cipher_algo
       
    if communication.get_integ_algo() is None and preferred_algorithms[3] is None:
        preferred_algorithms[3] = epc_integ_algo
# -------------------------------------------------------------------------------------------------------- #



def run_cipher_algorithm(eea):

    
    msg_sections = attach_ue(eea, None)
    communication = manage_messages(msg_sections, [0, eea], None)
    manage_sec_algos(communication)
    return communication


def run_integ_algorithm(eia):

    
    msg_sections = attach_ue(None, eia)    
    communication = manage_messages(msg_sections, None, [0, eia])
    manage_sec_algos(communication)
    return communication
    



def main():
    
    print_header()
    for eea in range(0, CIPHER_ALGORITHMS):
        communication = run_cipher_algorithm(eea)

    for eia in range(1, INT_ALGORITHMS):
         communication = run_integ_algorithm(eia)

    retrieve_cell_info(communication)
    print_security_algo_supported(enb_cipher_algo_supported, enb_integ_algo_supported, epc_cipher_algo_supported, epc_integ_algo_supported, preferred_algorithms)








if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    execution_time = end - start
    print(f"Execution time: {execution_time} seconds")

