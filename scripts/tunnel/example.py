import os
import sys
import time

import tunnel

my_key = open('/home/michaelgale/.ssh/id_rsa', 'r')
print("SSH Key: %s" % (my_key))

t = tunnel.Tunnel('192.168.1.3', 22, username='michael', client_key=my_key)
t1 = t.add_endpoint('127.0.0.1',25)
time.sleep(1)
t2 = t.add_endpoint('127.0.0.1',80)
time.sleep(1)
t3 = t.add_endpoint('127.0.0.1',8080)
time.sleep(1)
t4 = t.add_endpoint('192.168.3.2',80)
time.sleep(1)
t.remove_endpoint(t3)
print(t.list_endpoints())
t.disconnect()

print("Waiting at sleep")
time.sleep(600)