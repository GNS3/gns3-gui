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

import re

from ..qt import QtGui
from ..topology import Topology
from ..ui.idlepc_dialog_ui import Ui_IdlePCDialog


class IdlePCDialog(QtGui.QDialog, Ui_IdlePCDialog):

    """
    Idle-PC dialog.
    """

    def __init__(self, router, idlepcs, parent):

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.uiButtonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self._applySlot)
        self.uiButtonBox.button(QtGui.QDialogButtonBox.Help).clicked.connect(self._helpSlot)

        self._router = router
        self._idlepcs = idlepcs

        for value in self._idlepcs:
            match = re.search(r"^(0x[0-9a-f]+)\s+\[(\d+)\]$", value)
            if match:
                idlepc = match.group(1)
                count = int(match.group(2))
                if 50 <= count <= 60:
                    value += "*"
                self.uiComboBox.addItem(value, idlepc)

    def _helpSlot(self):
        """
        Shows the help for Idle-PC.
        """

        help_text = "Finding the right idlepc value is a trial and error process, consisting of applying " \
                    "different Idle-PC values and monitoring the CPU usage.\n\nBest Idle-PC values are usually " \
                    "obtained when IOS is in idle state, the following message being displayed " \
                    "on the console: {} con0 is now available ... Press RETURN to get started.".format(self._router.name())
        QtGui.QMessageBox.information(self, "Hints for Idle-PC", help_text)

    def _applySlot(self):
        """
        Applies an Idle-PC value.
        """

        if not self.uiComboBox.count():
            QtGui.QMessageBox.critical(self, "Idle-PC", "Sorry could not find a valid Idle-PC value, please check again with Cisco IOS in a different state")
            return

        idlepc = self.uiComboBox.itemData(self.uiComboBox.currentIndex())
        # apply Idle-PC to all routers with the same IOS image
        ios_image = self._router.settings()["image"]
        for node in Topology.instance().nodes():
            if hasattr(node, "idlepc") and node.settings()["image"] == ios_image:
                node.setIdlepc(idlepc)

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result:
            self._applySlot()
        QtGui.QDialog.done(self, result)
