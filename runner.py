import socket
import threading
import struct
import subprocess
from pycrate_mobile.NAS import *
from pycrate_asn1dir import RRCLTE
from binascii import unhexlify, hexlify
import binascii
import ast
import json_handler
import CryptoMobile
from colorama import init, Fore, Back
import os
import signal


DOWNLINK = 0
UPLINK = 1
file = None
Attach_proc_mex_dec = {}
ue_pid = 0


def asn1_rrc_decode(link, bytes):
    
    if link == DOWNLINK:
        sch = RRCLTE.EUTRA_RRC_Definitions.DL_DCCH_Message
        sch.from_uper(unhexlify(bytes))
        Attach_proc_mex_dec["DOWNLINK_RRC"].append(sch.to_json())
        file.write("RRC DOWNLINK\n")
        file.flush()
        file.write("------------- \n")
        file.flush()

    elif link == UPLINK: 
        sch = RRCLTE.EUTRA_RRC_Definitions.UL_DCCH_Message
        sch.from_uper(unhexlify(bytes))
        Attach_proc_mex_dec["UPLINK_RRC"].append(sch.to_json())
        file.write("RRC UPLINK\n")
        file.flush()
        file.write("------------- \n")
        file.flush()
    

def get_NASMessage_if_SecHdr_is_2(input_string):
    
    sec_hdr_start = input_string.find("<SecHdr : 2")
    if sec_hdr_start == -1:
        sec_hdr_start = input_string.find("<SecHdr : 4")
    if sec_hdr_start != -1:
        nas_message_start = input_string.find("<NASMessage : ", sec_hdr_start)
        if nas_message_start != -1:
            nas_message_hex = input_string[nas_message_start + 14: -2].strip()
            return nas_message_hex
    
    return None

def asn1_nas_decode(link, bytes):

    Msg= ""
    
    if link == DOWNLINK:
        #print(sch.to_asn1())
        Msg, err = parse_NAS_MT(unhexlify(bytes))
        newMsg = get_NASMessage_if_SecHdr_is_2(str(Msg))
        #print(type(Msg))
        if newMsg!= None:
            nas_message_binary_data = ast.literal_eval(newMsg)
            hex_data = binascii.hexlify(nas_message_binary_data).decode()
            
            Msg, err = parse_NAS_MT(unhexlify(hex_data))
            Attach_proc_mex_dec["DOWNLINK_NAS"].append(Msg)
            #json_handler.parse_nas_message(Msg, Msg._name)
            file.write("NAS DOWNLINK\n" + str(Msg) + "\n ------------- \n")
            file.flush()
            #show(Msg)

        else:
            Attach_proc_mex_dec["DOWNLINK_NAS"].append(Msg)
            #json_handler.parse_nas_message(Msg, Msg._name)
            file.write("NAS DOWNLINK\n" + str(Msg) + "\n ------------- \n")
            file.flush()
            #show(Msg)
        

    elif link == UPLINK: 
        Msg, err = parse_NAS_MO(unhexlify(bytes))
        newMsg = get_NASMessage_if_SecHdr_is_2(str(Msg))
        #print(newMsg)
        if newMsg!= None:
            nas_message_binary_data = ast.literal_eval(newMsg)
            #print(nas_message_binary_data)
            hex_data = binascii.hexlify(nas_message_binary_data).decode()
            Msg, err = parse_NAS_MO(unhexlify(hex_data))
            Attach_proc_mex_dec["UPLINK_NAS"].append(Msg)
            #show(Msg)
            #json_handler.parse_nas_message(Msg, Msg._name)
            file.write("NAS UPLINK\n" + str(Msg) + "\n ------------- \n")
            file.flush()
            #show(Msg)

        else:
            #show(Msg)
            Attach_proc_mex_dec["UPLINK_NAS"].append(Msg)
            #json_handler.parse_nas_message(Msg, Msg._name)
            file.write("NAS UPLINK\n" + str(Msg) + "\n ------------- \n")
            file.flush()
            #show(Msg)
    


def parse_file(file_path):
    with open(file_path, 'r') as file:
        current_section = None
        sections = {}
        lines = []
        rrc_uplink_messages = []
        rrc_downlink_messages = []
        nas_uplink_messages = []
        nas_downlink_messages = []

        for line in file:
            #line = line.strip()

            if line.startswith("MIB:") | line.startswith("SIB1:") | line.startswith("SIB2:") | line.startswith("SIB3:"):
                if current_section is not None:
                    sections[current_section] = lines

                current_section = line[:-2]
                lines = ""

            elif line.startswith("UPLINK_RRC:"):
                if current_section is not None:
                    sections[current_section] = lines
                current_section = None
                rrc_uplink_messages.append(line[11:-1])

            elif line.startswith("DOWNLINK_RRC:"):
                if current_section is not None:
                    sections[current_section] = lines
                current_section = None
                rrc_downlink_messages.append(line[13:-1])
            
            elif line.startswith("UPLINK_NAS:"):
                if current_section is not None:
                    sections[current_section] = lines
                current_section = None
                nas_uplink_messages.append(line[11:-1])

            elif line.startswith("DOWNLINK_NAS:"):
                if current_section is not None:
                    sections[current_section] = lines
                current_section = None
                nas_downlink_messages.append(line[13:-1])

            else:
                lines = lines + line

        # Aggiungiamo l'ultima sezione trovata
        if current_section is not None:
            sections[current_section] = lines

        sections["UPLINK_RRC"] = rrc_uplink_messages
        sections["DOWNLINK_RRC"] = rrc_downlink_messages
        sections["UPLINK_NAS"] = nas_uplink_messages
        sections["DOWNLINK_NAS"] = nas_downlink_messages
        return sections


def cell_information_gathering():
    
    #I primi valori sono le informazioni sulla cella:
    #Si analizzano mib e i sibs

    item = Attach_proc_mex_dec["SIB1"][0]
    parameter = None
    mcc = json_handler.parse_json_msg(item, "mcc")
    mnc = json_handler.parse_json_msg(item, "mnc")
    cellReservedForOperatorUse = json_handler.parse_json_msg(item, "cellReservedForOperatorUse")
    trackingAreaCode = json_handler.parse_json_msg(item, "trackingAreaCode")
    cellIdentity = json_handler.parse_json_msg(item, "cellIdentity")
    intraFreqReselection = json_handler.parse_json_msg(item, "intraFreqReselection")
    cellBarred = json_handler.parse_json_msg(item, "cellBarred")

    print("Cell identity:")
    print("\tmcc: {}".format(mcc))
    print("\tmnc: {}".format(mnc))
    print("\tcellReservedForOperatorUse: {}".format(cellReservedForOperatorUse))
    print("\ttrackingAreaCode: {}".format(trackingAreaCode))
    print("\tcellIdentity: {}".format(cellIdentity))
    print("\tintraFreqReselection: {}".format(intraFreqReselection))
    print("\tcellBarred: {}".format(cellBarred))
    
    
    #manage uplink parameter
    uL_nas = 0
    for item in Attach_proc_mex_dec["UPLINK_RRC"]:
        #print(item)

        if json_handler.parse_json_msg(item, "rrcConnectionSetupComplete")!=None:

            selectedPLMN_Identity = json_handler.parse_json_msg(item, "selectedPLMN-Identity")
            if selectedPLMN_Identity != None:
                print("\tselectedPLMN_Identity: {}".format(selectedPLMN_Identity))
            
        

        #check if there is a nas message
        if json_handler.parse_json_msg(item, "dedicatedInfoNAS") != None or json_handler.parse_json_msg(item, "dedicatedInfoNASList") != None:
            uL_nas += 1


    #manage dowlink parameter
    dL_nas = 0
    for item in Attach_proc_mex_dec["DOWNLINK_RRC"]:

        


        if json_handler.parse_json_msg(item, "dedicatedInfoNAS") != None or json_handler.parse_json_msg(item, "dedicatedInfoNASList") != None:
            
            

            dL_nas += 1


    

def wait_ue_signal():
    # Avvia il processo
    command = "./ue.sh"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    # Crea la pipe
    pipe_path = "./my_pipe"
    os.mkfifo(pipe_path)

    try:
        print("Waiting for UE attach procedure finish")

        with open(pipe_path, 'r') as pipe:
            #data = pipe.read()
            print("Attach procedure finished with success")

    finally:
        # Interrompi il processo
        kill_command = ["sudo", "pkill", "srsue"]

        # Esegui il comando di kill
        completed_process = subprocess.run(kill_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Verifica il codice di uscita del processo
        if completed_process.returncode is None:
            print("Il comando di kill è ancora in esecuzione.")
        else:
            print("Il comando di kill è stato completato con codice di uscita:", completed_process.returncode)

        os.remove(pipe_path)
       


if __name__ == "__main__":

    #Aspetto che mi arrivi il segnale di inizio analisi
    # Ricevi il messaggio dallo standard input
    wait_ue_signal()

    file_path = "./5g_connection.txt" 
    sections = parse_file(file_path)
    file = open("parameters_parsed.txt", "+w")
    # Stampa i contenuti dei messaggi
    print("""
╭─────────────────────────────────────────────────╮
│ .------.  ,----.  ,--.   ,--.  ,---.  ,------.  │
│ |  .--.' '  .-./  |   `.'   | /  O  \\ |  .--. ' │
│ '---. \\ |  | .---.|  |'.'|  ||  .-.  ||  '--' | │
│ .---' / '  '--'  ||  |   |  ||  | |  ||  | --'  │
│ `----'   `------' `--'   `--'`--' `--'`--'      │
╰─────────────────────────────────────────────────╯
""")

    # Stampa il risultato
    for section_name, section_lines in sections.items():

        Attach_proc_mex_dec[section_name] = []
       
        
        #print(f"{section_name}")
        if section_name=="UPLINK_RRC":
            for ex_message in section_lines:
                #print(ex_message)
                asn1_rrc_decode(UPLINK, ex_message)

        elif section_name=="DOWNLINK_RRC":
            for ex_message in section_lines:
                #print(ex_message)
                asn1_rrc_decode(DOWNLINK, ex_message)


        elif section_name=="UPLINK_NAS":
            for ex_message in section_lines:
                
                #print(ex_message)
                asn1_nas_decode(UPLINK, ex_message)

        elif section_name=="DOWNLINK_NAS":
            for ex_message in section_lines:
                #print(ex_message)
                asn1_nas_decode(DOWNLINK, ex_message)

        else:
            
            formatted_string = "{}\n {}\n ------------- \n".format(section_name, section_lines)
            Attach_proc_mex_dec[section_name].append(section_lines)
            #print(formatted_string)
            file.write(formatted_string)
            #print(section_lines)
    
    
    

    cell_information_gathering()
