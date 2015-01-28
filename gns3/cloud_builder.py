# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
"""

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import QThread

import ast
import logging
import os
import time
from .cloud.utils import ssh_client
from .cloud.exceptions import KeyPairExists

from .servers import Servers
from .topology import Topology


log = logging.getLogger(__name__)


class CloudBuilder(QThread):

    """
    """
    # Notify with progress amount and instance_id
    progressUpdate = pyqtSignal(object, str)

    # Notify with current state and instance_id
    stateChange = pyqtSignal(object, str)

    # Notify when instance is ready with instance_id
    buildComplete = pyqtSignal(str)

    # Notify when the instance has been created with instance and keypair
    instanceCreated = pyqtSignal(object, object)

    # Notify when the public ip is available with ip and instance_id
    instanceHasIP = pyqtSignal(str, str)

    # Notify when instance id exists with builder and instance_id
    instanceIdExists = pyqtSignal(object, str)

    def __init__(self, parent, cloud_provider, ca_dir):
        super(QThread, self).__init__(parent)
        # Store our parent so it can be passed to threads we spawn.
        self._parent = parent
        self._provider = cloud_provider
        self._ca_dir = ca_dir
        self._start_at_create = False
        self._start_at_setup = False
        self._instance = None

    def startAtCreate(self, instance_name, flavor_id, image_id):
        self._start_at_create = True
        self._instance_name = instance_name
        self._flavor_id = flavor_id
        self._image_id = image_id

    def startAtSetup(self, instance, keypair):
        self._start_at_setup = True
        self._instance = instance
        self._key_pair = keypair

    def run(self):
        try:
            log.debug('CloudBuilder.run')
            if self._start_at_create:
                log.debug('CloudBuilder._start_at_create')
                self._createInstance(self._provider, self._instance_name, self._flavor_id,
                                     self._image_id)
                log.debug('got here 3')
            if self._start_at_setup:
                log.debug('CloudBuilder start at setup')
                self._instanceCreated(self._instance, self._key_pair)
        except Exception:
            log.exception("CloudBuilder trapped an exception:")
            log.error('CloudBuilder stopped in error state.')

    def _createInstance(self, provider, name, flavor_id, image_id):
        log.debug("Creating cloud keypair with name {}".format(name))
        key_pair = None
        while key_pair is None:
            try:
                key_pair = provider.create_key_pair(name)
            except KeyPairExists:
                log.debug("Deleting old key pair with name {}.".format(name))
                self._provider.delete_key_pair_by_name(name)
            except Exception as e:
                log.debug("create_key_pair exception {}".format(e))

        log.debug("Creating cloud server with name {}".format(name))
        instance = None
        while instance is None:
            try:
                instance = self._provider.create_instance(name, flavor_id, image_id, key_pair)
            except Exception as e:
                log.debug("create_instance exception {}".format(e))
        log.debug("Cloud server {} created".format(name))
        self._instanceCreated(instance, key_pair)

    def _instanceCreated(self, instance, key_pair):
        log.debug('CloudBuilder._instanceCreated {}'.format(instance.id))
        self._instance = instance
        self._instance_id = instance.id
        self._key_pair = key_pair
        self.instanceIdExists.emit(self, instance.id)
        self.instanceCreated.emit(instance, key_pair)
        self._waitForPublicIP()

    def _waitForPublicIP(self):
        public_ip = None
        while public_ip is None:
            time.sleep(10)
            try:
                instance = self._provider.get_instance(self._instance)
                # Look for public ip address
                for ip in instance.public_ips:
                    # Don't use the ipv6 address
                    if ':' not in ip:
                        public_ip = ip
                        break
            except Exception as e:
                log.debug('list_instances error: {}'.format(e))

        # updated info, keep it.
        self._instance = instance
        self._public_ip = public_ip
        self.instanceHasIP.emit(self._public_ip, self._instance.id)
        time.sleep(60)
        self._startGNS3Server(1800)

    def _startGNS3Server(self, dead_time):
        commands = '''
DEBIAN_FRONTEND=noninteractive dpkg --configure -a
DEBIAN_FRONTEND=noninteractive dpkg --add-architecture i386
DEBIAN_FRONTEND=noninteractive apt-get -y update
DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confnew" --force-yes -fuy dist-upgrade
DEBIAN_FRONTEND=noninteractive apt-get -y install git python3-setuptools python3-netifaces python3-pip python3-zmq dynamips qemu-system
DEBIAN_FRONTEND=noninteractive apt-get -y install libc6:i386 libstdc++6:i386 libssl1.0.0:i386
ln -s /lib/i386-linux-gnu/libcrypto.so.1.0.0 /lib/i386-linux-gnu/libcrypto.so.4
mkdir -p /opt/gns3
cd /opt/gns3; git clone https://github.com/planctechnologies/gns3-server.git
cd /opt/gns3/gns3-server; git checkout dev; git pull
cd /opt/gns3/gns3-server; pip3 install -r dev-requirements.txt
cd /opt/gns3/gns3-server; python3 ./setup.py install
ln -sf /usr/bin/dynamips /usr/local/bin/dynamips
wget 'https://github.com/GNS3/iouyap/releases/download/0.95/iouyap.tar.gz'
tar xzf iouyap.tar.gz -C /usr/local/bin
python -c 'import struct; open("/etc/hostid", "w").write(struct.pack("i", 00000000))'
hostname gns3-iouvm # set hostname for iou
wget 'http://downloads.sourceforge.net/project/vpcs/0.6/vpcs_0.6_Linux64'
cp vpcs_0.6_Linux64 /usr/local/bin/vpcs
chmod a+x /usr/local/bin/vpcs
killall python3 gns3server gns3dms
'''

        def exec_command(client, cmd, wait_time=-1):

            cmd += '; exit $?'

            stdout_data = b''
            stderr_data = b''

            log.debug('cmd: {}'.format(cmd))
            # Send the command (non-blocking)
            stdin, stdout, stderr = client.exec_command(cmd)

            # Wait for the command to terminate
            wait = int(wait_time)
            while not stdout.channel.exit_status_ready() and wait != 0:
                time.sleep(1)
                wait -= 1

            stdout_data = stdout.read()
            stderr_data = stderr.read()
            log.debug('exit status: {}'.format(stdout.channel.exit_status))
            log.debug('stdout: {}'.format(stdout_data.decode('utf-8')))
            log.debug('stderr: {}'.format(stderr_data.decode('utf-8')))
            return stdout_data, stderr_data

        # We might be attempting a connection before the instance is fully booted, so retry
        # when the ssh connection fails.
        ssh_connected = False
        response = None
        while not ssh_connected:
            with ssh_client(self._public_ip, self._key_pair.private_key) as client:
                if client is None:
                    time.sleep(1)
                    continue
                ssh_connected = True

                for cmd in [l for l in commands.splitlines() if l.strip()]:
                    exec_command(client, cmd)

                data = {
                    'instance_id': self._instance_id,
                    'cloud_user_name': self._provider.username,
                    'cloud_api_key': self._provider.api_key,
                    'cloud_region': self._provider.region,
                    'dead_time': dead_time,
                }
                # TODO: Properly escape the data portion of the command line
                start_cmd = '/usr/bin/python3 /opt/gns3/gns3-server/gns3server/start_server.py -d -v --ip={} --data="{}" 2>/tmp/gns3-stderr.log'.format(self._public_ip, data)
                stdout, stderr = exec_command(client, start_cmd, wait_time=15)
                response = stdout.decode('utf-8')

        log.debug(response)
        data = ast.literal_eval(response)
        # TODO: have the server return the port it is running on
        port = 8000

        username = data['WEB_USERNAME']
        password = data['WEB_PASSWORD']

        ssl_cert = ''.join(data['SSL_CRT'])
        ca_filename = 'cloud_server_{}.crt'.format(self._public_ip)
        ca_dir = self._ca_dir
        ca_file = os.path.join(ca_dir, ca_filename)
        try:
            os.makedirs(ca_dir)
        except FileExistsError:
            pass
        with open(ca_file, 'wb') as ca_fh:
            ca_fh.write(ssl_cert.encode('utf-8'))

        topology = Topology.instance()
        top_instance = topology.getInstance(self._instance_id)
        top_instance.set_later_attributes(self._public_ip, port, ssl_cert, ca_file)

        servers = Servers.instance()
        server = servers.getCloudServer(self._public_ip, port, ca_file, username, password,
                                        self._key_pair.private_key, self._instance_id)
        servers.save()
        log.debug('Cloud server gns3server started.')
        self.buildComplete.emit(self._instance_id)
