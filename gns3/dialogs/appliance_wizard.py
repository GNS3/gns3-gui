#!/usr/bin/env python
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
import sip

from ..qt import QtWidgets, QtCore, QtGui, qpartial, qslot
from ..ui.appliance_wizard_ui import Ui_ApplianceWizard
from ..modules import Qemu
from ..registry.appliance import Appliance, ApplianceError
from ..registry.registry import Registry
from ..registry.config import Config, ConfigException
from ..registry.image import Image
from ..utils import human_filesize
from ..utils.wait_for_lambda_worker import WaitForLambdaWorker
from ..utils.progress_dialog import ProgressDialog
from ..compute_manager import ComputeManager
from ..controller import Controller
from ..local_config import LocalConfig


class ApplianceWizard(QtWidgets.QWizard, Ui_ApplianceWizard):
    images_changed_signal = QtCore.Signal()
    versions_changed_signal = QtCore.Signal()

    def __init__(self, parent, path):
        super().__init__(parent)
        self.setupUi(self)
        self.images_changed_signal.connect(self._refreshVersions)
        self.versions_changed_signal.connect(self._versionRefreshedSlot)

        self._refreshing = False

        self._path = path
        # Count how many images are curently uploading
        self._image_uploading_count = 0

        images_directories = list()
        images_directories.append(os.path.dirname(self._path))
        download_directory = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)
        if download_directory != "" and download_directory != os.path.dirname(self._path):
            images_directories.append(download_directory)
        self._registry = Registry(images_directories)
        self._registry.image_list_changed_signal.connect(self.images_changed_signal.emit)

        self._appliance = Appliance(self._registry, self._path)

        self.uiApplianceVersionTreeWidget.currentItemChanged.connect(self._applianceVersionCurrentItemChangedSlot)
        self.uiRefreshPushButton.clicked.connect(self.images_changed_signal.emit)
        self.uiDownloadPushButton.clicked.connect(self._downloadPushButtonClickedSlot)
        self.uiImportPushButton.clicked.connect(self._importPushButtonClickedSlot)
        self.uiCreateVersionPushButton.clicked.connect(self._createVersionPushButtonClickedSlot)

        self.uiRemoteRadioButton.toggled.connect(self._remoteServerToggledSlot)
        if hasattr(self, "uiVMRadioButton"):
            self.uiVMRadioButton.toggled.connect(self._vmToggledSlot)

        self.uiLocalRadioButton.toggled.connect(self._localToggledSlot)
        if Controller.instance().isRemote():
            self.uiLocalRadioButton.setText("Run the appliance on the main server")

        self.uiServerWizardPage.isComplete = self._uiServerWizardPage_isComplete

    def initializePage(self, page_id):
        """
        Initialize Wizard pages.

        :param page_id: page identifier
        """
        super().initializePage(page_id)

        if self._appliance["category"] == "guest":
            symbol = ":/symbols/computer.svg"
        else:
            symbol = ":/symbols/{}.svg".format(self._appliance["category"])
        self.page(page_id).setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(symbol))

        if "qemu" in self._appliance:
            type = "qemu"
        elif "iou" in self._appliance:
            type = "iou"
        elif "docker" in self._appliance:
            type = "docker"
        elif "dynamips" in self._appliance:
            type = "dynamips"

        if self.page(page_id) == self.uiInfoWizardPage:
            self.uiInfoWizardPage.setTitle(self._appliance["product_name"])
            self.uiDescriptionLabel.setText(self._appliance["description"])

            info = (
                ("Category", "category"),
                ("Product", "product_name"),
                ("Vendor", "vendor_name"),
                ("Status", "status"),
                ("Maintainer", "maintainer"),
                ("Architecture", "qemu/arch"),
                ("KVM", "qemu/kvm")
            )

            self.uiInfoTreeWidget.clear()
            for (name, key) in info:
                if "/" in key:
                    key, subkey = key.split("/")
                    value = self._appliance.get(key, {}).get(subkey, None)
                else:
                    value = self._appliance.get(key, None)
                if value is None:
                    continue
                item = QtWidgets.QTreeWidgetItem([name + ":", value])
                font = item.font(0)
                font.setBold(True)
                item.setFont(0, font)
                self.uiInfoTreeWidget.addTopLevelItem(item)

        elif self.page(page_id) == self.uiServerWizardPage:
            self.uiRemoteServersComboBox.clear()
            if len(ComputeManager.instance().remoteComputes()) == 0:
                self.uiRemoteRadioButton.setEnabled(False)
            else:
                self.uiRemoteRadioButton.setEnabled(True)
                for compute in ComputeManager.instance().remoteComputes():
                    self.uiRemoteServersComboBox.addItem(compute.name(), compute)

            if not ComputeManager.instance().vmCompute():
                self.uiVMRadioButton.setEnabled(False)

            if ComputeManager.instance().localPlatform() is None:
                self.uiLocalRadioButton.setEnabled(False)
            elif (ComputeManager.instance().localPlatform().startswith("darwin") or ComputeManager.instance().localPlatform().startswith("win")):
                if type == "qemu":
                    # Qemu has issues on OSX and Windows we disallow usage of the local server
                    if not LocalConfig.instance().experimental():
                        self.uiLocalRadioButton.setEnabled(False)
                elif type != "dynamips":
                    self.uiLocalRadioButton.setEnabled(False)

            if ComputeManager.instance().vmCompute():
                self.uiVMRadioButton.setChecked(True)
            elif ComputeManager.instance().localCompute() and self.uiLocalRadioButton.isEnabled():
                self.uiLocalRadioButton.setChecked(True)
            elif self.uiRemoteRadioButton.isEnabled():
                self.uiRemoteRadioButton.setChecked(True)
            else:
                self.uiRemoteRadioButton.setChecked(False)

        elif self.page(page_id) == self.uiFilesWizardPage:
            self._registry.getRemoteImageList(self._appliance.emulator(), self._compute_id)

        elif self.page(page_id) == self.uiQemuWizardPage:
            Qemu.instance().getQemuBinariesFromServer(self._compute_id, qpartial(self._getQemuBinariesFromServerCallback), [self._appliance["qemu"]["arch"]])

        elif self.page(page_id) == self.uiSummaryWizardPage:
            self.uiSummaryTreeWidget.clear()

            for key in self._appliance[type]:
                item = QtWidgets.QTreeWidgetItem([key.replace('_', ' ').capitalize() + ":", str(self._appliance[type][key])])
                font = item.font(0)
                font.setBold(True)
                item.setFont(0, font)
                self.uiSummaryTreeWidget.addTopLevelItem(item)
            self.uiSummaryTreeWidget.resizeColumnToContents(0)

        elif self.page(page_id) == self.uiUsageWizardPage:
            self.uiUsageTextEdit.setText("The appliance is available in the {} category. \n\n{}".format(
                self._appliance["category"].replace("_", " "),
                self._appliance.get("usage", ""))
            )

        elif self.page(page_id) == self.uiCheckServerWizardPage:
            self.uiCheckServerLabel.setText("Please wait while checking server capacities...")
            if 'qemu' in self._appliance:
                if self._appliance['qemu'].get('kvm', 'require') == 'require':
                    self._server_check = False  # If the server as the capacities for running the appliance
                    self.uiCheckServerLabel.setText("")
                    Qemu.instance().getQemuCapabilitiesFromServer(self._compute_id, qpartial(self._qemuServerCapabilitiesCallback))
                    return
            self.uiCheckServerLabel.setText("GNS3 server requirements is OK you can continue the installation")
            self._server_check = True

    def _qemuServerCapabilitiesCallback(self, result, error=None, *args, **kwargs):
        """
        Check if server support KVM or not
        """
        if error is None and "kvm" in result and self._appliance["qemu"]["arch"] in result["kvm"]:
            self._server_check = True
            self.uiCheckServerLabel.setText("GNS3 server requirements is OK you can continue the installation")
        else:
            if error:
                msg = result["message"]
            else:
                msg = "The remote server doesn't support KVM. You need a Linux server or the GNS3 VM with VMware and CPU virtualization instructions."
            self.uiCheckServerLabel.setText(msg)
            QtWidgets.QMessageBox.critical(self, "Qemu", msg)
            self._server_check = False

    def _uiServerWizardPage_isComplete(self):
        return self.uiRemoteRadioButton.isEnabled() or self.uiVMRadioButton.isEnabled() or self.uiLocalRadioButton.isEnabled()

    def _imageUploadedCallback(self, result, error=False, **kwargs):
        self._registry.getRemoteImageList(self._appliance.emulator(), self._compute_id)

    @qslot
    def _refreshVersions(self, *args):
        """
        Refresh the list of files for different version of the appliance
        """

        if self._refreshing:
            return
        self._refreshing = True

        self.uiFilesWizardPage.setSubTitle("The following versions are available for " + self._appliance["product_name"] + ".  Check the status of files required to install.")

        worker = WaitForLambdaWorker(lambda: self._refreshDialogWorker())
        progress_dialog = ProgressDialog(worker, "Add appliance", "Scanning directories for files...", None, busy=True, parent=self)
        progress_dialog.show()

    @qslot
    def _versionRefreshedSlot(self, *args):
        """
        Called when we finish to scan the disk for new versions
        """
        if self._refreshing or self.currentPage() != self.uiFilesWizardPage:
            return
        self._refreshing = True
        self.uiApplianceVersionTreeWidget.clear()

        for version in self._appliance["versions"]:
            top = QtWidgets.QTreeWidgetItem(self.uiApplianceVersionTreeWidget, ["{} {}".format(self._appliance["product_name"], version["name"])])
            size = 0
            status = "Ready to install"
            for image in version["images"].values():
                if image["status"] == "Missing":
                    status = "Missing files"

                size += image.get("filesize", 0)
                image_widget = QtWidgets.QTreeWidgetItem(
                    [
                        "",
                        image["filename"],
                        human_filesize(image.get("filesize", 0)),
                        image["status"],
                        image["version"],
                        image.get("md5sum", "")
                    ])
                if image["status"] == "Missing":
                    image_widget.setForeground(3, QtGui.QBrush(QtGui.QColor("red")))
                else:
                    image_widget.setForeground(3, QtGui.QBrush(QtGui.QColor("green")))

                # Associated data stored are col 0: version, col 1: image
                image_widget.setData(0, QtCore.Qt.UserRole, version)
                image_widget.setData(1, QtCore.Qt.UserRole, image)
                image_widget.setData(2, QtCore.Qt.UserRole, self._appliance)
                top.addChild(image_widget)

            font = top.font(0)
            font.setBold(True)
            top.setFont(0, font)

            expand = True
            if status == "Missing files":
                top.setForeground(3, QtGui.QBrush(QtGui.QColor("red")))
            else:
                expand = False
                top.setForeground(3, QtGui.QBrush(QtGui.QColor("green")))

            top.setData(2, QtCore.Qt.DisplayRole, human_filesize(size))
            top.setData(3, QtCore.Qt.DisplayRole, status)
            top.setData(2, QtCore.Qt.UserRole, self._appliance)
            top.setData(0, QtCore.Qt.UserRole, version)
            self.uiApplianceVersionTreeWidget.addTopLevelItem(top)
            # self.uiApplianceVersionTreeWidget.setCurrentItem(top)
            if expand:
                top.setExpanded(True)

        if len(self._appliance["versions"]) > 0:
            self.uiApplianceVersionTreeWidget.resizeColumnToContents(0)
            self.uiApplianceVersionTreeWidget.resizeColumnToContents(1)
        self._refreshing = False

    def _refreshDialogWorker(self):
        """
        Scan local directory in order to found the images on disk
        """

        # Docker do not have versions
        if "versions" not in self._appliance:
            return

        for version in self._appliance["versions"]:
            for image in version["images"].values():
                img = self._registry.search_image_file(self._appliance.emulator(), image["filename"], image.get("md5sum"), image.get("filesize"))
                if img:
                    image["status"] = "Found"
                    image["md5sum"] = img.md5sum
                    image["filesize"] = img.filesize
                else:
                    image["status"] = "Missing"
        self._refreshing = False
        self.versions_changed_signal.emit()

    @qslot
    def _applianceVersionCurrentItemChangedSlot(self, current, previous):
        """
        Called when user select a different item in the list of appliance files
        """
        self.uiDownloadPushButton.hide()
        self.uiImportPushButton.hide()
        self.uiExplainDownloadLabel.hide()

        if current is None or sip.isdeleted(current):
            return

        image = current.data(1, QtCore.Qt.UserRole)
        if image is not None:
            if "direct_download_url" in image or "download_url" in image:
                self.uiDownloadPushButton.show()
            self.uiImportPushButton.show()

    @qslot
    def _downloadPushButtonClickedSlot(self, *args):
        """
        Called when user want to download an appliance images.
        He should have selected the file before.
        """
        if self._refreshing:
            return False

        current = self.uiApplianceVersionTreeWidget.currentItem()

        if current is None or sip.isdeleted(current):
            return

        data = current.data(1, QtCore.Qt.UserRole)
        if data is not None:
            if "direct_download_url" in data:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(data["direct_download_url"]))
                if "compression" in data:
                    QtWidgets.QMessageBox.warning(self, "Add appliance", "The file is compressed with {} you need to uncompress it before using it.".format(data["compression"]))
            else:
                QtWidgets.QMessageBox.warning(self, "Add appliance", "Download will redirect you where the required file can be downloaded, you may have to be registered with the vendor in order to download the file.")
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(data["download_url"]))

    @qslot
    def _createVersionPushButtonClickedSlot(self, *args):
        """
        Allow user to create a new version of an appliance
        """

        new_version, ok = QtWidgets.QInputDialog.getText(self, "Creating a new version", "Creating a new version allows to import unknown files to use with this appliance.\nPlease share your experience on the GNS3 community if this version works.\n\nVersion name:", QtWidgets.QLineEdit.Normal)
        if ok:
            try:
                self._appliance.create_new_version(new_version)
            except ApplianceError as e:
                QtWidgets.QMessageBox.critical(self.parent(), "Create new version", str(e))
                return
            self.images_changed_signal.emit()

    @qslot
    def _importPushButtonClickedSlot(self, *args):
        """
        Called when user want to import an appliance images.
        He should have selected the file before.
        """
        if self._refreshing:
            return False

        current = self.uiApplianceVersionTreeWidget.currentItem()
        if not current:
            return
        disk = current.data(1, QtCore.Qt.UserRole)

        path, _ = QtWidgets.QFileDialog.getOpenFileName()
        if len(path) == 0:
            return

        image = Image(self._appliance.emulator(), path, filename=disk["filename"])
        try:
            if "md5sum" in disk and image.md5sum != disk["md5sum"]:
                QtWidgets.QMessageBox.warning(self.parent(), "Add appliance", "This is not the correct file. The MD5 sum is {} and should be {}.".format(image.md5sum, disk["md5sum"]))
                return
        except OSError as e:
            QtWidgets.QMessageBox.warning(self.parent(), "Add appliance", "Can't access to the image file {}: {}.".format(path, str(e)))
            return
        image.upload(self._compute_id, callback=self._imageUploadedCallback)

    def _getQemuBinariesFromServerCallback(self, result, error=False, **kwargs):
        """
        Callback for getQemuBinariesFromServer.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "Qemu binaries", "{}".format(result["message"]))
        else:
            self.uiQemuListComboBox.clear()
            for qemu in result:
                if qemu["version"]:
                    self.uiQemuListComboBox.addItem("{path} (v{version})".format(path=qemu["path"], version=qemu["version"]), qemu["path"])
                else:
                    self.uiQemuListComboBox.addItem("{path}".format(path=qemu["path"]), qemu["path"])
            if self.uiQemuListComboBox.count() == 1:
                self.next()
            else:
                i = self.uiQemuListComboBox.findText(self._appliance["qemu"]["arch"], QtCore.Qt.MatchContains)
                if i != -1:
                    self.uiQemuListComboBox.setCurrentIndex(i)

    def _install(self, version):
        """
        Install the appliance to GNS3

        :params version: Version name
        """

        try:
            config = Config()
        except OSError as e:
            QtWidgets.QMessageBox.critical(self.parent(), "Add appliance", str(e))
            return False

        if version is None:
            appliance_configuration = self._appliance.copy()
        else:
            try:
                appliance_configuration = self._appliance.search_images_for_version(version)
            except ApplianceError as e:
                QtWidgets.QMessageBox.critical(self.parent(), "Add appliance", str(e))
                return False

        while len(appliance_configuration["name"]) == 0 or not config.is_name_available(appliance_configuration["name"]):
            QtWidgets.QMessageBox.warning(self.parent(), "Add appliance", "The name \"{}\" is already used by another appliance".format(appliance_configuration["name"]))
            appliance_configuration["name"], ok = QtWidgets.QInputDialog.getText(self.parent(), "Add appliance", "New name:", QtWidgets.QLineEdit.Normal, appliance_configuration["name"])
            appliance_configuration["name"] = appliance_configuration["name"].strip()

        if "qemu" in appliance_configuration:
            appliance_configuration["qemu"]["path"] = self.uiQemuListComboBox.currentData()

        worker = WaitForLambdaWorker(lambda: config.add_appliance(appliance_configuration, self._compute_id), allowed_exceptions=[ConfigException, OSError])
        progress_dialog = ProgressDialog(worker, "Add appliance", "Install the appliance...", None, busy=True, parent=self)
        progress_dialog.show()
        if not progress_dialog.exec_():
            return False

        worker = WaitForLambdaWorker(lambda: config.save(), allowed_exceptions=[ConfigException, OSError])
        progress_dialog = ProgressDialog(worker, "Add appliance", "Install the appliance...", None, busy=True, parent=self)
        progress_dialog.show()
        if progress_dialog.exec_():
            QtWidgets.QMessageBox.information(self.parent(), "Add appliance", "{} installed!".format(appliance_configuration["name"]))
            return True

    def _uploadImages(self, version):
        """
        Upload an image to the compute
        """

        appliance_configuration = self._appliance.search_images_for_version(version)
        for image in appliance_configuration["images"]:
            if image["location"] == "local":
                image = Image(self._appliance.emulator(), image["path"], filename=image["filename"])
                image.upload(self._compute_id, self._applianceImageUploadedCallback)
                self._image_uploading_count += 1

    def _applianceImageUploadedCallback(self, result, error=False, **kwargs):
        self._image_uploading_count -= 1

    def nextId(self):
        if self.currentPage() == self.uiServerWizardPage:
            if "docker" in self._appliance:
                return super().nextId() + 3
            elif "qemu" not in self._appliance:
                return super().nextId() + 1
        elif self.currentPage() == self.uiFilesWizardPage:
            if "qemu" not in self._appliance:
                return super().nextId() + 1
        return super().nextId()

    def validateCurrentPage(self):
        """
        Validates the settings.
        """

        if self.currentPage() == self.uiFilesWizardPage:
            if self._refreshing:
                return False
            current = self.uiApplianceVersionTreeWidget.currentItem()
            if current is None or sip.isdeleted(current):
                return False
            version = current.data(0, QtCore.Qt.UserRole)
            if version is None:
                return False
            appliance = current.data(2, QtCore.Qt.UserRole)
            if not self._appliance.is_version_installable(version["name"]):
                QtWidgets.QMessageBox.warning(self, "Appliance", "Sorry, you cannot install {} with missing files".format(appliance["name"]))
                return False
            reply = QtWidgets.QMessageBox.question(self, "Appliance", "Would you like to install {} version {}?".format(appliance["name"], version["name"]),
                                                   QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                return False
            self._uploadImages(version["name"])

        elif self.currentPage() == self.uiUsageWizardPage:
            if self._image_uploading_count > 0:
                QtWidgets.QMessageBox.critical(self, "Add appliance", "Please wait for image uploading")
                return False

            current = self.uiApplianceVersionTreeWidget.currentItem()
            if current:
                version = current.data(0, QtCore.Qt.UserRole)
                return self._install(version["name"])
            else:
                return self._install(None)

        elif self.currentPage() == self.uiServerWizardPage:
            if self.uiRemoteRadioButton.isChecked():
                if len(ComputeManager.instance().remoteComputes()) == 0:
                    QtWidgets.QMessageBox.critical(self, "Remote server", "There is no remote server registered in your preferences")
                    return False
                self._compute_id = self.uiRemoteServersComboBox.itemData(self.uiRemoteServersComboBox.currentIndex()).id()
            elif hasattr(self, "uiVMRadioButton") and self.uiVMRadioButton.isChecked():
                self._compute_id = "vm"
            else:
                if ComputeManager.instance().localPlatform():
                    if (ComputeManager.instance().localPlatform().startswith("darwin") or ComputeManager.instance().localPlatform().startswith("win")):
                        if "qemu" in self._appliance:
                            reply = QtWidgets.QMessageBox.question(self, "Appliance", "Qemu on Windows and MacOSX is not supported by the GNS3 team. Are you sur to continue?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                            if reply == QtWidgets.QMessageBox.No:
                                return False

                self._compute_id = "local"

        elif self.currentPage() == self.uiQemuWizardPage:
            if self.uiQemuListComboBox.currentIndex() == -1:
                QtWidgets.QMessageBox.critical(self, "Qemu binary", "No compatible Qemu binary selected")
                return False

        elif self.currentPage() == self.uiCheckServerWizardPage:
            return self._server_check

        return True

    @qslot
    def _vmToggledSlot(self, checked):
        """
        Slot for when the VM radio button is toggled.

        :param checked: either the button is checked or not
        """
        if checked:
            self.uiRemoteServersGroupBox.setEnabled(False)
            self.uiRemoteServersGroupBox.hide()

    @qslot
    def _remoteServerToggledSlot(self, checked):
        """
        Slot for when the remote server radio button is toggled.

        :param checked: either the button is checked or not
        """

        if checked:
            self.uiRemoteServersGroupBox.setEnabled(True)
            self.uiRemoteServersGroupBox.show()

    @qslot
    def _localToggledSlot(self, checked):
        """
        Slot for when the local server radio button is toggled.

        :param checked: either the button is checked or not
        """
        if checked:
            self.uiRemoteServersGroupBox.setEnabled(False)
            self.uiRemoteServersGroupBox.hide()
