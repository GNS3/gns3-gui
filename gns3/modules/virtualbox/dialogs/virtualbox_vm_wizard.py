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
Wizard for VirtualBox VMs.
"""

from gns3.qt import QtGui

from ..ui.virtualbox_vm_wizard_ui import Ui_VirtualBoxVMWizard
from .. import VirtualBox


class VirtualBoxVMWizard(QtGui.QWizard, Ui_VirtualBoxVMWizard):
    """
    Wizard to create a VirtualBox VM.

    :param virtualbox_vms: existing VirtualBox VMs
    :param parent: parent widget
    """

    def __init__(self, virtualbox_vms, parent):

        QtGui.QWizard.__init__(self, parent)
        self.setupUi(self)
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/icons/virtualbox.png"))
        self.setWizardStyle(QtGui.QWizard.ModernStyle)

        vm_list = VirtualBox.instance().getVirtualBoxVMList()
        for server in vm_list:
            vms = vm_list[server]["vms"]
            for vm in vms:
                key = "{server}:{vm}".format(server=server, vm=vm)
                if key not in virtualbox_vms:
                    self.uiVMListComboBox.addItem(key)

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        if not self.uiVMListComboBox.count():
            return {}

        server, vmname = self.uiVMListComboBox.itemText(self.uiVMListComboBox.currentIndex()).split(":", 1)

        settings = {
            "vmname": vmname,
            "server": server,
        }

        return settings
