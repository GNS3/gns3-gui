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
Base cloud controller class.

Base class for interacting with Cloud APIs to create and manage cloud
instances.

"""
from collections import namedtuple
import hashlib
import os
import logging
from io import StringIO, BytesIO

from libcloud.compute.base import NodeAuthSSHKey
from libcloud.storage.types import ContainerAlreadyExistsError, ContainerDoesNotExistError, ObjectDoesNotExistError

from .exceptions import ItemNotFound, KeyPairExists, MethodNotAllowed
from .exceptions import OverLimit, BadRequest, ServiceUnavailable
from .exceptions import Unauthorized, ApiError


KeyPair = namedtuple("KeyPair", ['name'], verbose=False)
log = logging.getLogger(__name__)


def parse_exception(exception):
    """
    Parse the exception to separate the HTTP status code from the text.

    Libcloud raises many exceptions of the form:
        Exception("<http status code> <http error> <reponse body>")

    in lieu of raising specific incident-based exceptions.

    """

    e_str = str(exception)

    try:
        status = int(e_str[0:3])
        error_text = e_str[3:]

    except ValueError:
        status = None
        error_text = e_str

    return status, error_text


class BaseCloudCtrl(object):

    """ Base class for interacting with a cloud provider API. """

    http_status_to_exception = {
        400: BadRequest,
        401: Unauthorized,
        404: ItemNotFound,
        405: MethodNotAllowed,
        413: OverLimit,
        500: ApiError,
        503: ServiceUnavailable
    }

    GNS3_CONTAINER_NAME = 'GNS3'

    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def _handle_exception(self, status, error_text, response_overrides=None):
        """ Raise an exception based on the HTTP status. """

        if response_overrides:
            if status in response_overrides:
                raise response_overrides[status](error_text)

        raise self.http_status_to_exception[status](error_text)

    def authenticate(self):
        """ Validate cloud account credentials.  Return boolean. """
        raise NotImplementedError

    def list_sizes(self):
        """ Return a list of NodeSize objects. """

        return self.driver.list_sizes()

    def list_flavors(self):
        """ Return an iterable of flavors """

        raise NotImplementedError

    def create_instance(self, name, size_id, image_id, keypair):
        """
        Create a new instance with the supplied attributes.

        Return a Node object.

        """
        try:
            image = self.get_image(image_id)
            if image is None:
                raise ItemNotFound("Image not found")

            size = self.driver.ex_get_size(size_id)

            args = {
                "name": name,
                "size": size,
                "image": image,
            }

            if keypair is not None:
                auth_key = NodeAuthSSHKey(keypair.public_key)
                args["auth"] = auth_key
                args["ex_keyname"] = name

            return self.driver.create_node(**args)

        except Exception as e:
            status, error_text = parse_exception(e)

            if status:
                self._handle_exception(status, error_text)
            else:
                log.error("create_instance method raised an exception: {}".format(e))
                log.error('image id {}'.format(image_id))

    def delete_instance(self, instance):
        """ Delete the specified instance.  Returns True or False. """

        try:
            return self.driver.destroy_node(instance)

        except Exception as e:

            status, error_text = parse_exception(e)

            if status:
                self._handle_exception(status, error_text)
            else:
                raise e

    def get_instance(self, instance):
        """ Return a Node object representing the requested instance. """

        for i in self.driver.list_nodes():
            if i.id == instance.id:
                return i

        raise ItemNotFound("Instance not found")

    def list_instances(self):
        """ Return a list of instances in the current region. """

        return self.driver.list_nodes()

    def create_key_pair(self, name):
        """ Create and return a new Key Pair. """

        response_overrides = {
            409: KeyPairExists
        }
        try:
            return self.driver.create_key_pair(name)

        except Exception as e:
            status, error_text = parse_exception(e)
            if status:
                self._handle_exception(status, error_text, response_overrides)
            else:
                raise e

    def delete_key_pair(self, keypair):
        """ Delete the keypair. Returns True or False. """

        try:
            return self.driver.delete_key_pair(keypair)

        except Exception as e:
            status, error_text = parse_exception(e)
            if status:
                self._handle_exception(status, error_text)
            else:
                raise e

    def delete_key_pair_by_name(self, keypair_name):
        """ Utility method to incapsulate boilerplate code """

        kp = KeyPair(name=keypair_name)
        return self.delete_key_pair(kp)

    def list_key_pairs(self):
        """ Return a list of Key Pairs. """

        return self.driver.list_key_pairs()

    def upload_file(self, file_path, cloud_object_name):
        """
        Uploads file to cloud storage (if it is not identical to a file already in cloud storage).
        :param file_path: path to file to upload
        :param cloud_object_name: name of file saved in cloud storage
        :return: True if file was uploaded, False if it was skipped because it already existed and was identical
        """
        try:
            gns3_container = self.storage_driver.create_container(self.GNS3_CONTAINER_NAME)
        except ContainerAlreadyExistsError:
            gns3_container = self.storage_driver.get_container(self.GNS3_CONTAINER_NAME)

        with open(file_path, 'rb') as file:
            local_file_hash = hashlib.md5(file.read()).hexdigest()

            cloud_hash_name = cloud_object_name + '.md5'
            cloud_objects = [obj.name for obj in gns3_container.list_objects()]

            # if the file and its hash are in object storage, and the local and storage file hashes match
            # do not upload the file, otherwise upload it
            if cloud_object_name in cloud_objects and cloud_hash_name in cloud_objects:
                hash_object = gns3_container.get_object(cloud_hash_name)
                cloud_object_hash = ''
                for chunk in hash_object.as_stream():
                    cloud_object_hash += chunk.decode('utf8')

                if cloud_object_hash == local_file_hash:
                    return False

            file.seek(0)
            self.storage_driver.upload_object_via_stream(file, gns3_container, cloud_object_name)
            self.storage_driver.upload_object_via_stream(StringIO(local_file_hash), gns3_container, cloud_hash_name)
            return True

    def list_projects(self):
        """
        Lists projects in cloud storage
        :return: Dictionary where project names are keys and values are names of objects in storage
        """

        try:
            gns3_container = self.storage_driver.get_container(self.GNS3_CONTAINER_NAME)
            projects = {
                obj.name.replace('projects/', '').replace('.zip', ''): obj.name
                for obj in gns3_container.list_objects()
                if obj.name.startswith('projects/') and obj.name[-4:] == '.zip'
            }
            return projects
        except ContainerDoesNotExistError:
            return []

    def download_file(self, file_name, destination=None):
        """
        Downloads file from cloud storage. If a file exists at destination, and it is identical to the file in cloud
        storage, it is not downloaded.
        :param file_name: name of file in cloud storage to download
        :param destination: local path to save file to (if None, returns file contents as a file-like object)
        :return: A file-like object if file contents are returned, or None if file is saved to filesystem
        """

        gns3_container = self.storage_driver.get_container(self.GNS3_CONTAINER_NAME)
        storage_object = gns3_container.get_object(file_name)

        if destination is not None:
            if os.path.isfile(destination):
                # if a file exists at destination and its hash matches that of the
                # file in cloud storage, don't download it
                with open(destination, 'rb') as f:
                    local_file_hash = hashlib.md5(f.read()).hexdigest()

                    hash_object = gns3_container.get_object(file_name + '.md5')
                    cloud_object_hash = ''
                    for chunk in hash_object.as_stream():
                        cloud_object_hash += chunk.decode('utf8')

                    if local_file_hash == cloud_object_hash:
                        return

            storage_object.download(destination)
        else:
            contents = b''

            for chunk in storage_object.as_stream():
                contents += chunk

            return BytesIO(contents)

    def find_storage_image_names(self, images_to_find):
        """
        Maps names of image files to their full name in cloud storage
        :param images_to_find: list of image names to find
        :return: A dictionary where keys are image names, and values are the corresponding names of
        the files in cloud storage
        """
        gns3_container = self.storage_driver.get_container(self.GNS3_CONTAINER_NAME)
        images_in_storage = [obj.name for obj in gns3_container.list_objects() if obj.name.startswith('images/')]

        images = {}
        for image_name in images_to_find:
            images_with_same_name =\
                list(filter(lambda storage_image_name: storage_image_name.endswith(image_name), images_in_storage))

            if len(images_with_same_name) == 1:
                images[image_name] = images_with_same_name[0]
            else:
                raise Exception('Image does not exist in cloud storage or is duplicated')

        return images

    def delete_file(self, file_name):
        gns3_container = self.storage_driver.get_container(self.GNS3_CONTAINER_NAME)

        try:
            object_to_delete = gns3_container.get_object(file_name)
            object_to_delete.delete()
        except ObjectDoesNotExistError:
            pass

        try:
            hash_object = gns3_container.get_object(file_name + '.md5')
            hash_object.delete()
        except ObjectDoesNotExistError:
            pass
