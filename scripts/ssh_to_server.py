"""
This script can be used to ssh to a cloud server started by GNS3.  It copies
the ssh keys for a server to a temp file on disk and starts ssh using the
keys.

Right now it only connects to the first cloud server listed in the config
file.
"""

import os
import sys

from PyQt4 import QtCore, QtGui


if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
    QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)

app = QtGui.QApplication([])
app.setOrganizationName("GNS3")
app.setOrganizationDomain("gns3.net")
app.setApplicationName("GNS3")

settings = QtCore.QSettings()

print('Reading config from {}'.format(QtCore.QSettings().fileName()))

def read_cloud_settings():
    settings = QtCore.QSettings()
    settings.beginGroup("CloudInstances")

    # Load the instances
    size = settings.beginReadArray("cloud_instance")
    for index in range(0, size):
        settings.setArrayIndex(index)
        name = settings.value('name')
        host = settings.value('host')
        private_key = settings.value('private_key')
        public_key = settings.value('public_key')

        # For now, just use the first system.
        return name, host, private_key, public_key
    raise Exception("Could not find any servers")
    

name, host, private_key, public_key = read_cloud_settings()

print(name)
print(host)
print(private_key)
print(public_key)


open('/tmp/id_rsa.pub', 'w').write(public_key)
open('/tmp/id_rsa', 'w').write(private_key)
os.system('chmod 0600 /tmp/id_rsa')

cmd = 'ssh -i /tmp/id_rsa root@{}'.format(host) 
os.system(cmd)
