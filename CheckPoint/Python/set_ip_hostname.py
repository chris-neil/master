import paramiko
import time

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

hostname="192.168.182.250"   
username = "admin" #input("Enter username:")
password = "Admin123" #input("Enter password:")
ipaddress="192.168.182.13"

#ssh.connect(hostname=hostname,port=22,username=username,password=password)
#ssh.exec_command("set interface eth0 ipv4-address " + ipaddress + " mask-length 24")
#ssh.close

#time.sleep(0.5)

ssh.connect(hostname=ipaddress,port=22,username=username,password=password)
ssh.exec_command("set hostname vsx03")
ssh.exec_command("save config")
ssh.close

