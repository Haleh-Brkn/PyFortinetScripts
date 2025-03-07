# Basic Commands to Connect to Fortinet, Set an IP address and show full configuration on CLI
from netmiko import Netmiko

fortinet = {
    'host': '192.168.112.132',
    'username': 'admin',
    'password': 'admin',
    'device_type': 'fortinet'
}

net_connect= Netmiko(**fortinet)
print(net_connect.find_prompt())
command = 'show full-configuration'
#fullConfigs = net_connect.send_command(command)
#print(fullConfigs)
ip_policy_creator= [
    'config firewall address',
    'edit IP-180',
    'set type ipmask',
    'set subnet 192.168.0.180/32',
    'end']
set_config = net_connect.send_config_set(ip_policy_creator) # is an iterable containing all of the configuration commands. The commands will be executed one after the other.
print("done!")
print("Log is ",set_config )



