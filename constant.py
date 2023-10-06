#-------------------- Parameters to change ---------------------#
REAL_TESTING = False
EARFCN = 3500
#---------------------------------------------------------------#
#--------------------  Fixed parameters  -----------------------#
DOWNLINK = 0
UPLINK = 1

CIPHER_ALGORITHMS = 4
INT_ALGORITHMS = 4

# Error types managed
ATTACHED = "Attached"
SECURITY_MODE_REJECT = "Security Mode Reject"
ATTACH_REJECT_13 = "Attach reject #13: Could not attach, try changing your APN"
ATTACH_REJECT_14 = "Attach reject #14: Could not attach with these capabilities"
ATTACH_REJECT = "EPC sent attach reject"
RRC_CONN_REL="RRC Connection Release"

#Commands
KILL_UE = ["sudo", "pkill", "srsue"]
KILL_ENB = ["sudo", "pkill", "srsenb"]
#---------------------------------------------------------------#


