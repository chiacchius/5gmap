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


file = None
Attach_proc_mex_dec = {}
ue_pid = 0
enb_cipher_algo_supported = []
enb_integ_algo_supported = []

def cell_information_gathering():
    
    #I primi valori sono le informazioni sulla cella:
    #Si analizzano mib e i sibs

    item = Attach_proc_mex_dec["SIB1"][0]
    mcc = json_handler.parse_json_msg(item, "mcc")
    mnc = json_handler.parse_json_msg(item, "mnc")
    cellReservedForOperatorUse = json_handler.parse_json_msg(item, "cellReservedForOperatorUse")
    trackingAreaCode = json_handler.parse_json_msg(item, "trackingAreaCode")
    trackingAreaCode = int(trackingAreaCode, 2)
    cellIdentity = json_handler.parse_json_msg(item, "cellIdentity")
    cellIdentity = int(cellIdentity, 2)
    intraFreqReselection = json_handler.parse_json_msg(item, "intraFreqReselection")
    cellBarred = json_handler.parse_json_msg(item, "cellBarred")
    
    

    print_cell_identity(mcc, mnc, cellReservedForOperatorUse, trackingAreaCode, cellIdentity, intraFreqReselection, cellBarred)


def retrieve_security_alghoritms():

    #manage uplink parameter
    uL_nas = 0
    for item in Attach_proc_mex_dec["UPLINK_RRC"]:
        #print(item)

        if json_handler.parse_json_msg(item, "rrcConnectionSetupComplete")!=None:

            selectedPLMN_Identity = json_handler.parse_json_msg(item, "selectedPLMN-Identity")
        

        #check if there is a nas message
        if json_handler.parse_json_msg(item, "dedicatedInfoNAS") != None or json_handler.parse_json_msg(item, "dedicatedInfoNASList") != None:
            uL_nas += 1


    #manage dowlink parameter
    dL_nas = 0
    for item in Attach_proc_mex_dec["DOWNLINK_RRC"]:

        if json_handler.parse_json_msg(item, "securityModeCommand")!=None:

            #get bs algortithms decision
            
            cipheringAlgorithm_eNB = json_handler.parse_json_msg(item, "cipheringAlgorithm")
            integrityProtAlgorithm_eNB = json_handler.parse_json_msg(item, "integrityProtAlgorithm")
            
            if (cipheringAlgorithm_eNB not in enb_cipher_algo_supported):
                enb_cipher_algo_supported.append(cipheringAlgorithm_eNB)

            if (integrityProtAlgorithm_eNB not in enb_integ_algo_supported):
                enb_integ_algo_supported.append(integrityProtAlgorithm_eNB)

            

            
            


        if json_handler.parse_json_msg(item, "dedicatedInfoNAS") != None or json_handler.parse_json_msg(item, "dedicatedInfoNASList") != None:

            #get core algortithms decision
            if(Attach_proc_mex_dec["DOWNLINK_NAS"][dL_nas]._name == "EMMSecProtNASMessage"):

                cipheringAlgorithm_EPC = json_handler.parse_nas_message(Attach_proc_mex_dec["DOWNLINK_NAS"][dL_nas], "CiphAlgo")
                cipheringAlgorithm_EPC = "eea" + cipheringAlgorithm_EPC
                integrityProtAlgorithm_EPC = json_handler.parse_nas_message(Attach_proc_mex_dec["DOWNLINK_NAS"][dL_nas], "IntegAlgo")
                integrityProtAlgorithm_EPC = "eia" + integrityProtAlgorithm_EPC
       
                


            dL_nas += 1
    

def wait_ue_signal(eea, eia):
    # Avvia il processo

    if (eea != None and eia == None):


        
        #command = "./ue.sh --nas.eea='0," + str(eea) + "'"
        #print("sudo ./5gmap_sim.sh --nas.eaa=0," + str(eea))
        command = "sudo ./5gmap_sim.sh --nas.eea=0," + str(eea)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        # Crea la pipe
        pipe_path = "./my_pipe"
        os.mkfifo(pipe_path)

        try:
            #print("Waiting for UE attach procedure finish")

            open(pipe_path, 'r')
                
        finally:
            # Interrompi il processo
            kill_ue_command = ["sudo", "pkill", "srsue"]
            kill_enb_command = ["sudo", "pkill", "srsenb"]

            # Esegui il comando di kill
            completed_ue_process = subprocess.run(kill_ue_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            completed_enb_process = subprocess.run(kill_enb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            # Verifica il codice di uscita del processo
            # if completed_ue_process.returncode is None or completed_enb_process.returncode is None:
            #     print("Shutdown UE failed")
            # else:
            #     print("Shutdown UE completed")

            os.remove(pipe_path)
            time.sleep(5)



    elif (eea == None and eia != None):


       
        #print("sudo ./5gmap_sim.sh --nas.eia=1," + str(eia))
        command = "sudo ./5gmap_sim.sh  --nas.eia=1," + str(eia)




        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        # Crea la pipe
        pipe_path = "./my_pipe"
        os.mkfifo(pipe_path)

        try:
            #print("Waiting for UE attach procedure finish")

            open(pipe_path, 'r')
           

        finally:
            # Interrompi il processo
            kill_ue_command = ["sudo", "pkill", "srsue"]
            kill_enb_command = ["sudo", "pkill", "srsenb"]

            # Esegui il comando di kill
            completed_ue_process = subprocess.run(kill_ue_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            completed_enb_process = subprocess.run(kill_enb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            # Verifica il codice di uscita del processo
            # if completed_ue_process.returncode is None or completed_enb_process.returncode is None:
            #     print("Shutdown UE failed")
            # else:
            #     print("Shutdown UE completed")

            os.remove(pipe_path)
            time.sleep(5)
       




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

    
        wait_ue_signal(eea, None)

        file_path = "./5g_connection.txt" 
        sections = parse_file(file_path)
        file = open("parameters_parsed.txt", "+w")
        
        Attach_proc_mex_dec = file_mex_manager(file, sections)

        retrieve_security_alghoritms()


    for eia in range(2, INT_ALGORITHMS):

    
        wait_ue_signal(None, eia)

        file_path = "./5g_connection.txt" 
        sections = parse_file(file_path)
        file = open("parameters_parsed.txt", "+w")
        
        Attach_proc_mex_dec = file_mex_manager(file, sections)

        retrieve_security_alghoritms()


        
        
        
        
        
        
        
    cell_information_gathering()
    print_security_algo_supported(enb_cipher_algo_supported, enb_integ_algo_supported)

    end = time.time()
    execution_time = end - start
    print(f"Execution time: {execution_time} seconds")


        

    
