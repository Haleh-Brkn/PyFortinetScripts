from netmiko import Netmiko
import re
fortinet = {
    'host':'192.168.112.132',
    'username': 'admin',
    'password': 'admin',
    'device_type': 'fortinet'
}
net_connect = Netmiko(**fortinet)

# Regex Patterns for Both MAC and IP address validation
IPREGEX = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
MACREGEX = r"^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$"


ValidatedMAC = None;
ValidatedIP = None;
## validate the MAC address and will store it in "ValidatedMAC variable"
while ValidatedMAC is None:
    MACAddress = input("Enter the MAC addres: ") # NEEDS VALIDATION Before Process
    if re.match(MACREGEX, MACAddress):
        ValidatedMAC = MACAddress
    else:
        print("error: MAC address format is NOT valid. use format like: 00:11:22:33:44:55 ")

## validate the IP address and will store it in "ValidatedIP variable"
while ValidatedIP is None:
    IPAddress = input("Enter the IP Address: ") # NEEDS VALIDATION Before Process
    if re.match(IPREGEX, IPAddress):
        ValidatedIP = IPAddress
    else:
        print("error: the IP address format is NOT valid. use format like: 192.168.1.30 ")

# this function will receive the result of show output command in fortinet CLI and map through arp-table and look for biggest ID in table.
# then it will increment by 1 and assign and keep new ID in "ReceivedData ID" key.
def Get_Next_Arp_Edit_Number(show_output):
    editNumber=[]
    for line in show_output.splitlines():   
        line = line.strip()
        if line.startswith("edit"):
            try:
                number = int(line.split()[1])
                editNumber.append(number)
            except (IndexError, ValueError):
                print(f"could not parse edit number in line: {line}")
    if not editNumber:
        return 1
    else:
        return max(editNumber) + 1

# this is a dictionary in order to keep dynamic IP, MAC and ID
RecievedData = {
    "IPAddress": ValidatedIP,
    "MACAddress": ValidatedMAC,
    "ID": '0',
}

# Array of Commands:
# "show_command_fortinet" is to print out the result of show command for Created arp-table in vdom.
show_command_fortinet = [
    "config vdom",
    "edit root",
    "config system arp-table",
    "show"
]
list_of_arp_table = net_connect.send_config_set(show_command_fortinet)

# send the fortinet show arp-table result to the "Get_Next_Arp_Edit_Number" function to create new ID and assign in to ReceivedData ID.
RecievedData["ID"] = Get_Next_Arp_Edit_Number(list_of_arp_table)

# it will create new arp-table edit and assign MAC, IP and ID to it based on Operator Input.
print(f"### configuring for {RecievedData['IPAddress']} with the MAC {RecievedData['MACAddress']} ### ") #use one quotation inside formatted-string that is wrapped around double-quotation
config_commands = [
  "config vdom",
  "edit root",
  "config system arp-table",
  f"edit {RecievedData['ID']}",
  f"set ip {RecievedData['IPAddress']}",
  f"set mac {RecievedData['MACAddress']}",
  "set interface port1",
  "next",
  "end",
 ]


# to print the command result on terminal.
final_configuration = net_connect.send_config_set(config_commands)
print(f"#### result is: ####\n {config_commands}")


# TODO: The Ports are also Dynamic and we need a way to figure out how to configure the Port Based On IPs. (Nasty and Not Organized)
