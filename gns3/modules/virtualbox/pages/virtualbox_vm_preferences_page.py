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
Configuration page for VirtualBox VM preferences.
"""

from gns3.qt import QtGui
from gns3.servers import Servers
from gns3.main_window import MainWindow
from gns3.modules.module_error import ModuleError
from .. import VirtualBox
from ..ui.virtualbox_vm_preferences_page_ui import Ui_VirtualBoxVMPreferencesPageWidget


class VirtualBoxVMPreferencesPage(QtGui.QWidget, Ui_VirtualBoxVMPreferencesPageWidget):
    """
    QWidget preference page for VirtualBox VM preferences.
    """

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._virtualbox_vms = {}
        self.uiSaveVirtualBoxVMPushButton.clicked.connect(self._vboxVMSaveSlot)
        self.uiDeleteVirtualBoxVMPushButton.clicked.connect(self._vboxVMDeleteSlot)
        self.uiRefreshPushButton.clicked.connect(self._vboxRefreshSlot)
        self.uiVirtualBoxVMsTreeWidget.itemClicked.connect(self._vboxVMClickedSlot)
        self.uiVirtualBoxVMsTreeWidget.itemSelectionChanged.connect(self._vboxVMChangedSlot)

        self.uiAdapterTypesComboBox.clear()
        self.uiAdapterTypesComboBox.addItems(["Automatic",
                                              "PCnet-PCI II (Am79C970A)",
                                              "PCNet-FAST III (Am79C973)",
                                              "Intel PRO/1000 MT Desktop (82540EM)",
                                              "Intel PRO/1000 T Server (82543GC)",
                                              "Intel PRO/1000 MT Server (82545EM)",
                                              "Paravirtualized Network (virtio-net)"])

        self._vboxRefreshSlot()

    def _vboxVMClickedSlot(self, item, column):
        """
        Loads a selected VirtualBox VM from the tree widget.

        :param item: selected QTreeWidgetItem instance
        :param column: ignored
        """

        vmname = item.text(0)
        server = item.text(1)
        key = "{server}:{vmname}".format(server=server, vmname=vmname)
        vbox_vm = self._virtualbox_vms[key]

        index = self.uiVMListComboBox.findText("{server}:{vmname}".format(server=vbox_vm["server"], vmname=vbox_vm["vmname"]))
        if index != -1:
            self.uiVMListComboBox.setCurrentIndex(index)
        self.uiAdaptersSpinBox.setValue(vbox_vm["adapters"])
        index = self.uiAdapterTypesComboBox.findText(vbox_vm["adapter_type"])
        if index != -1:
            self.uiAdapterTypesComboBox.setCurrentIndex(index)
        self.uiHeadlessModeCheckBox.setChecked(vbox_vm["headless"])

    def _vboxVMChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiVirtualBoxVMsTreeWidget.currentItem()
        if item:
            self.uiDeleteVirtualBoxVMPushButton.setEnabled(True)
        else:
            self.uiDeleteVirtualBoxVMPushButton.setEnabled(False)

    def _vboxVMSaveSlot(self):
        """
        Adds/Saves an VirtualBox VM.
        """

        vm = self.uiVMListComboBox.currentText()
        if not vm:
            QtGui.QMessageBox.critical(self, "VirtualBox VM", "Please select a VirtualBox VM")
            return

        server, vmname = vm.split(":", 1)
        adapters = self.uiAdaptersSpinBox.value()
        adapter_type = self.uiAdapterTypesComboBox.currentText()
        headless = self.uiHeadlessModeCheckBox.isChecked()

        # #TODO: mutiple remote server
        # if VirtualBox.instance().settings()["use_local_server"]:
        #     server = "local"
        # else:
        #     server = next(iter(Servers.instance()))
        #     if not server:
        #         QtGui.QMessageBox.critical(self, "VirtualBox VM", "No remote server available!")
        #         return
        #     server = server.host

        key = "{server}:{vmname}".format(server=server, vmname=vmname)
        item = self.uiVirtualBoxVMsTreeWidget.currentItem()

        if key in self._virtualbox_vms and item and item.text(0) == vmname:
            item.setText(0, vmname)
            item.setText(1, server)
        elif key in self._virtualbox_vms:
            return
        else:
            # add a new entry in the tree widget
            item = QtGui.QTreeWidgetItem(self.uiVirtualBoxVMsTreeWidget)
            item.setText(0, vmname)
            item.setText(1, server)
            self.uiVirtualBoxVMsTreeWidget.setCurrentItem(item)

        self._virtualbox_vms[key] = {"vmname": vmname,
                                     "adapters": adapters,
                                     "adapter_type": adapter_type,
                                     "headless": headless,
                                     "server": server}

        self.uiVirtualBoxVMsTreeWidget.resizeColumnToContents(0)
        self.uiVirtualBoxVMsTreeWidget.resizeColumnToContents(1)

    def _vboxVMDeleteSlot(self):
        """
        Deletes a VirtualBox VM.
        """

        item = self.uiVirtualBoxVMsTreeWidget.currentItem()
        if item:
            vmname = item.text(0)
            server = item.text(1)
            key = "{server}:{vmname}".format(server=server, vmname=vmname)
            del self._virtualbox_vms[key]
            self.uiVirtualBoxVMsTreeWidget.takeTopLevelItem(self.uiVirtualBoxVMsTreeWidget.indexOfTopLevelItem(item))

    def _vboxRefreshSlot(self):
        """
        Gets/refreshes the VM list for all servers.
        """

        self.uiVMListComboBox.clear()
        vbox_module = VirtualBox.instance()
        servers = Servers.instance()

        if vbox_module.settings()["use_local_server"]:
            try:
                vbox_module.get_vm_list(servers.localServer(), self._VMListCallback)
            except ModuleError as e:
                QtGui.QMessageBox.critical(self, "VM list", "{}".format(e))
        else:
            for server in servers.remoteServers().values():
                try:
                    vbox_module.get_vm_list(server, self._VMListCallback)
                except ModuleError as e:
                    print("{}".format(e))
                    continue

    def _VMListCallback(self, result, error=False):
        """
        Callback to get the VM list.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtGui.QMessageBox.critical(self, "VM list", "Could not get the VM list from the server: {}".format(result["message"]))
        else:
            for vmname in result["vms"]:
                if VirtualBox.instance().settings()["use_local_server"]:
                    server = "local"
                else:
                    server = result["server"]
                self.uiVMListComboBox.addItem("{server}:{vmname}".format(server=server, vmname=vmname))

    def loadPreferences(self):
        """
        Loads the VirtualBox VM preferences.
        """

        self._virtualbox_vms.clear()
        self.uiVirtualBoxVMsTreeWidget.clear()

        vbox_module = VirtualBox.instance()
        vbox_vms = vbox_module.virtualBoxVMs()
        for vbox_vm in vbox_vms.values():
            item = QtGui.QTreeWidgetItem(self.uiVirtualBoxVMsTreeWidget)
            item.setText(0, vbox_vm["vmname"])
            item.setText(1, vbox_vm["server"])

        self.uiVirtualBoxVMsTreeWidget.resizeColumnToContents(0)
        self.uiVirtualBoxVMsTreeWidget.resizeColumnToContents(1)
        self._virtualbox_vms.update(vbox_vms)

    def savePreferences(self):
        """
        Saves the VirtualBox VM preferences.
        """

        VirtualBox.instance().setVirtualBoxVMs(self._virtualbox_vms)
