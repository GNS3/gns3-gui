from contextlib import contextmanager
import io
from socket import error as socket_error
import logging
import os
import select
import tempfile
import time
import zipfile

from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from PyQt4.QtCore import pyqtSignal

from .rackspace_ctrl import RackspaceCtrl
from ..topology import Topology
from ..servers import Servers

log = logging.getLogger(__name__)


@contextmanager
def ssh_client(host, key_string, retry=False):
    """
    Context manager wrapping a SSHClient instance: the client connects on
    enter and close the connection on exit
    """

    import paramiko
    class AllowAndForgetPolicy(paramiko.MissingHostKeyPolicy):
        """
        Custom policy for server host keys: we simply accept the key
        the server sent to us without storing it.
        """
        def missing_host_key(self, *args, **kwargs):
            """
            According to MissingHostKeyPolicy protocol, to accept
            the key, simply return.
            """
            return

    client = paramiko.SSHClient()
    try:
        f_key = io.StringIO(key_string)
        key = paramiko.RSAKey.from_private_key(f_key)
        client.set_missing_host_key_policy(AllowAndForgetPolicy())
        client.connect(hostname=host, username="root", pkey=key)
        yield client
    except socket_error as e:
        log.error("SSH connection error to {}: {}".format(host, e))
        yield None
    finally:
        client.close()


def get_provider(cloud_settings):
    """
    Utility function to retrieve a cloud provider instance already authenticated and with the
    region set

    :param cloud_settings: cloud settings dictionary
    :return: a provider instance or None on errors
    """
    try:
        username = cloud_settings['cloud_user_name']
        apikey = cloud_settings['cloud_api_key']
        region = cloud_settings['cloud_region']
        ias_url = cloud_settings['gns3_ias_url']
    except KeyError as e:
        log.error("Unable to create cloud provider: {}".format(e))
        return

    provider = RackspaceCtrl(username, apikey, ias_url)

    if not provider.authenticate():
        log.error("Authentication failed for cloud provider")
        return

    if not region:
        region = provider.list_regions().values()[0]

    if not provider.set_region(region):
        log.error("Unable to set cloud provider region")
        return

    return provider


class ListInstancesThread(QThread):
    """
    Helper class to retrieve data from the provider in a separate thread,
    avoid freezing the gui
    """
    instancesReady = pyqtSignal(object)

    def __init__(self, parent, provider):
        super(QThread, self).__init__(parent)
        self._provider = provider

    def run(self):
        try:
            instances = self._provider.list_instances()
            log.debug('Instance list:')
            for instance in instances:
                log.debug('  name={}, state={}'.format(instance.name, instance.state))
            self.instancesReady.emit(instances)
        except Exception as e:
            log.info('list_instances error: {}'.format(e))


class CreateInstanceThread(QThread):
    """
    Helper class to create instances in a separate thread
    """
    instanceCreated = pyqtSignal(object, object)

    def __init__(self, parent, provider, name, flavor_id, image_id):
        super(QThread, self).__init__(parent)
        self._provider = provider
        self._name = name
        self._flavor_id = flavor_id
        self._image_id = image_id

    def run(self):
        k = self._provider.create_key_pair(self._name)
        i = self._provider.create_instance(self._name, self._flavor_id, self._image_id, k)
        self.instanceCreated.emit(i, k)


class DeleteInstanceThread(QThread):
    """
    Helper class to remove an instance in a separate thread
    """
    instanceDeleted = pyqtSignal(object)

    def __init__(self, parent, provider, instance):
        super(QThread, self).__init__(parent)
        self._provider = provider
        self._instance = instance

    def run(self):
        if self._provider.delete_instance(self._instance):
            self.instanceDeleted.emit(self._instance)


class StartGNS3ServerThread(QThread):
    """
    Perform an SSH connection to the instances in a separate thread,
    outside the GUI event loop, and start GNS3 server
    """
    gns3server_started = pyqtSignal(str, str, str)

#     # Note: The htop package is for troubleshooting.  It can safely be removed.
#     commands = '''
# echo 'hello world'
# DEBIAN_FRONTEND=noninteractive apt-get -y update
# DEBIAN_FRONTEND=noninteractive apt-get -y install htop
# DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confnew" --force-yes -fuy dist-upgrade
# DEBIAN_FRONTEND=noninteractive apt-get -y install git python3-setuptools python3-netifaces python3-pip python3-zmq
# mkdir -p /opt/gns3
# tar xzf /tmp/gns3-server.tgz -C /opt/gns3
# cd /opt/gns3/gns3-server; pip3 install -r dev-requirements.txt
# cd /opt/gns3/gns3-server; python3 ./setup.py install
# killall gns3server gns3dms
# '''

    commands = '''
echo 'hello world'
DEBIAN_FRONTEND=noninteractive dpkg --configure -a
DEBIAN_FRONTEND=noninteractive apt-get -y update
DEBIAN_FRONTEND=noninteractive apt-get -y install htop
DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confnew" --force-yes -fuy dist-upgrade
DEBIAN_FRONTEND=noninteractive apt-get -y install git python3-setuptools python3-netifaces python3-pip python3-zmq
mkdir -p /opt/gns3
cd /opt/gns3; git clone https://github.com/planctechnologies/gns3-server.git
cd /opt/gns3/gns3-server; git checkout dev
cd /opt/gns3/gns3-server; pip3 install -r dev-requirements.txt
cd /opt/gns3/gns3-server; python3 ./setup.py install
killall gns3server gns3dms
'''

    def __init__(self, parent, host, private_key_string, server_id, username, api_key, region, dead_time):
        super(QThread, self).__init__(parent)
        self._host = host
        self._private_key_string = private_key_string
        self._server_id = server_id
        self._username = username
        self._api_key = api_key
        self._region = region
        self._dead_time = dead_time

    def exec_command(self, client, cmd, wait_time=-1):

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

        # stdout_data += stdout.channel.recv()
        # stderr_data += stderr.channel.recv()
        stdout_data = stdout.read()
        stderr_data = stderr.read()
        log.debug('exit status: {}'.format(stdout.channel.exit_status))
        log.debug('stdout: {}'.format(stdout_data.decode('utf-8')))
        log.debug('stderr: {}'.format(stderr_data.decode('utf-8')))
        return stdout_data, stderr_data


    def run(self):
        # Uncomment this at the same time as the commands above to test without having to push
        # changes to github.
        # os.system('rm -rf /tmp/gns3-server')
        # os.system('cp -a /Users/jseutter/projects/gns3-server-newinstancerework /tmp/gns3-server')
        # os.system('cd /tmp; tar czf /tmp/gns3-server.tgz gns3-server')
        # os.system('scp /tmp/gns3-server.tgz root@{}:/tmp/'.format(self._host))

        # We might be attempting a connection before the instance is fully booted, so retry
        # when the ssh connection fails.
        ssh_connected = False
        while not ssh_connected:
            with ssh_client(self._host, self._private_key_string) as client:
                if client is None:
                    time.sleep(1)
                    continue
                ssh_connected = True

                for cmd in [l for l in self.commands.splitlines() if l.strip()]:
                    self.exec_command(client, cmd)

                data = {
                    'instance_id': self._server_id,
                    'cloud_user_name': self._username,
                    'cloud_api_key': self._api_key,
                    'region': self._region,
                    'dead_time': self._dead_time,
                }
                # TODO: Properly escape the data portion of the command line
                start_cmd = '/usr/bin/python3 /opt/gns3/gns3-server/gns3server/start_server.py -d -v --data="{}" 2> /tmp/gns3-stderr.log'.format(data)
                stdout, stderr = self.exec_command(client, start_cmd, wait_time=15)
                response = stdout.decode('utf-8')
                self.gns3server_started.emit(str(self._server_id), str(self._host), str(response))


class WSConnectThread(QThread):
    """
    Establish a websocket connection with the remote gns3server
    instance. Run outside the GUI event loop.
    """
    established = pyqtSignal(str)

    def __init__(self, parent, provider, server_id, host, port, ca_file):
        super(QThread, self).__init__(parent)
        self._provider = provider
        self._server_id = server_id
        self._host = host
        self._port = port
        self._ca_file = ca_file

    def run(self):
        """
        Establish a websocket connection to gns3server on the cloud instance.
        """

        log.debug('WSConnectThread.run() begin')
        servers = Servers.instance()
        server = servers.getCloudServer(self._host, self._port, self._ca_file)
        log.debug('after getCloudServer call. {}'.format(server))
        self.established.emit(str(self._server_id))

        log.debug('WSConnectThread.run() end')
        # emit signal on success
        self.established.emit(self._server_id)


class UploadProjectThread(QThread):
    """
    Zip and Upload project to the cloud
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    completed = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(int)

    def __init__(self, project_settings, cloud_settings):
        super().__init__()
        self.project_settings = project_settings
        self.cloud_settings = cloud_settings

    def run(self):
        try:
            log.info("Exporting project to cloud")
            self.update.emit(0)

            zipped_project_file = self.zip_project_dir()

            self.update.emit(10)  # update progress to 10%

            provider = get_provider(self.cloud_settings)
            provider.upload_file(zipped_project_file, 'projects')

            self.update.emit(20)  # update progress to 20%

            topology = Topology.instance()
            images = set([node.settings()["image"] for node in topology.nodes() if 'image' in node.settings()])

            for i, image in enumerate(images):
                provider.upload_file(image, 'images')
                self.update.emit(20 + (float(i) / len(images) * 80))

            self.completed.emit()
        except Exception as e:
            log.exception("Error exporting project to cloud")
            self.error.emit("Error exporting project {}".format(str(e)), True)

    def zip_project_dir(self):
        """
        Zips project files
        :return: path to zipped project file
        """
        project_name = os.path.basename(self.project_settings["project_path"])
        output_filename = os.path.join(tempfile.gettempdir(), project_name + ".zip")
        project_dir = os.path.dirname(self.project_settings["project_path"])
        relroot = os.path.abspath(os.path.join(project_dir, os.pardir))
        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(project_dir):
                # add directory (needed for empty dirs)
                zip_file.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename) and not self._should_exclude(filename):  # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip_file.write(filename, arcname)

        return output_filename

    def _should_exclude(self, filename):
        """
        Returns True if file should be excluded from zip of project files
        :param filename:
        :return: True if file should be excluded from zip, False otherwise
        """
        return filename.endswith('.ghost')

    def stop(self):
        self.quit()
