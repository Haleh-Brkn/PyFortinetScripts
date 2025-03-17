''''
V1.0: it receives the IP address and based on the IP address will look for relative Edit ID table.
then it will set the MAC address that is being received by Operator.

Update:
when Operator Enters the IP address it will iterate through arp-table to validate IP in arp-table as well.
after IP validation it will Request for new MAC address.

'''
import re 
from netmiko import Netmiko
import time

fortinet = {
    'host':'172.24.24.15',
    'username': 'admin',
    'password': 'admin',
    'device_type': 'fortinet'
}

net_connect = Netmiko(**fortinet)

# Regex Patterns for Both MAC and IP address validation
IPREGEX = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
MACREGEX = r"^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$"

ValidatedMAC = None
ValidatedIP = None
ValidatedEditID = ''

# 1. Get ARP Table Output
get_show_result_command_list = [
        "config vdom",
        "edit root",
        "config system arp-table",
        "show",
        "end",
        "end"
]

def parse_arp_table_output_for_ip_search(show_output):
    arp_entries = []
    current_entry = {}
    in_arp_table_config = False # Flag to track if we are inside 'config system arp-table'

    for line in show_output.splitlines():
        line = line.strip()

        if line == "config system arp-table":
            in_arp_table_config = True
            continue 
        if line == "end" and in_arp_table_config: # Detect 'end' within arp-table config
            in_arp_table_config = False
            continue 
        if not in_arp_table_config: # Skip lines outside arp-table config block
            continue

        if line.startswith("edit "):
            if current_entry: # Save previous entry if exists before starting new one
                arp_entries.append(current_entry)
            current_entry = {'edit_id': line.split()[1]} # Start new entry, extract edit ID
        elif line.startswith("set interface"):
            current_entry['interface'] = line.split()[2].strip('"') # Extract interface, remove quotes
        elif line.startswith("set ip"):
            current_entry['ip'] = line.split()[2] # Extract IP address
        elif line.startswith("set mac"):
            current_entry['mac'] = line.split()[2] # Extract MAC address

    if current_entry: # Add the last entry if any
        arp_entries.append(current_entry)
    else:
        print("arp-table cannot be parsed!")
    return arp_entries

def find_arp_entry_by_ip(arp_table_data, target_ip):
    for entry in arp_table_data:
        if 'ip' in entry and entry['ip'] == target_ip:
            if entry['mac']:
                print(f"\nThe IP {entry['ip']} has MAC address of {entry['mac']} ")
            else:
                print(f"\nNo MAC Address is set for IP {entry['ip']}")
            return {'edit_id': entry['edit_id'], 'interface': entry['interface']} # Return edit_id and interface
    return None  # IP address not found in ARP table

# Get ARP table data first
show_arp_table_output = net_connect.send_config_set(get_show_result_command_list)
arp_table_data = parse_arp_table_output_for_ip_search(show_arp_table_output)

## Validate the IP address and exit immediately if invalid or not in ARP table
while ValidatedIP is None:
    IPAddress = input("Enter the IP Address: ")
    if not re.match(IPREGEX, IPAddress):
        print("Error: The IP address format is NOT valid. Use format like: 192.168.1.30")
        continue
    
    # Check if IP exists in ARP table ( we do that by examinating the IPAddress variable instead of ValidatedIP variable)
    # it send the received IP to the function which will iterate through data recieved by show arp table command
    found_entry_info = find_arp_entry_by_ip(arp_table_data, IPAddress)
    if not found_entry_info:
        print("Error: The entered IP is NOT Registered in ARP-Table!")
        print("Please enter a valid IP address that exists in the ARP table.")
        continue
    
    # If we reach here, the IP is valid and exists in the ARP table
    ValidatedIP = IPAddress
    ValidatedEditID = found_entry_info['edit_id']
    # time.sleep(1)
    # print(f"Target IP address: {IPAddress} Selected")
    time.sleep(1)
    print(f"Target Edit ID is {found_entry_info['edit_id']}")

## validate the MAC address and will store it in "ValidatedMAC variable"
while ValidatedMAC is None:
    MACAddress = input("Enter the MAC address: ")
    if re.match(MACREGEX, MACAddress):
        ValidatedMAC = MACAddress
    else:
        print("Error: MAC address format is NOT valid. Use format like: 00:11:22:33:44:55")

# save all required data in a dictionary
RecievedData = {
    "IPAddress": ValidatedIP,
    "MACAddress": ValidatedMAC,
    "ID": ValidatedEditID,
}

time.sleep(1)
print(f"The given MAC address is {RecievedData['MACAddress']}")
time.sleep(1)
print("Applying Configuration...")
time.sleep(3)

# preparing commands scripts to Bind MAC address for selected Edit ID (which is defined via IP address)
Modify_MAC_Commands=[
    'config vdom',
    'edit root',
    'config system arp-table',
    f'edit {ValidatedEditID}',
    f'set mac {RecievedData["MACAddress"]}',
    'next',
    'end',
]

# applying changes on Fortinet CLI.
ModifiedMAC = net_connect.send_config_set(Modify_MAC_Commands)
print(f"\nMAC Binding is Successfully Done!")
net_connect.disconnect()
