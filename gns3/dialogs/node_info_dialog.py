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
Dialog to show node information.
"""

from ..qt import QtWidgets
from ..ui.node_info_dialog_ui import Ui_NodeInfoDialog


class NodeInfoDialog(QtWidgets.QDialog, Ui_NodeInfoDialog):

    """
    Node information dialog.

    :param parent: parent widget
    """

    def __init__(self, node, parent):

        super().__init__(parent)
        self.setupUi(self)
        general_info = node.info()
        usage_info = node.usage()
        command_line_info = node.commandLine()
        self.setWindowTitle(node.name())

        # General tab
        self.uiGeneralTextBrowser.setPlainText(general_info)

        # Usage tab
        if not usage_info:
            usage_info = "No usage information has been provided for this node."
        self.uiUsageTextBrowser.setPlainText(usage_info)

        # Command line tab
        if command_line_info is None:
            command_line_info = "Command line information is not supported for this type of node."
        elif len(command_line_info) == 0:
            command_line_info = "Please start the node in order to get the command line information."
        self.uiCommandLineTextBrowser.setPlainText(command_line_info)
