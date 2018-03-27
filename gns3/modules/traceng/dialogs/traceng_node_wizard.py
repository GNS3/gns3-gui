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


from gns3.qt import QtGui, QtWidgets
from gns3.node import Node
from gns3.dialogs.vm_wizard import VMWizard

from ..ui.traceng_node_wizard_ui import Ui_TraceNGNodeWizard


class TraceNGNodeWizard(VMWizard, Ui_TraceNGNodeWizard):

    """
    Wizard to create a TraceNG node template.

    :param parent: parent widget
    """

    def __init__(self, traceng_nodes, parent):

        super().__init__(traceng_nodes, parent)
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/icons/traceng.png"))
        self.uiNameWizardPage.registerField("name*", self.uiNameLineEdit)

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        settings = {"name": self.uiNameLineEdit.text(),
                    "ip_address": self.uiIPAddressLineEdit.text(),
                    "symbol": ":/symbols/traceng.svg",
                    "category": Node.end_devices,
                    "server": self._compute_id}

        return settings
