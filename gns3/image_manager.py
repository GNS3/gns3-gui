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
import pathlib

from gns3.qt import QtCore, QtWidgets
from gns3.utils.file_copy_worker import FileCopyWorker
from gns3.utils.progress_dialog import ProgressDialog


class ImageManager:

    @classmethod
    def askCopyUploadImage(cls, parent, path, server, destination_directory, upload_endpoint):
        """
        Ask user for copying the image to the default directory or upload
        it to remote server.

        :param parent: Parent window
        :param path: File path on computer
        :param server: The server where the images should be located
        :param destination_directory: Local destination directory
        :param upload_endpoint: Remote upload endpoint
        :returns path: Final path
        """

        if server and not server.isLocal():
            return cls._uploadImageToRemoteServer(path, server, upload_endpoint)
        else:
            if os.path.normpath(os.path.dirname(path)) != destination_directory:
                # the IOS image is not in the default images directory
                reply = QtWidgets.QMessageBox.question(parent,
                                                       "Image",
                                                       "Would you like to copy {} to the default images directory".format(os.path.basename(path)),
                                                       QtWidgets.QMessageBox.Yes,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    destination_path = os.path.join(destination_directory, os.path.basename(path))
                    worker = FileCopyWorker(path, destination_path)
                    progress_dialog = ProgressDialog(worker, "Image", "Copying {}".format(os.path.basename(path)), "Cancel", busy=True, parent=parent)
                    progress_dialog.show()
                    progress_dialog.exec_()
                    errors = progress_dialog.errors()
                    if errors:
                        QtWidgets.QMessageBox.critical(parent, "Image", "{}".format("".join(errors)))
                    else:
                        path = destination_path
            return path

    @staticmethod
    def _uploadImageToRemoteServer(path, server, upload_endpoint):
        """
        Upload image to remote server

        :param path: File path on computer
        :param server: The server where the images should be located
        :returns path: Final path
        """

        filename = os.path.basename(path)
        server.post("{}/{}".format(upload_endpoint, filename), None, body=pathlib.Path(path))
        return filename
