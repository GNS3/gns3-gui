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

if not os.path.isfile(QtCore.QSettings().fileName()):
    print('Config file {} not found! Aborting...'.format(QtCore.QSettings().fileName()))
    sys.exit(1)

print('Reading config file {}...'.format(QtCore.QSettings().fileName()))

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

print('Instance name: {}'.format(name))
print('Host ip: {}'.format(host))

public_key_path = '/tmp/id_rsa.pub'
open(public_key_path, 'w').write(public_key)
private_key_path = '/tmp/id_rsa'
open(private_key_path, 'w').write(private_key)
cmd = 'chmod 0600 {}'.format(private_key_path)
os.system(cmd)
print('Per-instance ssh keys written to {}'.format(private_key_path))

cmd = 'ssh -i /tmp/id_rsa root@{}'.format(host)
print(cmd)
os.system(cmd)
