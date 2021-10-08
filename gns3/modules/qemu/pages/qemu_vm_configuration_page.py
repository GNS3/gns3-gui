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
Configuration page for QEMU VMs.
"""

import os
import re

from collections import OrderedDict
from gns3.modules.qemu.dialogs.qemu_image_wizard import QemuImageWizard
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.ports.port_name_factory import StandardPortNameFactory
from gns3.dialogs.custom_adapters_configuration_dialog import CustomAdaptersConfigurationDialog
from gns3.node import Node
from gns3.qt import QtCore, QtWidgets, qpartial, sip_is_deleted
from gns3.dialogs.node_properties_dialog import ConfigurationError
from gns3.image_manager import ImageManager

from ..ui.qemu_vm_configuration_page_ui import Ui_QemuVMConfigPageWidget
from .. import Qemu


class QemuVMConfigurationPage(QtWidgets.QWidget, Ui_QemuVMConfigPageWidget):
    """
    QWidget configuration page for QEMU VMs.
    """

    _default_images_dir = ""

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self._compute_id = None
        self._settings = None
        self._custom_adapters = []

        self.uiBootPriorityComboBox.addItem("HDD", "c")
        self.uiBootPriorityComboBox.addItem("CD/DVD-ROM", "d")
        self.uiBootPriorityComboBox.addItem("Network", "n")
        self.uiBootPriorityComboBox.addItem("HDD or Network", "cn")
        self.uiBootPriorityComboBox.addItem("HDD or CD/DVD-ROM", "cd")
        self.uiBootPriorityComboBox.addItem("CD/DVD-ROM or Network", "dn")
        self.uiBootPriorityComboBox.addItem("CD/DVD-ROM or HDD", "dc")
        self.uiBootPriorityComboBox.addItem("Network or HDD", "nc")
        self.uiBootPriorityComboBox.addItem("Network or CD/DVD-ROM", "nd")

        self.uiHdaDiskImageToolButton.clicked.connect(self._hdaDiskImageBrowserSlot)
        self.uiHdbDiskImageToolButton.clicked.connect(self._hdbDiskImageBrowserSlot)
        self.uiHdcDiskImageToolButton.clicked.connect(self._hdcDiskImageBrowserSlot)
        self.uiHddDiskImageToolButton.clicked.connect(self._hddDiskImageBrowserSlot)
        self.uiCdromImageToolButton.clicked.connect(self._cdromImageBrowserSlot)
        self.uiBiosImageToolButton.clicked.connect(self._biosImageBrowserSlot)

        self.uiHdaDiskImageCreateToolButton.clicked.connect(self._hdaDiskImageCreateSlot)
        self.uiHdbDiskImageCreateToolButton.clicked.connect(self._hdbDiskImageCreateSlot)
        self.uiHdcDiskImageCreateToolButton.clicked.connect(self._hdcDiskImageCreateSlot)
        self.uiHddDiskImageCreateToolButton.clicked.connect(self._hddDiskImageCreateSlot)

        self.uiHdaDiskImageResizeToolButton.clicked.connect(self._hdaDiskImageResizeSlot)
        self.uiHdbDiskImageResizeToolButton.clicked.connect(self._hdbDiskImageResizeSlot)
        self.uiHdcDiskImageResizeToolButton.clicked.connect(self._hdcDiskImageResizeSlot)
        self.uiHddDiskImageResizeToolButton.clicked.connect(self._hddDiskImageResizeSlot)

        disk_interfaces = ["ide", "sata", "nvme", "scsi", "sd", "mtd", "floppy", "pflash", "virtio", "none"]
        self.uiHdaDiskInterfaceComboBox.addItems(disk_interfaces)
        self.uiHdbDiskInterfaceComboBox.addItems(disk_interfaces)
        self.uiHdcDiskInterfaceComboBox.addItems(disk_interfaces)
        self.uiHddDiskInterfaceComboBox.addItems(disk_interfaces)

        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)
        self.uiInitrdToolButton.clicked.connect(self._initrdBrowserSlot)
        self.uiKernelImageToolButton.clicked.connect(self._kernelImageBrowserSlot)
        self.uiActivateCPUThrottlingCheckBox.stateChanged.connect(self._cpuThrottlingChangedSlot)
        self.uiLegacyNetworkingCheckBox.stateChanged.connect(self._legacyNetworkingChangedSlot)
        self.uiCustomAdaptersConfigurationPushButton.clicked.connect(self._customAdaptersConfigurationSlot)
        self.uiCreateConfigDiskCheckBox.stateChanged.connect(self._createConfigDiskChangedSlot)

        # add the categories
        for name, category in Node.defaultCategories().items():
            self.uiCategoryComboBox.addItem(name, category)

        # add the on close options
        for name, option_name in Node.onCloseOptions().items():
            self.uiOnCloseComboBox.addItem(name, option_name)

        # Supported NIC models: e1000, e1000-82544gc, e1000-82545em, e1000e, i82550, i82551, i82557a, i82557b, i82557c, i82558a
        # i82558b, i82559a, i82559b, i82559c, i82559er, i82562, i82801, ne2k_pci, pcnet, rocker, rtl8139, virtio-net-pci, vmxnet3
        # This list can be retrieved using "qemu-system-x86_64 -nic model=?" or "qemu-system-x86_64 -device help"
        self._legacy_devices = ("e1000", "i82551", "i82557b", "i82559er", "ne2k_pci", "pcnet", "rtl8139", "virtio")
        self._qemu_network_devices = OrderedDict([("e1000", "Intel Gigabit Ethernet"),
                                                  ("e1000-82544gc", "Intel 82544GC Gigabit Ethernet"),
                                                  ("e1000-82545em", "Intel 82545EM Gigabit Ethernet"),
                                                  ("e1000e", "Intel PCIe Gigabit Ethernet"),
                                                  ("i82550", "Intel i82550 Ethernet"),
                                                  ("i82551", "Intel i82551 Ethernet"),
                                                  ("i82557a", "Intel i82557A Ethernet"),
                                                  ("i82557b", "Intel i82557B Ethernet"),
                                                  ("i82557c", "Intel i82557C Ethernet"),
                                                  ("i82558a", "Intel i82558A Ethernet"),
                                                  ("i82558b", "Intel i82558B Ethernet"),
                                                  ("i82559a", "Intel i82559A Ethernet"),
                                                  ("i82559b", "Intel i82559B Ethernet"),
                                                  ("i82559c", "Intel i82559C Ethernet"),
                                                  ("i82559er", "Intel i82559ER Ethernet"),
                                                  ("i82562", "Intel i82562 Ethernet"),
                                                  ("i82801", "Intel i82801 Ethernet"),
                                                  ("ne2k_pci", "NE2000 Ethernet"),
                                                  ("pcnet", "AMD PCNet Ethernet"),
                                                  ("rocker", "Rocker L2 switch device"),
                                                  ("rtl8139", "Realtek 8139 Ethernet"),
                                                  ("virtio", "Legacy paravirtualized Network I/O"),
                                                  ("virtio-net-pci", "Paravirtualized Network I/O"),
                                                  ("vmxnet3", "VMWare Paravirtualized Ethernet v3")])

        self._refreshQemuNetworkDevices()

    def _symbolBrowserSlot(self):
        """
        Slot to open the symbol browser and select a new symbol.
        """

        symbol_path = self.uiSymbolLineEdit.text()
        dialog = SymbolSelectionDialog(self, symbol=symbol_path)
        dialog.show()
        if dialog.exec_():
            new_symbol_path = dialog.getSymbol()
            self.uiSymbolLineEdit.setText(new_symbol_path)
            self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(new_symbol_path))

    def _refreshQemuNetworkDevices(self, legacy_networking=False):
        """
        Refreshes the Qemu network device list.

        :param legacy_networking: True if legacy networking is enabled.
        """

        self.uiAdapterTypesComboBox.clear()
        for device_name, device_description in self._qemu_network_devices.items():
            if legacy_networking and device_name not in self._legacy_devices:
                continue
            # special case for virtio legacy networking
            if not legacy_networking and device_name == "virtio":
                continue
            self.uiAdapterTypesComboBox.addItem("{} ({})".format(device_description, device_name), device_name)

    @staticmethod
    def getImageDirectory():
        return ImageManager.instance().getDirectoryForType("QEMU")

    @classmethod
    def getDiskImage(cls, parent, server):

        if not cls._default_images_dir:
            cls._default_images_dir = cls.getImageDirectory()

        path, _ = QtWidgets.QFileDialog.getOpenFileName(parent, "Select a QEMU disk image", cls._default_images_dir)
        if not path:
            return
        cls._default_images_dir = os.path.dirname(path)

        if not os.access(path, os.R_OK):
            QtWidgets.QMessageBox.critical(parent, "QEMU disk image", "Cannot read {}".format(path))
            return

        path = ImageManager.instance().askCopyUploadImage(parent, path, server, "QEMU")

        return path

    def _hdaDiskImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU hda disk image.
        """

        path = self.getDiskImage(self, self._compute_id)
        if path:
            self.uiHdaDiskImageLineEdit.clear()
            self.uiHdaDiskImageLineEdit.setText(path)

    def _hdbDiskImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU hdb disk image.
        """

        path = self.getDiskImage(self, self._compute_id)
        if path:
            self.uiHdbDiskImageLineEdit.clear()
            self.uiHdbDiskImageLineEdit.setText(path)

    def _hdcDiskImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU hdc disk image.
        """

        path = self.getDiskImage(self, self._compute_id)
        if path:
            self.uiHdcDiskImageLineEdit.clear()
            self.uiHdcDiskImageLineEdit.setText(path)

    def _hddDiskImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU hdd disk image.
        """

        path = self.getDiskImage(self, self._compute_id)
        if path:
            self.uiHddDiskImageLineEdit.clear()
            self.uiHddDiskImageLineEdit.setText(path)

    def _biosImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU bios image.
        """

        path = self.getDiskImage(self, self._compute_id)
        if path:
            self.uiBiosImageLineEdit.clear()
            self.uiBiosImageLineEdit.setText(path)

    def _cdromImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU CD/DVD-ROM image.
        """

        path = self.getDiskImage(self, self._compute_id)
        if path:
            self.uiCdromImageLineEdit.clear()
            self.uiCdromImageLineEdit.setText(path)

    def _hdaDiskImageCreateSlot(self):
        create_dialog = QemuImageWizard(self, self._compute_id, self.uiNameLineEdit.text() + '-hda')
        if QtWidgets.QDialog.Accepted == create_dialog.exec_():
            self.uiHdaDiskImageLineEdit.setText(create_dialog.uiLocationLineEdit.text())

    def _hdbDiskImageCreateSlot(self):
        create_dialog = QemuImageWizard(self, self._compute_id, self.uiNameLineEdit.text() + '-hdb')
        if QtWidgets.QDialog.Accepted == create_dialog.exec_():
            self.uiHdbDiskImageLineEdit.setText(create_dialog.uiLocationLineEdit.text())

    def _hdcDiskImageCreateSlot(self):
        create_dialog = QemuImageWizard(self, self._compute_id, self.uiNameLineEdit.text() + '-hdc')
        if QtWidgets.QDialog.Accepted == create_dialog.exec_():
            self.uiHdcDiskImageLineEdit.setText(create_dialog.uiLocationLineEdit.text())

    def _hddDiskImageCreateSlot(self):
        create_dialog = QemuImageWizard(self, self._compute_id, self.uiNameLineEdit.text() + '-hdd')
        if QtWidgets.QDialog.Accepted == create_dialog.exec_():
            self.uiHddDiskImageLineEdit.setText(create_dialog.uiLocationLineEdit.text())

    def _resizeDiskImageCallback(self, result, error=False, **kwargs):
        """
        Callback for resizing a disk image in a VM.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "Disk image", "{}".format(result["message"]))
        else:
            QtWidgets.QMessageBox.information(self, "Disk image", "The disk has been resized")

    def _hdaDiskImageResizeSlot(self):
        size, ok = QtWidgets.QInputDialog.getInt(self, "HDA disk size", "Increase hda disk size in MB:", 10000, 1, 1000000000, 1000)
        if ok and self._node:
            self._node.resizeDiskImage("hda", size, self._resizeDiskImageCallback)

    def _hdbDiskImageResizeSlot(self):
        size, ok = QtWidgets.QInputDialog.getInt(self, "HDB disk size", "Increase hdb disk size in MB:", 10000, 1, 1000000000, 1000)
        if ok and self._node:
            self._node.resizeDiskImage("hdb", size, self._resizeDiskImageCallback)

    def _hdcDiskImageResizeSlot(self):
        size, ok = QtWidgets.QInputDialog.getInt(self, "HDC disk size", "Increase hdc disk size in MB:", 10000, 1, 1000000000, 1000)
        if ok and self._node:
            self._node.resizeDiskImage("hdc", size, self._resizeDiskImageCallback)

    def _hddDiskImageResizeSlot(self):
        size, ok = QtWidgets.QInputDialog.getInt(self, "HDD disk size", "Increase hdd disk size in MB:", 10000, 1, 1000000000, 1000)
        if ok and self._node:
            self._node.resizeDiskImage("hdd", size, self._resizeDiskImageCallback)

    def _initrdBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU initrd.
        """

        path = self.getDiskImage(self, self._compute_id)
        if path:
            self.uiInitrdLineEdit.clear()
            self.uiInitrdLineEdit.setText(path)

    def _kernelImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU kernel image.
        """

        path = self.getDiskImage(self, self._compute_id)
        if path:
            self.uiKernelImageLineEdit.clear()
            self.uiKernelImageLineEdit.setText(path)

    def _getQemuBinariesFromServerCallback(self, result, error=False, qemu_path=None, **kwargs):
        """
        Callback for getQemuBinariesFromServer.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if sip_is_deleted(self.uiQemuListComboBox) or sip_is_deleted(self):
            return

        if error:
            QtWidgets.QMessageBox.critical(self, "Qemu binaries", "{}".format(result["message"]))
        else:
            self.uiQemuListComboBox.clear()
            for qemu in result:
                if qemu["version"]:
                    self.uiQemuListComboBox.addItem("{path} (v{version})".format(path=qemu["path"], version=qemu["version"]), qemu["path"])
                else:
                    self.uiQemuListComboBox.addItem("{path}".format(path=qemu["path"]), qemu["path"])

        if qemu_path and "/" not in qemu_path and "\\" not in qemu_path:
            self.uiQemuListComboBox.addItem("{path}".format(path=qemu_path), qemu_path)

        index = self.uiQemuListComboBox.findData("{path}".format(path=qemu_path))
        if index != -1:
            self.uiQemuListComboBox.setCurrentIndex(index)
        else:
            index = self.uiQemuListComboBox.findData("{path}".format(path=os.path.basename(qemu_path)), flags=QtCore.Qt.MatchEndsWith)
            self.uiQemuListComboBox.setCurrentIndex(index)
            if index == -1:
                QtWidgets.QMessageBox.warning(self, "Qemu","Could not find '{}' in the Qemu binaries list, please select a new binary".format(qemu_path))
            else:
                QtWidgets.QMessageBox.warning(self, "Qemu","Could not find '{}' in the Qemu binaries list, an alternative path has been selected".format(qemu_path))

    def _cpuThrottlingChangedSlot(self, state):
        """
        Slot to enable or not CPU throttling.
        """

        if state:
            self.uiCPUThrottlingSpinBox.setEnabled(True)
        else:
            self.uiCPUThrottlingSpinBox.setEnabled(False)

    def _legacyNetworkingChangedSlot(self, state):
        """
        Slot to enable or not legacy networking.
        """

        if state:
            self._refreshQemuNetworkDevices(legacy_networking=True)
        else:
            self._refreshQemuNetworkDevices()

    def _createConfigDiskChangedSlot(self, state):
        """
        Slot to allow or not HDD disk to be configured based on the state of the config disk option.
        """

        _translate = QtCore.QCoreApplication.translate
        if state:
            self.uiHddDiskImageLabel.setText(_translate("QemuVMConfigPageWidget", "Startup-cfg:"))
        else:
            self.uiHddDiskImageLabel.setText(_translate("QemuVMConfigPageWidget", "Disk image:"))
        self.uiHddDiskImageCreateToolButton.setEnabled(not state)
        self.uiHddDiskImageResizeToolButton.setEnabled(not state)

    def _customAdaptersConfigurationSlot(self):
        """
        Slot to open the custom adapters configuration dialog
        """

        if self._node:
            first_port_name = self._settings["first_port_name"]
            port_segment_size = self._settings["port_segment_size"]
            port_name_format = self._settings["port_name_format"]
            adapters = self._settings["adapters"]
            default_adapter = self._settings["adapter_type"]
            base_mac_address = self._settings["mac_address"]
        else:
            first_port_name = self.uiFirstPortNameLineEdit.text().strip()
            port_name_format = self.uiPortNameFormatLineEdit.text()
            port_segment_size = self.uiPortSegmentSizeSpinBox.value()
            adapters = self.uiAdaptersSpinBox.value()
            default_adapter = self.uiAdapterTypesComboBox.currentData()

            mac = self.uiMacAddrLineEdit.text()
            if mac != ":::::":
                if not re.search(r"""^([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$""", mac):
                    QtWidgets.QMessageBox.critical(self, "MAC address", "Invalid MAC address (format required: hh:hh:hh:hh:hh:hh)")
                    return
                else:
                    base_mac_address = mac
            else:
                base_mac_address = ""

        try:
            ports = StandardPortNameFactory(adapters, first_port_name, port_name_format, port_segment_size)
        except (IndexError, ValueError, KeyError):
            QtWidgets.QMessageBox.critical(self, "Invalid format", "Invalid port name format")
            return

        if self.uiLegacyNetworkingCheckBox.isChecked():
            network_devices = {}
            for nic, desc in self._qemu_network_devices.items():
                if nic in self._legacy_devices:
                    network_devices[nic] = desc
        else:
            network_devices = self._qemu_network_devices.copy()
            # special case for virtio legacy networking
            network_devices.pop("virtio")

        dialog = CustomAdaptersConfigurationDialog(ports, self._custom_adapters, default_adapter, network_devices, base_mac_address, parent=self)
        dialog.show()
        dialog.exec_()

    def loadSettings(self, settings, node=None, group=False):
        """
        Loads the QEMU VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        if node:
            self._compute_id = node.compute().id()
            self._node = node
            self._settings = settings
        else:
            self._compute_id = settings["compute_id"]
            self._node = None

        if self._compute_id is None:
            QtWidgets.QMessageBox.warning(self, "Qemu", "Server {} is not running, cannot retrieve the QEMU binaries list".format(settings["compute_id"]))
        else:
            callback = qpartial(self._getQemuBinariesFromServerCallback, qemu_path=settings["qemu_path"])
            Qemu.instance().getQemuBinariesFromServer(self._compute_id, callback)

        if not group:
            # set the device name
            self.uiNameLineEdit.setText(settings["name"])

            if "linked_clone" in settings:
                self.uiBaseVMCheckBox.setChecked(settings["linked_clone"])
            else:
                self.uiBaseVMCheckBox.hide()

            self.uiHdaDiskImageLineEdit.setText(settings["hda_disk_image"])
            self.uiHdbDiskImageLineEdit.setText(settings["hdb_disk_image"])
            self.uiHdcDiskImageLineEdit.setText(settings["hdc_disk_image"])
            self.uiHddDiskImageLineEdit.setText(settings["hdd_disk_image"])
            self.uiHdaDiskInterfaceComboBox.setCurrentIndex(self.uiHdaDiskInterfaceComboBox.findText(settings["hda_disk_interface"]))
            self.uiHdbDiskInterfaceComboBox.setCurrentIndex(self.uiHdbDiskInterfaceComboBox.findText(settings["hdb_disk_interface"]))
            self.uiHdcDiskInterfaceComboBox.setCurrentIndex(self.uiHdcDiskInterfaceComboBox.findText(settings["hdc_disk_interface"]))
            self.uiHddDiskInterfaceComboBox.setCurrentIndex(self.uiHddDiskInterfaceComboBox.findText(settings["hdd_disk_interface"]))
            self.uiCreateConfigDiskCheckBox.setChecked(settings["create_config_disk"])
            self.uiCdromImageLineEdit.setText(settings["cdrom_image"])
            self.uiBiosImageLineEdit.setText(settings["bios_image"])
            self.uiInitrdLineEdit.setText(settings["initrd"])
            self.uiKernelImageLineEdit.setText(settings["kernel_image"])
        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiHddTab.hide()
            self.uiCdromTab.hide()
            self.uiBiosImageGroupBox.hide()
            self.uiInitrdLabel.hide()
            self.uiInitrdLineEdit.hide()
            self.uiInitrdToolButton.hide()
            self.uiKernelImageLabel.hide()
            self.uiKernelImageLineEdit.hide()
            self.uiKernelImageToolButton.hide()

        if not node:
            # these are template settings

            self.uiNameLabel.setText("Template name:")

            # load the default name format
            self.uiDefaultNameFormatLineEdit.setText(settings["default_name_format"])

            # load the symbol
            self.uiSymbolLineEdit.setText(settings["symbol"])
            self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(settings["symbol"]))

            # load the category
            index = self.uiCategoryComboBox.findData(settings["category"])
            if index != -1:
                self.uiCategoryComboBox.setCurrentIndex(index)

            self.uiPortNameFormatLineEdit.setText(settings["port_name_format"])
            self.uiPortSegmentSizeSpinBox.setValue(settings["port_segment_size"])
            self.uiFirstPortNameLineEdit.setText(settings["first_port_name"])

            self.uiHdaDiskImageResizeToolButton.hide()
            self.uiHdbDiskImageResizeToolButton.hide()
            self.uiHdcDiskImageResizeToolButton.hide()
            self.uiHddDiskImageResizeToolButton.hide()
        else:
            self.uiDefaultNameFormatLabel.hide()
            self.uiDefaultNameFormatLineEdit.hide()
            self.uiSymbolLabel.hide()
            self.uiSymbolLineEdit.hide()
            self.uiSymbolToolButton.hide()
            self.uiCategoryComboBox.hide()
            self.uiCategoryLabel.hide()
            self.uiCategoryComboBox.hide()
            self.uiPortNameFormatLabel.hide()
            self.uiPortNameFormatLineEdit.hide()
            self.uiPortSegmentSizeLabel.hide()
            self.uiPortSegmentSizeSpinBox.hide()
            self.uiFirstPortNameLabel.hide()
            self.uiFirstPortNameLineEdit.hide()

        index = self.uiBootPriorityComboBox.findData(settings["boot_priority"])
        if index != -1:
            self.uiBootPriorityComboBox.setCurrentIndex(index)

        index = self.uiConsoleTypeComboBox.findText(settings["console_type"])
        if index != -1:
            self.uiConsoleTypeComboBox.setCurrentIndex(index)

        self.uiConsoleAutoStartCheckBox.setChecked(settings["console_auto_start"])
        self.uiKernelCommandLineEdit.setText(settings["kernel_command_line"])
        self.uiAdaptersSpinBox.setValue(settings["adapters"])
        self._custom_adapters = settings["custom_adapters"].copy()

        self.uiLegacyNetworkingCheckBox.setChecked(settings["legacy_networking"])
        self.uiReplicateNetworkConnectionStateCheckBox.setChecked(settings["replicate_network_connection_state"])

        # load the MAC address setting
        self.uiMacAddrLineEdit.setInputMask("HH:HH:HH:HH:HH:HH;_")
        if settings["mac_address"]:
            self.uiMacAddrLineEdit.setText(settings["mac_address"])
        else:
            self.uiMacAddrLineEdit.clear()

        # load the on close option
        index = self.uiOnCloseComboBox.findData(settings["on_close"])
        if index != -1:
            self.uiOnCloseComboBox.setCurrentIndex(index)

        index = self.uiAdapterTypesComboBox.findData(settings["adapter_type"])
        if index != -1:
            self.uiAdapterTypesComboBox.setCurrentIndex(index)

        self.uiCPUSpinBox.setValue(settings["cpus"])
        self.uiRamSpinBox.setValue(settings["ram"])

        if settings["cpu_throttling"]:
            self.uiActivateCPUThrottlingCheckBox.setChecked(True)
            self.uiCPUThrottlingSpinBox.setValue(settings["cpu_throttling"])
        else:
            self.uiActivateCPUThrottlingCheckBox.setChecked(False)

        index = self.uiProcessPriorityComboBox.findText(settings["process_priority"], QtCore.Qt.MatchFixedString)
        if index != -1:
            self.uiProcessPriorityComboBox.setCurrentIndex(index)
        self.uiQemuOptionsLineEdit.setText(settings["options"])
        self.uiUsageTextEdit.setPlainText(settings["usage"])

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the QEMU VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        # these settings cannot be shared by nodes and updated
        # in the node properties dialog.
        if not group:

            name = self.uiNameLineEdit.text()
            if not name:
                QtWidgets.QMessageBox.critical(self, "Name", "The QEMU VM name cannot be empty!")
            else:
                settings["name"] = name

            if "linked_clone" in settings:
                settings["linked_clone"] = self.uiBaseVMCheckBox.isChecked()

            settings["hda_disk_image"] = self.uiHdaDiskImageLineEdit.text().strip()
            settings["hdb_disk_image"] = self.uiHdbDiskImageLineEdit.text().strip()
            settings["hdc_disk_image"] = self.uiHdcDiskImageLineEdit.text().strip()
            settings["hdd_disk_image"] = self.uiHddDiskImageLineEdit.text().strip()
            settings["hda_disk_interface"] = self.uiHdaDiskInterfaceComboBox.currentText()
            settings["hdb_disk_interface"] = self.uiHdbDiskInterfaceComboBox.currentText()
            settings["hdc_disk_interface"] = self.uiHdcDiskInterfaceComboBox.currentText()
            settings["hdd_disk_interface"] = self.uiHddDiskInterfaceComboBox.currentText()
            settings["create_config_disk"] = self.uiCreateConfigDiskCheckBox.isChecked()
            settings["cdrom_image"] = self.uiCdromImageLineEdit.text().strip()
            settings["bios_image"] = self.uiBiosImageLineEdit.text().strip()
            settings["initrd"] = self.uiInitrdLineEdit.text().strip()
            settings["kernel_image"] = self.uiKernelImageLineEdit.text().strip()

            # check and save the MAC address
            mac = self.uiMacAddrLineEdit.text()
            if mac != ":::::":
                if not re.search(r"""^([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$""", mac):
                    QtWidgets.QMessageBox.critical(self, "MAC address", "Invalid MAC address (format required: hh:hh:hh:hh:hh:hh)")
                    if node:
                        raise ConfigurationError()
                else:
                    settings["mac_address"] = mac
            else:
                settings["mac_address"] = None

        if not node:
            # these are template settings

            # save the default name format
            default_name_format = self.uiDefaultNameFormatLineEdit.text().strip()
            if '{0}' not in default_name_format and '{id}' not in default_name_format:
                QtWidgets.QMessageBox.critical(self, "Default name format", "The default name format must contain at least {0} or {id}")
            else:
                settings["default_name_format"] = default_name_format

            symbol_path = self.uiSymbolLineEdit.text()
            settings["symbol"] = symbol_path
            settings["category"] = self.uiCategoryComboBox.itemData(self.uiCategoryComboBox.currentIndex())

            port_name_format = self.uiPortNameFormatLineEdit.text()
            port_segment_size = self.uiPortSegmentSizeSpinBox.value()
            first_port_name = self.uiFirstPortNameLineEdit.text().strip()

            try:
                StandardPortNameFactory(self.uiAdaptersSpinBox.value(), first_port_name, port_name_format, port_segment_size)
            except (IndexError, ValueError, KeyError):
                QtWidgets.QMessageBox.critical(self, "Invalid format", "Invalid port name format")
                raise ConfigurationError()

            settings["port_name_format"] = self.uiPortNameFormatLineEdit.text()
            settings["port_segment_size"] = port_segment_size
            settings["first_port_name"] = first_port_name

        if self.uiQemuListComboBox.currentIndex() != -1:
            qemu_path = self.uiQemuListComboBox.itemData(self.uiQemuListComboBox.currentIndex())
            settings["qemu_path"] = qemu_path
        else:
            QtWidgets.QMessageBox.critical(self, "Qemu binary", "Please select a Qemu binary")
            if node:
                raise ConfigurationError()

        settings["boot_priority"] = self.uiBootPriorityComboBox.itemData(self.uiBootPriorityComboBox.currentIndex())
        settings["console_type"] = self.uiConsoleTypeComboBox.currentText().lower()
        settings["console_auto_start"] = self.uiConsoleAutoStartCheckBox.isChecked()
        settings["adapter_type"] = self.uiAdapterTypesComboBox.itemData(self.uiAdapterTypesComboBox.currentIndex())
        settings["kernel_command_line"] = self.uiKernelCommandLineEdit.text()

        adapters = self.uiAdaptersSpinBox.value()
        if node and node.settings()["adapters"] != adapters:
            # check if the adapters settings have changed
            node_ports = node.ports()
            for node_port in node_ports:
                if not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                    raise ConfigurationError()

        settings["adapters"] = adapters
        settings["legacy_networking"] = self.uiLegacyNetworkingCheckBox.isChecked()
        settings["replicate_network_connection_state"] = self.uiReplicateNetworkConnectionStateCheckBox.isChecked()
        settings["custom_adapters"] = self._custom_adapters.copy()
        settings["on_close"] = self.uiOnCloseComboBox.itemData(self.uiOnCloseComboBox.currentIndex())
        settings["cpus"] = self.uiCPUSpinBox.value()
        settings["ram"] = self.uiRamSpinBox.value()
        if self.uiActivateCPUThrottlingCheckBox.isChecked():
            settings["cpu_throttling"] = self.uiCPUThrottlingSpinBox.value()
        else:
            settings["cpu_throttling"] = 0
        settings["process_priority"] = self.uiProcessPriorityComboBox.currentText().lower()
        settings["options"] = self.uiQemuOptionsLineEdit.text()
        settings["usage"] = self.uiUsageTextEdit.toPlainText()
        return settings
