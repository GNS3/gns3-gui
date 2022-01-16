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

import os
import copy
import pathlib

from gns3.qt import QtWidgets
from gns3.controller import Controller
from gns3.utils.file_copy_worker import FileCopyWorker
from gns3.utils.progress_dialog import ProgressDialog
from gns3.http_client_error import HttpClientError, HttpClientCancelledRequestError
from gns3.registry.image import Image


class ImageManager:

    def __init__(self):
        # Remember if we already ask the user about this image for this server
        self._asked_for_this_image = {}

    def _getUniqueDestinationPath(self, source_image, node_type, path):
        """
        Get a unique destination path (with counter).
        """

        if not os.path.exists(path):
            return path
        path, extension = os.path.splitext(path)
        counter = 1
        new_path = "{}-{}{}".format(path, counter, extension)
        while os.path.exists(new_path):
            destination_image = Image(node_type, new_path, filename=os.path.basename(new_path))
            try:
                if source_image.md5sum == destination_image.md5sum:
                    # the source and destination images are identical
                    return new_path
            except OSError:
                continue
            counter += 1
            new_path = "{}-{}{}".format(path, counter, extension)
        return new_path

    def askCopyUploadImage(self, parent, source_path, server, node_type):
        """
        Ask user for copying the image to the default directory or upload
        it to remote server.

        :param parent: Parent window
        :param path: File path on computer
        :param server: The server where the images should be located
        :param node_type: Remote upload endpoint
        :returns path: Final path
        """

        if (server and server != "local") or Controller.instance().isRemote():
            return self._uploadImageToRemoteServer(source_path, node_type, parent)
        else:
            destination_directory = self.getDirectoryForType(node_type)
            destination_path = os.path.join(destination_directory, os.path.basename(source_path))
            source_filename = os.path.basename(source_path)
            destination_filename = os.path.basename(destination_path)
            if os.path.normpath(os.path.dirname(source_path)) != destination_directory:
                # the image is not in the default images directory
                if source_filename == destination_filename:
                    # the filename already exists in the default images directory
                    source_image = Image(node_type, source_path, filename=source_filename)
                    destination_image = Image(node_type, destination_path, filename=destination_filename)
                    try:
                        if source_image.md5sum == destination_image.md5sum:
                            # the source and destination images are identical
                            return source_path
                    except OSError as e:
                        QtWidgets.QMessageBox.critical(parent, 'Image', 'Cannot compare image file {} with {}: {}.'.format(source_path, destination_path, str(e)))
                        return source_path
                    # find a new unique path to avoid overwriting existing destination file
                    destination_path = self._getUniqueDestinationPath(source_image, node_type, destination_path)

                reply = QtWidgets.QMessageBox.question(parent,
                                                       'Image',
                                                       'Would you like to copy {} to the default images directory'.format(source_filename),
                                                       QtWidgets.QMessageBox.Yes,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    try:
                        os.makedirs(destination_directory, exist_ok=True)
                    except OSError as e:
                        QtWidgets.QMessageBox.critical(parent, 'Image', 'Could not create destination directory {}: {}'.format(destination_directory, str(e)))
                        return source_path

                    worker = FileCopyWorker(source_path, destination_path)
                    progress_dialog = ProgressDialog(worker, 'Image', 'Copying {}'.format(source_filename), 'Cancel', busy=True, parent=parent)
                    progress_dialog.show()
                    progress_dialog.exec_()
                    errors = progress_dialog.errors()
                    if errors:
                        QtWidgets.QMessageBox.critical(parent, 'Image', '{}'.format(''.join(errors)))
                        return source_path
                    else:
                        source_path = destination_path
            return source_path

    def _uploadImageToRemoteServer(self, path, node_type, parent):
        """
        Upload image to remote server

        :param path: File path on computer
        :param node_type: Image node_type
        :returns path: Final path
        """

        if node_type == 'QEMU':
            image_type = 'qemu'
        elif node_type == 'IOU':
            image_type = 'iou'
        elif node_type == 'DYNAMIPS':
            image_type = 'ios'
        else:
            raise Exception('Invalid node type')

        filename = self._getRelativeImagePath(path, node_type).replace("\\", "/")

        try:
            Controller.instance().post(
                f"/images/upload/{filename}",
                callback=None,
                params={"image_type": image_type},
                body=pathlib.Path(path),
                progress_text="Uploading {}".format(filename),
                timeout=None,
                wait=True
            )
        except HttpClientCancelledRequestError:
            return
        except HttpClientError as e:
            QtWidgets.QMessageBox.critical(
                parent,
                "Image upload",
                f"Could not upload image {filename}: {e}"
            )

        return filename

    def _getRelativeImagePath(self, path, node_type):
        """
        Get a path relative to images directory path
        or just filename if the path is not located inside
        image directory

        :param path: file path
        :param node_type: Type of vm
        :return: file path
        """

        if not path:
            return ""
        img_directory = self.getDirectoryForType(node_type)
        path = os.path.abspath(path)
        if os.path.commonprefix([img_directory, path]) == img_directory:
            return os.path.relpath(path, img_directory)
        return os.path.basename(path)

    def getDirectory(self):
        """
        Returns the images directory path.

        :returns: path to the default images directory
        """

        return copy.copy(Controller.instance().settings()['images_path'])

    def getDirectoryForType(self, node_type):
        """
        Return the path of local directory of the images
        of a specific node_type

        :param node_type: Type of vm
        """
        if node_type == 'DYNAMIPS':
            return os.path.join(self.getDirectory(), 'IOS')
        else:
            return os.path.join(self.getDirectory(), node_type.upper())

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of ImageManager.

        :returns: instance of ImageManager
        """

        if not hasattr(ImageManager, '_instance') or ImageManager._instance is None:
            ImageManager._instance = ImageManager()
        return ImageManager._instance
