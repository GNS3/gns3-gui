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
from ..qt import sip
import shutil

from ..qt import QtWidgets, QtCore, QtGui, qpartial, qslot
from ..ui.appliance_wizard_ui import Ui_ApplianceWizard
from ..template_manager import TemplateManager
from ..template import Template
from ..modules import Qemu
from ..registry.appliance import Appliance, ApplianceError
from ..registry.registry import Registry
from ..registry.config import Config
from ..registry.appliance_to_template import ApplianceToTemplate
from ..registry.image import Image
from ..utils import human_filesize
from ..utils.wait_for_lambda_worker import WaitForLambdaWorker
from ..utils.progress_dialog import ProgressDialog
from ..compute_manager import ComputeManager
from ..controller import Controller
from ..local_config import LocalConfig
from ..image_upload_manager import ImageUploadManager
from ..image_manager import ImageManager

import logging
log = logging.getLogger(__name__)


class ApplianceWizard(QtWidgets.QWizard, Ui_ApplianceWizard):

    images_changed_signal = QtCore.Signal()
    versions_changed_signal = QtCore.Signal()

    def __init__(self, parent, path):
        super().__init__(parent)

        self.setupUi(self)
        self._refreshing = False
        self._server_check = False
        self._template_created = False
        self._path = path

        # count how many images are being uploaded
        self._image_uploading_count = 0

        # symbols loaded from controller
        self._symbols = []

        # connect slots
        self.images_changed_signal.connect(self._refreshVersions)
        self.versions_changed_signal.connect(self._versionRefreshedSlot)
        self.uiRefreshPushButton.clicked.connect(self.images_changed_signal.emit)
        self.uiDownloadPushButton.clicked.connect(self._downloadPushButtonClickedSlot)
        self.uiImportPushButton.clicked.connect(self._importPushButtonClickedSlot)
        self.uiApplianceVersionTreeWidget.currentItemChanged.connect(self._applianceVersionCurrentItemChangedSlot)
        self.uiCreateVersionPushButton.clicked.connect(self._createVersionPushButtonClickedSlot)
        self.allowCustomFiles.clicked.connect(self._allowCustomFilesChangedSlot)

        #FIXME: deactivate the create version feature (confusing and maybe not necessary, TBD)
        self.uiCreateVersionPushButton.hide()

        # directories where to search for images
        images_directories = list()
        images_directories.append(os.path.dirname(self._path))
        download_directory = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)
        if download_directory != "" and download_directory != os.path.dirname(self._path):
            images_directories.append(download_directory)

        for emulator in ("QEMU", "IOU", "DYNAMIPS"):
            emulator_images_dir = ImageManager.instance().getDirectoryForType(emulator)
            if os.path.exists(emulator_images_dir):
                images_directories.append(emulator_images_dir)

        # registry to search for images
        self._registry = Registry(images_directories)
        self._registry.image_list_changed_signal.connect(self.images_changed_signal.emit)

        # appliance object
        self._appliance = Appliance(self._registry, self._path)
        self.setWindowTitle("Install {} appliance".format(self._appliance["name"]))

        # add a custom button to show appliance information
        self.setButtonText(QtWidgets.QWizard.CustomButton1, "&Appliance info")
        self.setOption(QtWidgets.QWizard.HaveCustomButton1, True)
        self.customButtonClicked.connect(self._showApplianceInfoSlot)

        # customize the server selection
        self.uiRemoteRadioButton.toggled.connect(self._remoteServerToggledSlot)
        if hasattr(self, "uiVMRadioButton"):
            self.uiVMRadioButton.toggled.connect(self._vmToggledSlot)

        self.uiLocalRadioButton.toggled.connect(self._localToggledSlot)
        if Controller.instance().isRemote():
            self.uiLocalRadioButton.setText("Install the appliance on the main server")
        else:
            if not path.endswith('.builtin.gns3a'):
                destination = None
                try:
                    destination = Config().appliances_dir
                except OSError as e:
                    QtWidgets.QMessageBox.critical(self.parent(), "Add appliance", "Could not find configuration file: {}".format(e))
                except ValueError as e:
                    QtWidgets.QMessageBox.critical(self.parent(), "Add appliance", "Invalid configuration file: {}".format(e))
                if destination:
                    try:
                        os.makedirs(destination, exist_ok=True)
                        destination = os.path.join(destination, os.path.basename(path))
                        shutil.copy(path, destination)
                    except OSError as e:
                        QtWidgets.QMessageBox.warning(self.parent(), "Cannot copy {} to {}".format(path, destination), str(e))

        self.uiServerWizardPage.isComplete = self._uiServerWizardPage_isComplete

    def initializePage(self, page_id):
        """
        Initialize wizard pages.

        :param page_id: page identifier
        """

        super().initializePage(page_id)

        # add symbol
        if self._appliance["category"] == "guest":
            symbol = ":/symbols/computer.svg"
        else:
            symbol = ":/symbols/{}.svg".format(self._appliance["category"])
        self.page(page_id).setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(symbol))

        if self.page(page_id) == self.uiServerWizardPage:

            Controller.instance().getSymbols(self._getSymbolsCallback)

            if "qemu" in self._appliance:
                emulator_type = "qemu"
            elif "iou" in self._appliance:
                emulator_type = "iou"
            elif "docker" in self._appliance:
                emulator_type = "docker"
            elif "dynamips" in self._appliance:
                emulator_type = "dynamips"
            else:
                QtWidgets.QMessageBox.warning(self, "Appliance", "Could not determine the emulator type")

            is_mac = ComputeManager.instance().localPlatform().startswith("darwin")
            is_win = ComputeManager.instance().localPlatform().startswith("win")

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
            elif is_mac or is_win:
                if emulator_type == "qemu":
                    # disallow usage of the local server because Qemu has issues on OSX and Windows
                    if not LocalConfig.instance().experimental():
                        self.uiLocalRadioButton.setEnabled(False)
                elif emulator_type != "dynamips":
                    self.uiLocalRadioButton.setEnabled(False)

            if ComputeManager.instance().vmCompute():
                self.uiVMRadioButton.setChecked(True)
            elif ComputeManager.instance().localCompute() and self.uiLocalRadioButton.isEnabled():
                self.uiLocalRadioButton.setChecked(True)
            elif self.uiRemoteRadioButton.isEnabled():
                self.uiRemoteRadioButton.setChecked(True)
            else:
                self.uiRemoteRadioButton.setChecked(False)

            if is_mac or is_win:
                if not self.uiRemoteRadioButton.isEnabled() and not self.uiVMRadioButton.isEnabled() and not self.uiLocalRadioButton.isEnabled():
                    QtWidgets.QMessageBox.warning(self, "GNS3 VM", "The GNS3 VM is not available, please configure the GNS3 VM before adding a new appliance.")

        elif self.page(page_id) == self.uiFilesWizardPage:
            if self._compute_id != "local":
                self._registry.getRemoteImageList(self._appliance.emulator(), self._compute_id)

        elif self.page(page_id) == self.uiQemuWizardPage:
            if self._appliance['qemu'].get('kvm', 'require') == 'require':
                self._server_check = False
                Qemu.instance().getQemuCapabilitiesFromServer(self._compute_id, qpartial(self._qemuServerCapabilitiesCallback))
            else:
                self._server_check = True
            Qemu.instance().getQemuBinariesFromServer(self._compute_id, qpartial(self._getQemuBinariesFromServerCallback), [self._appliance["qemu"]["arch"]])

        elif self.page(page_id) == self.uiUsageWizardPage:
            self.uiUsageTextEdit.setText("The template will be available in the {} category.\n\n{}".format(self._appliance["category"].replace("_", " "), self._appliance.get("usage", "")))

    def _qemuServerCapabilitiesCallback(self, result, error=None, *args, **kwargs):
        """
        Check if the server supports KVM or not
        """

        if error is None and "kvm" in result and self._appliance["qemu"]["arch"] in result["kvm"]:
            self._server_check = True
        else:
            if error:
                msg = result["message"]
            else:
                msg = "The selected server does not support KVM. A Linux server or the GNS3 VM running in VMware is required."
            QtWidgets.QMessageBox.critical(self, "KVM support", msg)
            self._server_check = False

    def _uiServerWizardPage_isComplete(self):
        return self.uiRemoteRadioButton.isEnabled() or self.uiVMRadioButton.isEnabled() or self.uiLocalRadioButton.isEnabled()

    def _imageUploadedCallback(self, result, error=False, context=None, **kwargs):
        if context is None:
            context = {}
        image_path = context.get("image_path", "unknown")
        if error:
            log.error("Error while uploading image '{}': {}".format(image_path, result["message"]))
        else:
            log.info("Image '{}' has been successfully uploaded".format(image_path))
            self._registry.getRemoteImageList(self._appliance.emulator(), self._compute_id)

    def _showApplianceInfoSlot(self):
        """
        Shows appliance information.
        """

        info = (("Product", "product_name"),
                ("Vendor", "vendor_name"),
                ("Availability", "availability"),
                ("Status", "status"),
                ("Maintainer", "maintainer"))

        if "qemu" in self._appliance:
            qemu_info = (("vCPUs", "qemu/cpus"),
                         ("RAM", "qemu/ram"),
                         ("Adapters", "qemu/adapters"),
                         ("Adapter type", "qemu/adapter_type"),
                         ("Console type", "qemu/console_type"),
                         ("Architecture", "qemu/arch"),
                         ("Console type", "qemu/console_type"),
                         ("KVM", "qemu/kvm"))
            info = info + qemu_info

        elif "docker" in self._appliance:
            docker_info = (("Image", "docker/image"),
                           ("Adapters", "docker/adapters"),
                           ("Console type", "docker/console_type"))
            info = info + docker_info

        elif "iou" in self._appliance:
            iou_info = (("RAM", "iou/ram"),
                        ("NVRAM", "iou/nvram"),
                        ("Ethernet adapters", "iou/ethernet_adapters"),
                        ("Serial adapters", "iou/serial_adapters"))
            info = info + iou_info

        elif "dynamips" in self._appliance:
            dynamips_info = (("Platform", "dynamips/platform"),
                             ("Chassis", "dynamips/chassis"),
                             ("Midplane", "dynamips/midplane"),
                             ("NPE", "dynamips/npe"),
                             ("RAM", "dynamips/ram"),
                             ("NVRAM", "dynamips/nvram"),
                             ("slot0", "dynamips/slot0"),
                             ("slot1", "dynamips/slot1"),
                             ("slot2", "dynamips/slot2"),
                             ("slot3", "dynamips/slot3"),
                             ("slot4", "dynamips/slot4"),
                             ("slot5", "dynamips/slot5"),
                             ("slot6", "dynamips/slot6"),
                             ("wic0", "dynamips/wic0"),
                             ("wic1", "dynamips/wic1"),
                             ("wic2", "dynamips/wic2"))
            info = info + dynamips_info

        text_info = ""
        for (name, key) in info:
            if "/" in key:
                key, subkey = key.split("/")
                value = self._appliance.get(key, {}).get(subkey, None)
            else:
                value = self._appliance.get(key, None)
            if value is None:
                continue
            text_info += "<span style='font-weight:bold;'>{}</span>: {}<br>".format(name, value)

        msgbox = QtWidgets.QMessageBox(self)
        msgbox.setWindowTitle("Appliance information")
        msgbox.setStyleSheet("QLabel{min-width: 600px;}") # TODO: resize details box QTextEdit{min-height: 500px;}
        msgbox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        msgbox.setText(text_info)
        msgbox.setDetailedText(self._appliance["description"])
        msgbox.exec_()

    @qslot
    def _refreshVersions(self, *args):
        """
        Refresh the list of files for different versions of the appliance
        """

        if self._refreshing:
            return
        self._refreshing = True

        self.uiFilesWizardPage.setSubTitle("Please select one version of " + self._appliance["product_name"] + " and import the required files. Files are searched in your downloads and GNS3 images directories by default")
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
            top = QtWidgets.QTreeWidgetItem(self.uiApplianceVersionTreeWidget, ["{} version {}".format(self._appliance["product_name"], version["name"])])
            size = 0
            status = "Ready to install"
            for image in version["images"].values():
                if image["status"] == "Missing":
                    status = "Missing files"

                size += image.get("filesize", 0)
                image_widget = QtWidgets.QTreeWidgetItem([image["filename"],
                                                          human_filesize(image.get("filesize", 0)),
                                                          image["status"]])
                if image["status"] == "Missing":
                    image_widget.setForeground(2, QtGui.QBrush(QtGui.QColor("red")))
                else:
                    image_widget.setForeground(2, QtGui.QBrush(QtGui.QColor("green")))
                    image_widget.setToolTip(2, image["path"])

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
                top.setForeground(2, QtGui.QBrush(QtGui.QColor("red")))
            else:
                expand = False
                top.setForeground(2, QtGui.QBrush(QtGui.QColor("green")))

            top.setData(1, QtCore.Qt.DisplayRole, human_filesize(size))
            top.setData(2, QtCore.Qt.DisplayRole, status)
            top.setData(0, QtCore.Qt.UserRole, version)
            top.setData(2, QtCore.Qt.UserRole, self._appliance)
            self.uiApplianceVersionTreeWidget.addTopLevelItem(top)
            if expand:
                top.setExpanded(True)

        if len(self._appliance["versions"]) > 0:
            for column in range(self.uiApplianceVersionTreeWidget.columnCount()):
                self.uiApplianceVersionTreeWidget.resizeColumnToContents(column)

        self._refreshing = False

    def _getSymbolsCallback(self, result, error=False, **kwargs):
        """
        Callback to retrieve the appliance symbols.
        """

        if error:
            log.warning("Cannot load symbols from controller")
        else:
            self._symbols = result

    def _refreshDialogWorker(self):
        """
        Scan local directory in order to find images on the disk
        """

        # Docker do not have versions
        if "versions" not in self._appliance:
            return

        for version in self._appliance["versions"]:
            for image in version["images"].values():
                img = self._registry.search_image_file(self._appliance.emulator(),
                                                       image["filename"],
                                                       image.get("md5sum"),
                                                       image.get("filesize"),
                                                       strict_md5_check=not self.allowCustomFiles.isChecked())
                if img:
                    if img.location == "local":
                        image["status"] = "Found locally"
                    else:
                        image["status"] = "Found on {}".format(self._compute_id)
                    image["md5sum"] = img.md5sum
                    image["filesize"] = img.filesize
                    image["path"] = img.path
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
        Called when user wants to download an appliance image.
        The file should be selected first.
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
                    QtWidgets.QMessageBox.warning(self, "Add appliance", "The file is compressed with '{}', it must be uncompressed first".format(data["compression"]))
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
        Called when user wants to import an appliance images.
        The file should be selected first.
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
                reply = QtWidgets.QMessageBox.question(self, "Add appliance",
                                                       "This is not the correct file. The MD5 sum is {} and should be {}.\nDo you want to accept it at your own risks?".format(image.md5sum, disk["md5sum"]),
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.No:
                    return
        except OSError as e:
            QtWidgets.QMessageBox.warning(self.parent(), "Add appliance", "Can't access to the image file {}: {}.".format(path, str(e)))
            return

        image_upload_manger = ImageUploadManager(image, Controller.instance(), self._compute_id, self._imageUploadedCallback, LocalConfig.instance().directFileUpload())
        image_upload_manger.upload()

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
        Install the appliance in GNS3

        :params version: appliance version name
        """

        if version is None:
            appliance_configuration = self._appliance.copy()
            if "docker" not in appliance_configuration:
                # only Docker do not have version
                return False
        else:
            try:
                appliance_configuration = self._appliance.search_images_for_version(version)
            except ApplianceError as e:
                QtWidgets.QMessageBox.critical(self.parent(), "Add appliance", str(e))
                return False

        template_manager = TemplateManager().instance()
        while len(appliance_configuration["name"]) == 0 or not template_manager.is_name_available(appliance_configuration["name"]):
            QtWidgets.QMessageBox.warning(self.parent(), "Add template", "The name \"{}\" is already used by another template".format(appliance_configuration["name"]))
            appliance_configuration["name"], ok = QtWidgets.QInputDialog.getText(self.parent(), "Add template", "New name:", QtWidgets.QLineEdit.Normal, appliance_configuration["name"])
            if not ok:
                return False
            appliance_configuration["name"] = appliance_configuration["name"].strip()

        if "qemu" in appliance_configuration:
            appliance_configuration["qemu"]["path"] = self.uiQemuListComboBox.currentData()

        new_template = ApplianceToTemplate().new_template(appliance_configuration, self._compute_id, self._symbols)
        TemplateManager.instance().createTemplate(Template(new_template), callback=self._templateCreatedCallback)
        return False

        #worker = WaitForLambdaWorker(lambda: self._create_template(appliance_configuration, self._compute_id), allowed_exceptions=[ConfigException, OSError])
        #progress_dialog = ProgressDialog(worker, "Add template", "Installing a new template...", None, busy=True, parent=self)
        #progress_dialog.show()
        #if progress_dialog.exec_():
        #    QtWidgets.QMessageBox.information(self.parent(), "Add template", "{} template has been installed!".format(appliance_configuration["name"]))
        #    return True
        #return False

        # worker = WaitForLambdaWorker(lambda: config.save(), allowed_exceptions=[ConfigException, OSError])
        # progress_dialog = ProgressDialog(worker, "Add appliance", "Install the appliance...", None, busy=True, parent=self)
        # progress_dialog.show()
        # if progress_dialog.exec_():
        #     QtWidgets.QMessageBox.information(self.parent(), "Add appliance", "{} installed!".format(appliance_configuration["name"]))
        #     return True

    def _templateCreatedCallback(self, result, error=False, **kwargs):

        if error is True:
            QtWidgets.QMessageBox.critical(self.parent(), "Add template", "The template cannot be created: {}".format(result.get("message", "unknown")))
            return

        QtWidgets.QMessageBox.information(self.parent(), "Add template", "The appliance has been installed and a template named '{}' has been successfully created!".format(result["name"]))
        self._template_created = True
        self.done(True)

    def _uploadImages(self, name, version):
        """
        Upload an image the compute.
        """

        try:
            appliance_configuration = self._appliance.search_images_for_version(version)
        except ApplianceError as e:
            QtWidgets.QMessageBox.critical(self, "Appliance","Cannot install {} version {}: {}".format(name, version, e))
            return
        for image in appliance_configuration["images"]:
            if image["location"] == "local":
                image = Image(self._appliance.emulator(), image["path"], filename=image["filename"])
                image_upload_manger = ImageUploadManager(image, Controller.instance(), self._compute_id, self._applianceImageUploadedCallback, LocalConfig.instance().directFileUpload())
                image_upload_manger.upload()
                self._image_uploading_count += 1

    def _applianceImageUploadedCallback(self, result, error=False, context=None, **kwargs):
        if context is None:
            context = {}
        image_path = context.get("image_path", "unknown")
        if error:
            log.error("Error while uploading image '{}': {}".format(image_path, result["message"]))
        else:
            log.info("Image '{}' has been successfully uploaded".format(image_path))
            self._image_uploading_count -= 1

    def nextId(self):
        if self.currentPage() == self.uiServerWizardPage:
            if "docker" in self._appliance:
                # skip Qemu binary selection and files pages if this is a Docker appliance
                return super().nextId() + 2
            elif "qemu" not in self._appliance:
                # skip the Qemu binary selection page if not a Qemu appliance
                return super().nextId() + 1
        return super().nextId()

    def validateCurrentPage(self):
        """
        Validates the settings.
        """

        if self.currentPage() == self.uiFilesWizardPage:
            # validate the files page

            if self._refreshing:
                return False
            current = self.uiApplianceVersionTreeWidget.currentItem()
            if current is None or sip.isdeleted(current):
                return False
            version = current.data(0, QtCore.Qt.UserRole)
            if version is None:
                return False
            appliance = current.data(2, QtCore.Qt.UserRole)
            try:
                self._appliance.search_images_for_version(version["name"])
            except ApplianceError as e:
                QtWidgets.QMessageBox.critical(self, "Appliance", "Cannot install {} version {}: {}".format(appliance["name"], version["name"], e))
                return False
            reply = QtWidgets.QMessageBox.question(self, "Appliance", "Would you like to install {} version {}?".format(appliance["name"], version["name"]),
                                                   QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                return False

            self._uploadImages(appliance["name"], version["name"])

        elif self.currentPage() == self.uiUsageWizardPage:
            # validate the usage page

            if self._template_created:
                return True
            if self._image_uploading_count > 0:
                QtWidgets.QMessageBox.critical(self, "Add appliance", "Please wait for appliance files to be uploaded")
                return False
            current = self.uiApplianceVersionTreeWidget.currentItem()
            if current:
                version = current.data(0, QtCore.Qt.UserRole)
                return self._install(version["name"])
            else:
                return self._install(None)

        elif self.currentPage() == self.uiServerWizardPage:
            # validate the server page

            if self.uiRemoteRadioButton.isChecked():
                if len(ComputeManager.instance().remoteComputes()) == 0:
                    QtWidgets.QMessageBox.critical(self, "Remote server", "There is no remote servers configured in your preferences")
                    return False
                self._compute_id = self.uiRemoteServersComboBox.itemData(self.uiRemoteServersComboBox.currentIndex()).id()
            elif hasattr(self, "uiVMRadioButton") and self.uiVMRadioButton.isChecked():
                self._compute_id = "vm"
            else:
                if ComputeManager.instance().localPlatform():
                    if (ComputeManager.instance().localPlatform().startswith("darwin") or ComputeManager.instance().localPlatform().startswith("win")):
                        if "qemu" in self._appliance:
                            reply = QtWidgets.QMessageBox.question(self, "Appliance", "Qemu on Windows and macOS is not supported by the GNS3 team. Do you want to continue?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                            if reply == QtWidgets.QMessageBox.No:
                                return False
                self._compute_id = "local"

        elif self.currentPage() == self.uiQemuWizardPage:
            # validate the Qemu

            if self._server_check is False:
                QtWidgets.QMessageBox.critical(self, "Checking for KVM support", "Please wait for the server to reply...")
                return False
            if self.uiQemuListComboBox.currentIndex() == -1:
                QtWidgets.QMessageBox.critical(self, "Qemu binary", "No compatible Qemu binary selected")
                return False
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

    @qslot
    def _allowCustomFilesChangedSlot(self, checked):
        """
        Slot for when user want to upload images which don't match md5

        :param checked: if allows or doesn't allow custom files
        :return:
        """
        if checked:
            reply = QtWidgets.QMessageBox.question(self, "Custom files",
                "This option allows files with different MD5 checksums. This feature is only for advanced users and can lead "
                "to unexpected problems. Do you want to proceed?",
                QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

            if reply == QtWidgets.QMessageBox.No:
                self.allowCustomFiles.setChecked(False)
                return False
