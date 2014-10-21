from contextlib import contextmanager
import io
import json
from socket import error as socket_error
import logging
import os
import zipfile
import tempfile

from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from PyQt4.QtCore import pyqtSignal
import paramiko

from .rackspace_ctrl import RackspaceCtrl
from ..topology import Topology
from ..servers import Servers


log = logging.getLogger(__name__)


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


@contextmanager
def ssh_client(host, key_string):
    """
    Context manager wrapping a SSHClient instance: the client connects on
    enter and close the connection on exit
    """
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

    def __init__(self, parent, host, private_key_string, server_id, username, api_key, region, dead_time):
        super(QThread, self).__init__(parent)
        self._host = host
        self._private_key_string = private_key_string
        self._server_id = server_id
        self._username = username
        self._api_key = api_key
        self._region = region
        self._dead_time = dead_time

    def run(self):
        with ssh_client(self._host, self._private_key_string) as client:
            if client is not None:
                data = {
                    'instance_id': self._server_id,
                    'cloud_user_name': self._username,
                    'cloud_api_key': self._api_key,
                    'region': self._region,
                    'dead_time': self._dead_time,
                }
                # TODO: Properly escape the data portion of the command line
                start_cmd = '/usr/bin/python3 /opt/gns3/gns3-server/gns3server/start_server.py -d -v --data="{}" 2>/tmp/gns3_stderr.log'.format(data)
                log.debug(start_cmd)
                stdin, stdout, stderr = client.exec_command(start_cmd)
                response = stdout.read().decode('ascii')
                log.debug('ssh response: {}'.format(response))

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

    def __init__(self, cloud_settings, project_path, images_path):
        super().__init__()
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
            self.error.emit("Error exporting project: {}".format(str(e)), True)

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


class DownloadProjectThread(QThread):
    """
    Downloads project from cloud storage
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    completed = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(int)

    def __init__(self, cloud_project_file_name, project_dest_path, images_dest_path, cloud_settings):
        super().__init__()
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
            self.error.emit("Error importing project: {}".format(str(e)), True)

    def stop(self):
        pass  # TODO cleanup and delete downloaded files
