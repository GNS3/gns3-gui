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
Configuration page for IOU preferences.
"""

import sys
from gns3.qt import QtGui
from gns3.servers import Servers
from .. import IOU
from ..ui.iou_preferences_page_ui import Ui_IOUPreferencesPageWidget
from ..settings import IOU_SETTINGS


class IOUPreferencesPage(QtGui.QWidget, Ui_IOUPreferencesPageWidget):
    """
    QWidget preference page for IOU.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        # connect signals
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiUseLocalServercheckBox.stateChanged.connect(self._useLocalServerSlot)

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(IOU_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not the QTreeWidget for remote servers.
        """

        if state:
            # IOU is only available on Linux
            if not sys.platform.startswith("linux"):
                QtGui.QMessageBox.critical(self, "IOU", "Sorry, local server is only supported on Linux")
                return
            self.uiRemoteServersTreeWidget.setEnabled(False)
        else:
            self.uiRemoteServersTreeWidget.setEnabled(True)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: IOU settings
        """

        self.uiIOURCPathLineEdit.setText(settings["iourc"])
        self.uiUseLocalServercheckBox.setChecked(settings["use_local_server"])
        self.uiConsoleStartPortSpinBox.setValue(settings["console_start_port_range"])
        self.uiConsoleEndPortSpinBox.setValue(settings["console_end_port_range"])
        self.uiUDPStartPortSpinBox.setValue(settings["udp_start_port_range"])
        self.uiUDPEndPortSpinBox.setValue(settings["udp_end_port_range"])

    def _updateRemoteServersSlot(self):
        """
        Adds/Updates the available remote servers.
        """

        servers = Servers.instance()
        self.uiRemoteServersTreeWidget.clear()
        for server in servers.remoteServers().values():
            host = server.host
            port = server.port
            item = QtGui.QTreeWidgetItem(self.uiRemoteServersTreeWidget)
            item.setText(0, host)
            item.setText(1, str(port))

    def loadPreferences(self):
        """
        Loads IOU preferences.
        """

        iou_settings = IOU.instance().settings()
        self._populateWidgets(iou_settings)

        servers = Servers.instance()
        servers.updated_signal.connect(self._updateRemoteServersSlot)
        self._updateRemoteServersSlot()

    def savePreferences(self):
        """
        Saves IOU preferences.
        """

        new_settings = {}
        new_settings["iourc"] = self.uiIOURCPathLineEdit.text()
        new_settings["use_local_server"] = self.uiUseLocalServercheckBox.isChecked()
        new_settings["console_start_port_range"] = self.uiConsoleStartPortSpinBox.value()
        new_settings["console_end_port_range"] = self.uiConsoleEndPortSpinBox.value()
        new_settings["udp_start_port_range"] = self.uiUDPStartPortSpinBox.value()
        new_settings["udp_end_port_range"] = self.uiUDPEndPortSpinBox.value()
        IOU.instance().setSettings(new_settings)
