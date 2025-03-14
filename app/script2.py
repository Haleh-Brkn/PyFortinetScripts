# Assigning IP addresses to Fortinet and Adding them to IP_group defined for each.
from csv import DictReader
import time
from netmiko import Netmiko

fortinethost = {
    "host": "192.168.112.132",
    "username": "admin",
    "password": "admin",
    "device_type":"fortinet"
}

net_connect = Netmiko(**fortinethost)
with open('../misc/ip_group.csv') as csv_file:
    ip_details = DictReader(csv_file)

    for ip in ip_details:
        time.sleep(0.5) # optional: setting a delay time in order to prevent throttling
        print(f"### configuring for {ip['Name']} with the IP {ip['IP']} ### ") #use one quotation inside formatted-string that is wrapped around double-quotation
        config_commands = [
                "config firewall address",
                f"edit {ip['Name']}",
                "set type ipmask",
                f"set subnet  {ip['IP']}/32",
                "end",
                "config firewall addrgrp",
                f"edit {ip['IPGroup']}",
                f"append member {ip['Name']}",
                "end"]
        sent_configs = net_connect.send_config_set(config_commands)
        print(f"Done! Log: {sent_configs}")
        # sentConfigs = net_connect.send_config_set(config_commands)        
        # print(f"done with logs: {sentConfigs}")