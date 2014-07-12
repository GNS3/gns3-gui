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
        self.uiVirtualBoxVMsTreeWidget.itemClicked.connect(self._vboxVMClickedSlot)
        self.uiVirtualBoxVMsTreeWidget.itemSelectionChanged.connect(self._vboxVMChangedSlot)

    def _vboxVMClickedSlot(self, item, column):
        """
        Loads a selected VirtualBox VM from the tree widget.

        :param item: selected QTreeWidgetItem instance
        :param column: ignored
        """

        name = item.text(0)
        server = item.text(1)
        key = "{server}:{name}".format(server=server, name=name)
        vbox_vm = self._virtualbox_vms[key]

        self.uiNameLineEdit.setText(vbox_vm["name"])
        self.uiAdaptersSpinBox.setValue(vbox_vm["adapters"])
        self.uiEnableConsoleSupportCheckBox.setChecked(vbox_vm["console_support"])
        self.uiEnableConsoleServerCheckBox.setChecked(vbox_vm["console_server"])
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

        name = self.uiNameLineEdit.text()
        adapters = self.uiAdaptersSpinBox.value()
        console_support = self.uiEnableConsoleSupportCheckBox.isChecked()
        console_server = self.uiEnableConsoleServerCheckBox.isChecked()
        headless = self.uiHeadlessModeCheckBox.isChecked()

        #TODO: mutiple remote server
        if VirtualBox.instance().settings()["use_local_server"]:
            server = "local"
        else:
            server = next(iter(Servers.instance()))
            if not server:
                QtGui.QMessageBox.critical(self, "VirtualBox VM", "No remote server available!")
                return
            server = server.host

        key = "{server}:{name}".format(server=server, name=name)
        item = self.uiVirtualBoxVMsTreeWidget.currentItem()

        if key in self._virtualbox_vms and item and item.text(0) == name:
            item.setText(0, name)
            item.setText(1, server)
        elif key in self._virtualbox_vms:
            return
        else:
            # add a new entry in the tree widget
            item = QtGui.QTreeWidgetItem(self.uiVirtualBoxVMsTreeWidget)
            item.setText(0, name)
            item.setText(1, server)
            self.uiVirtualBoxVMsTreeWidget.setCurrentItem(item)

        self._virtualbox_vms[key] = {"name": name,
                                     "adapters": adapters,
                                     "console_support": console_support,
                                     "console_server": console_server,
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
            name = item.text(0)
            server = item.text(1)
            key = "{server}:{name}".format(server=server, name=name)
            del self._virtualbox_vms[key]
            self.uiVirtualBoxVMsTreeWidget.takeTopLevelItem(self.uiVirtualBoxVMsTreeWidget.indexOfTopLevelItem(item))

    def loadPreferences(self):
        """
        Loads the VirtualBox VM preferences.
        """

        self._virtualbox_vms.clear()
        self.uiVirtualBoxVMsTreeWidget.clear()

        vbox_vms = VirtualBox.instance().virtualBoxVMs()
        for vbox_vm in vbox_vms.values():
            item = QtGui.QTreeWidgetItem(self.uiVirtualBoxVMsTreeWidget)
            item.setText(0, vbox_vm["name"])
            item.setText(1, vbox_vm["server"])

        self.uiVirtualBoxVMsTreeWidget.resizeColumnToContents(0)
        self.uiVirtualBoxVMsTreeWidget.resizeColumnToContents(1)
        self._virtualbox_vms.update(vbox_vms)

    def savePreferences(self):
        """
        Saves the VirtualBox VM preferences.
        """

        VirtualBox.instance().setVirtualBoxVMs(self._virtualbox_vms)
