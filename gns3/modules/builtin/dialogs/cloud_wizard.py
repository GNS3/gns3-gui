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
Wizard for cloud nodes.
"""

from gns3.qt import QtGui, QtWidgets
from gns3.dialogs.vm_wizard import VMWizard

from ..ui.cloud_wizard_ui import Ui_CloudNodeWizard


class CloudWizard(VMWizard, Ui_CloudNodeWizard):

    """
    Wizard to create a cloud node.

    :param parent: parent widget
    """

    def __init__(self, cloud_nodes, parent):

        super().__init__(cloud_nodes, parent)

        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/cloud.svg"))
        self.uiNameWizardPage.registerField("name*", self.uiNameLineEdit)

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        settings = {"name": self.uiNameLineEdit.text(),
                    "symbol": "cloud",
                    "compute_id": self._compute_id}

        return settings
