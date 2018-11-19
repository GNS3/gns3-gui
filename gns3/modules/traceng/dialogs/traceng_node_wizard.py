# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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
Wizard for TraceNG nodes.
"""

import sys
import ipaddress

from gns3.qt import QtGui, QtWidgets
from gns3.node import Node
from gns3.dialogs.vm_wizard import VMWizard

from ..ui.traceng_node_wizard_ui import Ui_TraceNGNodeWizard


class TraceNGNodeWizard(VMWizard, Ui_TraceNGNodeWizard):
    """
    Wizard to create a TraceNG node.

    :param parent: parent widget
    """

    def __init__(self, traceng_nodes, parent):

        super().__init__(traceng_nodes, parent)
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/icons/traceng.png"))
        self.uiNameWizardPage.registerField("name*", self.uiNameLineEdit)

        # TraceNG is only supported on a local server
        self.uiRemoteRadioButton.setEnabled(False)
        self.uiVMRadioButton.setEnabled(False)

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if super().validateCurrentPage() is False:
            return False

        if self.currentPage() == self.uiNameWizardPage:

            if not sys.platform.startswith("win"):
                QtWidgets.QMessageBox.critical(self, "TraceNG", "TraceNG can only run on Windows with a local server")
                return False

            ip_address = self.uiIPAddressLineEdit.text()
            if ip_address:
                try:
                    ipaddress.IPv4Address(ip_address)
                except ipaddress.AddressValueError:
                    QtWidgets.QMessageBox.critical(self, "IP address", "Invalid IP address format")
                    return False
        return True

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        settings = {"name": self.uiNameLineEdit.text(),
                    "ip_address": self.uiIPAddressLineEdit.text(),
                    "symbol": ":/symbols/traceng.svg",
                    "category": Node.end_devices,
                    "compute_id": self._compute_id}

        return settings
