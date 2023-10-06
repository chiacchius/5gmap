from constant import *
import datetime
from tabulate import *


border = "+-------------------------+"

def print_security_algo_supported(enb_cipher_algo_supported, integrityProtAlgorithm_eNB, epc_cipher_algo_supported, epc_integ_algo_supported, preferred_algorithms):
    print("\n" + border)
    print("| eNB Security Algorithms |")
    print(border)
    print("| {:<28} | {:<}".format("eNB_cipheringAlgorithm_supported", str(enb_cipher_algo_supported)))
    print("| {:<28} | {:<}".format("eNB_integrityAlgorithm_supported", str(integrityProtAlgorithm_eNB)))
    print("| {:<28} | {:<}".format("eNB_preferred_cipheringAlgorithm", str(preferred_algorithms[0])))
    print("| {:<28} | {:<}".format("eNB_preferred_integrityAlgorithm", str(preferred_algorithms[1])))
    print("\n" + border)
    print("| EPC Security Algorithms |")
    print(border)
    print("| {:<28} | {:<}".format("EPC_cipheringAlgorithm_supported", str(epc_cipher_algo_supported)))
    print("| {:<28} | {:<}".format("EPC_integrityAlgorithm_supported", str(epc_integ_algo_supported)))
    print("| {:<28} | {:<}".format("EPC_preferred_cipheringAlgorithm", str(preferred_algorithms[2])))
    print("| {:<28} | {:<}".format("EPC_preferred_integrityAlgorithm", str(preferred_algorithms[3])))
    print_table()



def print_table():
    print("\n\nThe table below provides a summary of the algorithm types and their corresponding descriptions.")
    parameters = ["Type", "Decription"]
    data = [
        ["EEA0", "Null ciphering algorithm"],
        ["EEA1", "SNOW 3G"],
        ["EEA2", "AES"],
        ["EEA3", "ZUC"]
    ]

    # Crea la tabella utilizzando tabulate
    table = tabulate(data, headers=parameters, tablefmt="grid")

    # Stampa la tabella
    print(table)

def print_cell_identity(mcc, mnc, cellReservedForOperatorUse, trackingAreaCode, cellIdentity, intraFreqReselection, cellBarred):
    print("\n\n")
    print(border)
    print("|       Cell identity     |")
    print(border)
    print("| {:<28} | {:<}".format("mcc", str(mcc)))
    print("| {:<28} | {:<}".format("mnc", str(mnc)))
    #print("| {:<28} | {:<}".format("cellReservedForOperatorUse", cellReservedForOperatorUse))
    print("| {:<28} | {:<}".format("trackingAreaCode", trackingAreaCode))
    print("| {:<28} | {:<}".format("cellIdentity", cellIdentity))
    #print("| {:<28} | {:<}".format("intraFreqReselection", intraFreqReselection))
    #print("| {:<28} | {:<}".format("cellBarred", cellBarred))
    

def print_header():
    current_time = datetime.datetime.now() 
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
    if REAL_TESTING:
        #manage imsi 
        print("[5GMAP] Binding to Base Station")

    else:

        print("[5GMAP] Simulation with srsran")


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
    
