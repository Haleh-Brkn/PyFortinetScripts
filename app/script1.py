from csv import DictReader # importing DictReader to Read from csv file and turn them into python dictionary. come handy later
from netmiko import Netmiko
import time 
fortinethost = {
    "host": "192.168.112.132",
    "username": "admin",
    "password": "admin",
    "device_type":"fortinet"
}


## connect to the fortinet and till the loop is not finished it will hold the connection
net_connect = Netmiko(**fortinethost) #using ** to define dictionary object

with open('../misc/ips.csv') as csv_file:
    ip_details = DictReader(csv_file)

    for ip in ip_details:
        time.sleep(0.5) # optional: setting a delay time in order to prevent throttling
        print(f"### configuring for {ip['Name']} with the IP {ip['IP']} ### ") #use one quotation inside formatted-string that is wrapped around double-quotation
        config_commands = [
                "config firewall address",
                f"edit {ip['Name']}",
                "set type ipmask",
                f"set subnet  {ip['IP']}/32",
                "end"]
        sentConfigs = net_connect.send_config_set(config_commands)        
        print(f"done with logs: {sentConfigs}")

