# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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
Wizard for Ethernet switches.
"""

from gns3.qt import QtGui, QtWidgets
from gns3.node import Node
from gns3.dialogs.vm_wizard import VMWizard

from ..ui.ethernet_switch_wizard_ui import Ui_EthernetSwitchWizard
from .. import Builtin


class EthernetSwitchWizard(VMWizard, Ui_EthernetSwitchWizard):

    """
    Wizard to create an Ethernet switch template.

    :param parent: parent widget
    """

    def __init__(self, ethernet_switches, parent):

        super().__init__(ethernet_switches, parent)

        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/ethernet_switch.svg"))
        self.uiNameWizardPage.registerField("name*", self.uiNameLineEdit)

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        ports = []
        for port_number in range(0, self.uiPortsSpinBox.value()):
            ports.append({"port_number": int(port_number),
                          "name": "Ethernet{}".format(port_number),
                          "type": "access",
                          "vlan": 1,
                          "ethertype": ""})

        settings = {"name": self.uiNameLineEdit.text(),
                    "symbol": ":/symbols/ethernet_switch.svg",
                    "category": Node.switches,
                    "server": self._compute_id,
                    "ports_mapping": ports}

        return settings
