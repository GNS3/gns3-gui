import os
import sys
import tunnel_poc

my_key = open('/home/michaelgale/.ssh/id_rsa', 'r')
print("SSH Key: %s" % (my_key))

t = tunnel_poc.Tunnel('192.168.1.3', 22, username='michael', client_key=my_key)
t.add_destination('test1', '127.0.0.1',25)