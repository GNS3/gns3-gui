from contextlib import contextmanager
import io
import json
from socket import error as socket_error
import logging
import os
import tempfile
import time
import zipfile

from ..qt import QtCore

from .exceptions import KeyPairExists
from .rackspace_ctrl import get_provider
from ..topology import Topology
from ..servers import Servers

log = logging.getLogger(__name__)


@contextmanager
def ssh_client(host, key_string):
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
        log.debug("SSH connection socket error to {}: {}".format(host, e))
        yield None
    except Exception as e:
        log.debug("SSH connection error to {}: {}".format(host, e))
        yield None
    finally:
        client.close()


class ListInstancesThread(QtCore.QThread):
    """
    Helper class to retrieve data from the provider in a separate thread,
    avoid freezing the gui
    """
    instancesReady = QtCore.pyqtSignal(object)

    def __init__(self, parent, provider):
        super().__init__(parent)
        self._provider = provider

    def run(self):
        try:
            instances = self._provider.list_instances()
            log.debug('Instance list: {}'.format([(i.name, i.state) for i in instances]))
            self.instancesReady.emit(instances)
        except Exception as e:
            log.info('list_instances error: {}'.format(e))


class CreateInstanceThread(QtCore.QThread):
    """
    Helper class to create instances in a separate thread
    """
    instanceCreated = QtCore.pyqtSignal(object, object)

    def __init__(self, parent, provider, name, flavor_id, image_id):
        super().__init__(parent)
        self._provider = provider
        self._name = name
        self._flavor_id = flavor_id
        self._image_id = image_id

    def run(self):
        log.debug("Creating cloud keypair with name {}".format(self._name))
        try:
            k = self._provider.create_key_pair(self._name)
        except KeyPairExists:
            log.debug("Cloud keypair with name {} exists.  Recreating.".format(self._name))
            # delete keypairs if they already exist
            self._provider.delete_key_pair_by_name(self._name)
            k = self._provider.create_key_pair(self._name)

        log.debug("Creating cloud server with name {}".format(self._name))
        i = self._provider.create_instance(self._name, self._flavor_id, self._image_id, k)
        log.debug("Cloud server {} created".format(self._name))

        self.instanceCreated.emit(i, k)


class DeleteInstanceThread(QtCore.QThread):
    """
    Helper class to remove an instance in a separate thread
    """
    instanceDeleted = QtCore.pyqtSignal(object)

    def __init__(self, parent, provider, instance):
        super().__init__(parent)
        self._provider = provider
        self._instance = instance

    def run(self):
        if self._provider.delete_instance(self._instance):
            self.instanceDeleted.emit(self._instance)


class StartGNS3ServerThread(QtCore.QThread):
    """
    Perform an SSH connection to the instances in a separate thread,
    outside the GUI event loop, and start GNS3 server
    """
    gns3server_started = QtCore.pyqtSignal(str, str, str)

# This is for testing without pushing to github
#     commands = '''
# DEBIAN_FRONTEND=noninteractive dpkg --configure -a
# DEBIAN_FRONTEND=noninteractive dpkg --add-architecture i386
# DEBIAN_FRONTEND=noninteractive apt-get -y update
# DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confnew" --force-yes -fuy dist-upgrade
# DEBIAN_FRONTEND=noninteractive apt-get -y install git python3-setuptools python3-netifaces python3-pip python3-zmq dynamips qemu-system
# DEBIAN_FRONTEND=noninteractive apt-get -y install libc6:i386 libstdc++6:i386 libssl1.0.0:i386
# ln -s /lib/i386-linux-gnu/libcrypto.so.1.0.0 /lib/i386-linux-gnu/libcrypto.so.4
# mkdir -p /opt/gns3
# tar xzf /tmp/gns3-server.tgz -C /opt/gns3
# cd /opt/gns3/gns3-server; pip3 install -r dev-requirements.txt
# cd /opt/gns3/gns3-server; python3 ./setup.py install
# ln -sf /usr/bin/dynamips /usr/local/bin/dynamips
# wget 'https://github.com/GNS3/iouyap/releases/download/0.95/iouyap.tar.gz'
# python -c 'import struct; open("/etc/hostid", "w").write(struct.pack("i", 00000000))'
# hostname gns3-iouvm
# tar xzf iouyap.tar.gz -C /usr/local/bin
# killall python3 gns3server gns3dms
# '''

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
wget 'https://github.com/GNS3/iouyap/releases/download/0.95/iouyap-64-bit.tar.gz'
tar xzf iouyap-64-bit.tar.gz -C /usr/local/bin
python -c 'import struct; open("/etc/hostid", "w").write(struct.pack("i", 00000000))'
hostname gns3-iouvm # set hostname for iou
wget -O vpcs http://sourceforge.net/projects/vpcs/files/0.6/vpcs_0.6_Linux64/download
cp vpcs /usr/local/bin/vpcs
chmod a+x /usr/local/bin/vpcs
killall python3 gns3server gns3dms
'''

    def __init__(self, parent, host, private_key_string, server_id, username, api_key, region, dead_time):
        super().__init__(parent)
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

        stdout_data = stdout.read()
        stderr_data = stderr.read()
        log.debug('exit status: {}'.format(stdout.channel.exit_status))
        log.debug('stdout: {}'.format(stdout_data.decode('utf-8')))
        log.debug('stderr: {}'.format(stderr_data.decode('utf-8')))
        return stdout_data, stderr_data


    def run(self):
        # We might be attempting a connection before the instance is fully booted, so retry
        # when the ssh connection fails.
        ssh_connected = False
        while not ssh_connected:
            with ssh_client(self._host, self._private_key_string) as client:
                if client is None:
                    time.sleep(1)
                    continue
                ssh_connected = True

                # This is for testing without pushing to github
                # os.system('rm -rf /tmp/gns3-server')
                # os.system('cp -a /Users/jseutter/projects/gns3-server /tmp/gns3-server')
                # os.system('cd /tmp; tar czf /tmp/gns3-server.tgz gns3-server')
                # sftp = client.open_sftp()
                # sftp.put('/tmp/gns3-server.tgz', '/tmp/gns3-server.tgz')
                # sftp.close()

                for cmd in [l for l in self.commands.splitlines() if l.strip()]:
                    self.exec_command(client, cmd)

                data = {
                    'instance_id': self._server_id,
                    'cloud_user_name': self._username,
                    'cloud_api_key': self._api_key,
                    'cloud_region': self._region,
                    'dead_time': self._dead_time,
                }
                # TODO: Properly escape the data portion of the command line
                start_cmd = '/usr/bin/python3 /opt/gns3/gns3-server/gns3server/start_server.py -d -v --ip={} --data="{}" 2>/tmp/gns3-stderr.log'.format(self._host, data)
                stdout, stderr = self.exec_command(client, start_cmd, wait_time=15)
                response = stdout.decode('utf-8')
                self.gns3server_started.emit(str(self._server_id), str(self._host), str(response))


class WSConnectThread(QtCore.QThread):
    """
    Establish a websocket connection with the remote gns3server
    instance. Run outside the GUI event loop.
    """
    established = QtCore.pyqtSignal(str)

    def __init__(self, parent, provider, server_id, host, port, ca_file,
                 auth_user, auth_password, ssh_pkey, instance_id):
        super().__init__(parent)
        self._provider = provider
        self._server_id = server_id
        self._host = host
        self._port = port
        self._ca_file = ca_file
        self._auth_user = auth_user
        self._auth_password = auth_password
        self._ssh_pkey = ssh_pkey
        self._instance_id = instance_id

    def run(self):
        """
        Establish a websocket connection to gns3server on the cloud instance.
        """

        log.debug('WSConnectThread.run() begin')
        servers = Servers.instance()
        server = servers.getCloudServer(self._host, self._port, self._ca_file,
                                        self._auth_user, self._auth_password, self._ssh_pkey,
                                        self._instance_id)
        log.debug('after getCloudServer call. {}'.format(server))
        self.established.emit(str(self._server_id))

        log.debug('WSConnectThread.run() end')
        # emit signal on success
        self.established.emit(self._server_id)


class UploadProjectThread(QtCore.QThread):
    """
    Zip and Upload project to the cloud
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    completed = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(int)

    def __init__(self, parent, cloud_settings, project_path, images_path):
        super().__init__(parent)
        self.cloud_settings = cloud_settings
        self.project_path = project_path
        self.images_path = images_path

    def run(self):
        try:
            log.info("Exporting project to cloud")
            self.update.emit(0)

            zipped_project_file = self.zip_project_dir()

            self.update.emit(10)  # update progress to 10%

            provider = get_provider(self.cloud_settings)
            provider.upload_file(zipped_project_file, 'projects/' + os.path.basename(zipped_project_file))

            self.update.emit(20)  # update progress to 20%

            topology = Topology.instance()
            images = set([node.settings()["image"] for node in topology.nodes() if 'image' in node.settings()])

            for i, image in enumerate(images):
                provider.upload_file(image, 'images/' + os.path.relpath(image, self.images_path))
                self.update.emit(20 + (float(i) / len(images) * 80))

            self.completed.emit()
        except Exception as e:
            log.exception("Error exporting project to cloud")
            self.error.emit("Error exporting project: {}".format(e), True)

    def zip_project_dir(self):
        """
        Zips project files
        :return: path to zipped project file
        """
        project_name = os.path.basename(self.project_path)
        output_filename = os.path.join(tempfile.gettempdir(), project_name + ".zip")
        project_dir = os.path.dirname(self.project_path)
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


class UploadFilesThread(QtCore.QThread):
    """
    Uploads files to cloud files

    :param cloud_settings:
    :param files_to_upload: list of tuples of (file path, file name to save in cloud)
    """

    error = QtCore.pyqtSignal(str, bool)
    completed = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(int)

    def __init__(self, parent, cloud_settings, files_to_upload):
        super().__init__(parent)
        self._cloud_settings = cloud_settings
        self._files_to_upload = files_to_upload

    def run(self):
        self.update.emit(0)

        try:
            for i, file_to_upload in enumerate(self._files_to_upload):
                provider = get_provider(self._cloud_settings)

                log.debug('Uploading image {} to cloud as {}'.format(file_to_upload[0], file_to_upload[1]))
                provider.upload_file(file_to_upload[0], file_to_upload[1])

                self.update.emit((i+1) * 100 / len(self._files_to_upload))
                log.debug('Uploading image completed')
        except Exception as e:
            log.exception("Error uploading images to cloud")
            self.error.emit("Error uploading images: {}".format(e), True)

        self.completed.emit()

    def stop(self):
        self.quit()


class DownloadProjectThread(QtCore.QThread):
    """
    Downloads project from cloud storage
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    completed = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(int)

    def __init__(self, parent, cloud_project_file_name, project_dest_path, images_dest_path, cloud_settings):
        super().__init__(parent)
        self.project_name = cloud_project_file_name
        self.project_dest_path = project_dest_path
        self.images_dest_path = images_dest_path
        self.cloud_settings = cloud_settings

    def run(self):
        try:
            self.update.emit(0)
            provider = get_provider(self.cloud_settings)
            zip_file = provider.download_file(self.project_name)
            zip_file = zipfile.ZipFile(zip_file, mode='r')
            zip_file.extractall(self.project_dest_path)
            zip_file.close()
            project_name = zip_file.namelist()[0].strip('/')

            self.update.emit(20)

            with open(os.path.join(self.project_dest_path, project_name, project_name + '.gns3'), 'r') as f:
                project_settings = json.loads(f.read())

                images = set()
                for node in project_settings["topology"].get("nodes", []):
                    if "properties" in node and "image" in node["properties"]:
                        images.add(node["properties"]["image"])

            image_names_in_cloud = provider.find_storage_image_names(images)

            for i, image in enumerate(images):
                dest_path = os.path.join(self.images_dest_path, *image_names_in_cloud[image].split('/')[1:])

                if not os.path.exists(os.path.dirname(dest_path)):
                    os.makedirs(os.path.dirname(dest_path))

                provider.download_file(image_names_in_cloud[image], dest_path)
                self.update.emit(20 + (float(i) / len(images) * 80))

            self.completed.emit()
        except Exception as e:
            log.exception("Error importing project from cloud")
            self.error.emit("Error importing project: {}".format(e), True)

    def stop(self):
        self.quit()

class DownloadImagesThread(QtCore.QThread):
    """
    Downloads multiple files from cloud files
    """

    error = QtCore.pyqtSignal(str, bool)
    completed = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(int)

    def __init__(self, cloud_settings, images_dest_path, image_names):
        super().__init__()
        self._cloud_settings = cloud_settings
        self._images_dest_path = images_dest_path
        self._image_names = image_names

    def run(self):
        self.update.emit(0)
        try:
            provider = get_provider(self._cloud_settings)
            image_names_in_cloud = provider.find_storage_image_names(self._image_names)

            for i, image in enumerate(self._image_names):
                dest_path = os.path.join(self._images_dest_path, *image_names_in_cloud[image].split('/')[1:])

                if not os.path.exists(os.path.dirname(dest_path)):
                    os.makedirs(os.path.dirname(dest_path))

                provider.download_file(image_names_in_cloud[image], dest_path)

                self.update.emit(i * 100 / len(self._image_names))

            self.completed.emit()
        except Exception as e:
            log.exception("Error importing project from cloud")
            self.error.emit("Error importing project: {}".format(e), True)

    def stop(self):
        self.quit()


class DeleteProjectThread(QtCore.QThread):
    """
    Deletes project from cloud storage
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    completed = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(int)

    def __init__(self, parent, project_file_name, cloud_settings):
        super().__init__(parent)
        self.project_file_name = project_file_name
        self.cloud_settings = cloud_settings

    def run(self):
        try:
            provider = get_provider(self.cloud_settings)
            provider.delete_file(self.project_file_name)
            self.completed.emit()
        except Exception as e:
            log.exception("Error deleting project")
            self.error.emit("Error deleting project: {}".format(e), True)

    def stop(self):
        pass


def get_cloud_projects(cloud_settings):
    provider = get_provider(cloud_settings)
    return provider.list_projects()
