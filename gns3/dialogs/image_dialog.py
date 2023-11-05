# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 GNS3 Technologies Inc.
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
from gns3.http_client_error import HttpClientError, HttpClientCancelledRequestError
from ..qt import QtCore, QtWidgets, qslot, sip_is_deleted
from ..ui.image_dialog_ui import Ui_ImageDialog
from ..utils import human_size
from ..controller import Controller


import logging
log = logging.getLogger(__name__)


class ImageDialog(QtWidgets.QDialog, Ui_ImageDialog):
    """
    Image management dialog.
    """

    def __init__(self, parent):
        """
        :param parent: parent widget.
        """
        super().__init__(parent)
        self.setupUi(self)
        self.uiUploadImagePushButton.clicked.connect(self._uploadImageSlot)
        self.uiDeleteImagePushButton.clicked.connect(self._deleteImageSlot)
        self.uiRefreshImagesPushButton.clicked.connect(Controller.instance().refreshImageList)
        Controller.instance().image_list_updated_signal.connect(self._updateImageListSlot)
        self._updateImageListSlot()
        Controller.instance().refreshImageList()

    @qslot
    def _uploadImageSlot(self, *args):

        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select one or more images to upload",
            QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation),
            "Images (*.bin *.image *.qcow2 *.vmdk *.iso);;All files (*.*)"
        )
        error_msgs = ""
        for path in files:
            log.debug("Uploading image '{}' to controller".format(path))
            image_filename = os.path.basename(path)
            install_appliances = self.uiInstallApplianceCheckBox.isChecked()
            try:
                Controller.instance().post(
                    f"/images/upload/{image_filename}",
                    params={"install_appliances": install_appliances},
                    body=pathlib.Path(path),
                    context={"image_path": path},
                    progress_text="Uploading {}".format(image_filename),
                    timeout=None,
                    wait=True
                )
            except HttpClientCancelledRequestError:
                return
            except HttpClientError as e:
                error_msgs += f"{e}\n"

        if error_msgs:
            error_dialog = QtWidgets.QMessageBox(self)
            error_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            error_dialog.setWindowTitle("Image upload")
            error_dialog.setText(f"Error while uploading images to the controller")
            error_dialog.setDetailedText(error_msgs)
            error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
            error_dialog.show()

        Controller.instance().refreshImageList()

    @qslot
    def _deleteImageSlot(self, *args):

        if len(self.uiImagesTreeWidget.selectedItems()) == 0:
            QtWidgets.QMessageBox.critical(self, "Delete image", "No images selected")
            return

        reply = QtWidgets.QMessageBox.warning(
            self,
            "Delete image(s)",
            "Delete the selected images?\nThis cannot be reverted.",
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.No:
            return

        images_to_delete = set()
        for image in self.uiImagesTreeWidget.selectedItems():
            if sip_is_deleted(image):
                continue
            image_filename = image.data(0, QtCore.Qt.UserRole)
            images_to_delete.add(image_filename)

        error_msgs = ""
        for image_filename in images_to_delete:
            try:
                Controller.instance().delete(
                    f"/images/{image_filename}",
                    progress_text=f"Deleting {image_filename}",
                    timeout=None,
                    wait=True
                )
            except HttpClientCancelledRequestError:
                return
            except HttpClientError as e:
                error_msgs += f"{e}\n"

        if error_msgs:
            error_dialog = QtWidgets.QMessageBox(self)
            error_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            error_dialog.setWindowTitle("Image deletion")
            error_dialog.setText(f"Error while deleting images on the controller")
            error_dialog.setDetailedText(error_msgs)
            error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
            error_dialog.show()

        Controller.instance().refreshImageList()

    @qslot
    def _updateImageListSlot(self, *args):

        self.uiImagesTreeWidget.clear()
        self.uiDeleteImagePushButton.setEnabled(False)
        self.uiImagesTreeWidget.setUpdatesEnabled(False)
        items = []
        for image in Controller.instance().images():
            item = QtWidgets.QTreeWidgetItem([image["filename"], image["image_type"], human_size(image["image_size"])])
            item.setData(0, QtCore.Qt.UserRole, image["filename"])
            items.append(item)

        self.uiImagesTreeWidget.addTopLevelItems(items)
        if len(Controller.instance().images()):
            self.uiDeleteImagePushButton.setEnabled(True)

        self.uiImagesTreeWidget.header().setResizeContentsPrecision(100)  # How many rows are checked for the resize for performance reason
        self.uiImagesTreeWidget.resizeColumnToContents(0)
        self.uiImagesTreeWidget.resizeColumnToContents(1)
        self.uiImagesTreeWidget.resizeColumnToContents(2)
        self.uiImagesTreeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        self.uiImagesTreeWidget.setUpdatesEnabled(True)

    def keyPressEvent(self, e):
        """
        Event handler in order to properly handle escape.
        """

        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
