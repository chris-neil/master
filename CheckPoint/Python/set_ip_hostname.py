from pexpect import pxssh
s = pxssh.pxssh()
username = input("Enter username:")
password = input("Enter password:")
if not s.login ('192.168.182.250', username, password):
    print("SSH session failed on login.")
    print(str(s))
else:
    print("SSH session login successful")
    s.sendline ('set hostname vsx03')
    s.sendline ('save config')
    s.logout()