import os
import sys
import time
import getpass
import tunnel

my_home = os.path.expanduser("~/.ssh")
my_key_file = "%s/id_rsa" % (my_home)

my_key = open(my_key_file, 'r')
print("Using ssh key: %s" % (my_key))

username = getpass.getuser()

t = tunnel.Tunnel('192.168.1.3', 22, username=username, client_key=my_key)

t1 = t.add_endpoint('127.0.0.1', 25)
t2 = t.add_endpoint('127.0.0.1', 80)
t3 = t.add_endpoint('127.0.0.1', 8080)
t4 = t.add_endpoint('192.168.3.2', 80)

t.remove_endpoint(t3)

print(t.list_endpoints())

t.disconnect()
