import paramiko

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

hostname="192.168.182.13"   
username = "admin" #input("Enter username:")
password = "Admin123" #input("Enter password:")
cluster_node = "vsx03"

ssh.connect(hostname=hostname,port=22,username=username,password=password)
ssh.exec_command("add cluster member method hostname identifier " + cluster_node + " site-id 1 format json")
ssh.close