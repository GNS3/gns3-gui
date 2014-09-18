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

from functools import partial
from gns3.qt import QtGui
from gns3.dialogs.node_configurator_dialog import ConfigurationError
from gns3.modules.module_error import ModuleError

from ..ui.qemu_vm_configuration_page_ui import Ui_QemuVMConfigPageWidget
from .. import Qemu


class QemuVMConfigurationPage(QtGui.QWidget, Ui_QemuVMConfigPageWidget):
    """
    QWidget configuration page for QEMU VMs.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.uiAdapterTypesComboBox.clear()
        self.uiAdapterTypesComboBox.addItems(["ne2k_pci",
                                              "i82551",
                                              "i82557b",
                                              "i82559er",
                                              "rtl8139",
                                              "e1000",
                                              "pcnet",
                                              "virtio"])

    def _QemuListCallback(self, result, error=False, server="", qemu_path=""):
        """
        Callback to get the QEMU binaries list.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtGui.QMessageBox.critical(self, "QEMU list", "Could not get the QEMU binaries list: {}".format(result["message"]))
        else:
            for qemu in result["qemus"]:
                if Qemu.instance().settings()["use_local_server"]:
                    server = "local"
                else:
                    server = result["server"]
                key = "{server}:{qemu}".format(server=server, qemu=qemu["path"])
                self.uiQemuListComboBox.addItem("{key} (v{version})".format(key=key, version=qemu["version"]), key)

            index = self.uiQemuListComboBox.findData("{server}:{qemu_path}".format(server=server, qemu_path=qemu_path))
            if index != -1:
                self.uiQemuListComboBox.setCurrentIndex(index)
            else:
                self.uiQemuListComboBox.clear()

    def loadSettings(self, settings, node, group=False):
        """
        Loads the QEMU VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        if node.server().isLocal():
            host = "local"
        else:
            host = node.server().host
        callback = partial(self._QemuListCallback, server=host, qemu_path=settings["qemu_path"])
        try:
            Qemu.instance().get_qemu_list(node.server(), callback)
        except ModuleError as e:
            QtGui.QMessageBox.critical(self, "QEMU list", "{}".format(e))

        if not group:
            # set the device name
            self.uiNameLineEdit.setText(settings["name"])
            self.uiConsolePortSpinBox.setValue(settings["console"])
            self.uiDiskImageLineEdit.setText(settings["disk_image"])
        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiConsolePortLabel.hide()
            self.uiConsolePortSpinBox.hide()
            self.uiDiskImageLabel.hide()
            self.uiDiskImageLineEdit.hide()

        self.uiAdaptersSpinBox.setValue(settings["adapters"])
        index = self.uiAdapterTypesComboBox.findText(settings["adapter_type"])
        if index != -1:
            self.uiAdapterTypesComboBox.setCurrentIndex(index)

        self.uiRamSpinBox.setValue(settings["ram"])
        self.uiQemuOptionsLineEdit.setText(settings["options"])

    def saveSettings(self, settings, node, group=False):
        """
        Saves the QEMU VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        # these settings cannot be shared by nodes and updated
        # in the node configurator.
        if not group:

            name = self.uiNameLineEdit.text()
            if not name:
                QtGui.QMessageBox.critical(self, "Name", "The QEMU VM name cannot be empty!")
            else:
                settings["name"] = name

            settings["console"] = self.uiConsolePortSpinBox.value()
            settings["disk_image"] = self.uiDiskImageLineEdit.text()

        else:
            del settings["name"]
            del settings["console"]
            del settings["disk_image"]

        server, qemu_path = self.uiQemuListComboBox.itemData(self.uiQemuListComboBox.currentIndex()).split(":", 1)
        settings["qemu_path"] = qemu_path
        settings["adapter_type"] = self.uiAdapterTypesComboBox.currentText()

        adapters = self.uiAdaptersSpinBox.value()
        if settings["adapters"] != adapters:
            # check if the adapters settings have changed
            node_ports = node.ports()
            for node_port in node_ports:
                if not node_port.isFree():
                    QtGui.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                    raise ConfigurationError()
        settings["adapters"] = adapters

        settings["ram"] = self.uiRamSpinBox.value()
        settings["options"] = self.uiQemuOptionsLineEdit.text()
