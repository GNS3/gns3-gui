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
Wizard for VPCS nodes.
"""


from gns3.qt import QtGui, QtWidgets
from gns3.node import Node
from gns3.dialogs.vm_wizard import VMWizard

from ..ui.vpcs_node_wizard_ui import Ui_VPCSNodeWizard


class VPCSNodeWizard(VMWizard, Ui_VPCSNodeWizard):
    """
    Wizard to create a VPCS node.

    :param parent: parent widget
    """

    def __init__(self, vpcs_nodes, parent):

        super().__init__(vpcs_nodes, parent)

        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/vpcs_guest.svg"))
        self.uiNameWizardPage.registerField("name*", self.uiNameLineEdit)

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        settings = {"name": self.uiNameLineEdit.text(),
                    "base_script_file": "vpcs_base_config.txt",
                    "symbol": "vpcs_guest",
                    "compute_id": self._compute_id}

        return settings
