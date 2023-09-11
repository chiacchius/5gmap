import decoders
from constant import *


border = "+-------------------------+"

def print_security_algo_supported(enb_cipher_algo_supported, integrityProtAlgorithm_eNB):
    print("\n" + border)
    print("| eNB Security Algorithms |")
    print(border)
    print("| {:<28} | {:<}".format("eNB_cipheringAlgorithm_supported", str(enb_cipher_algo_supported)))
    print("| {:<28} | {:<}".format("eNB_integrityAlgorithm_supported", str(integrityProtAlgorithm_eNB)))
    #print("| {:<28} | {:<}".format("eNB_integrityProtAlgorithm", integrityProtAlgorithm_eNB))




def print_cell_identity(mcc, mnc, cellReservedForOperatorUse, trackingAreaCode, cellIdentity, intraFreqReselection, cellBarred):
    
    print(border)
    print("|       Cell identity     |")
    print(border)
    print("| {:<28} | {:<}".format("mcc", str(mcc)))
    print("| {:<28} | {:<}".format("mnc", str(mnc)))
    print("| {:<28} | {:<}".format("cellReservedForOperatorUse", cellReservedForOperatorUse))
    print("| {:<28} | {:<}".format("trackingAreaCode", trackingAreaCode))
    print("| {:<28} | {:<}".format("cellIdentity", cellIdentity))
    print("| {:<28} | {:<}".format("intraFreqReselection", intraFreqReselection))
    print("| {:<28} | {:<}".format("cellBarred", cellBarred))
    




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
    


def file_mex_manager(file, sections):

    Attach_proc_mex_dec = {}


    for section_name, section_lines in sections.items():

            Attach_proc_mex_dec[section_name] = []
        
            
            #print(f"{section_name}")
            if section_name=="UPLINK_RRC":
                for ex_message in section_lines:
                    #print(ex_message)
                    Attach_proc_mex_dec["UPLINK_RRC"].append(decoders.asn1_rrc_decode(UPLINK, ex_message, file))

            elif section_name=="DOWNLINK_RRC":
                for ex_message in section_lines:
                    #print(ex_message)
                    Attach_proc_mex_dec["DOWNLINK_RRC"].append(decoders.asn1_rrc_decode(DOWNLINK, ex_message, file))


            elif section_name=="UPLINK_NAS":
                for ex_message in section_lines:
                    
                    #print(ex_message)
                    Attach_proc_mex_dec["UPLINK_NAS"].append(decoders.asn1_nas_decode(UPLINK, ex_message, file))

            elif section_name=="DOWNLINK_NAS":
                for ex_message in section_lines:
                    #print(ex_message)
                    Attach_proc_mex_dec["DOWNLINK_NAS"].append(decoders.asn1_nas_decode(DOWNLINK, ex_message, file))

            else:
                
                formatted_string = "{}\n {}\n ------------- \n".format(section_name, section_lines)
                Attach_proc_mex_dec[section_name].append(section_lines)
                #print(formatted_string)
                file.write(formatted_string)
                #print(section_lines)

    return Attach_proc_mex_dec