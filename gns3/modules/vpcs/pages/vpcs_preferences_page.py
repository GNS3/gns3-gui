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
Configuration page for VPCS preferences.
"""

import os
import sys
from gns3.qt import QtCore, QtGui
from gns3.servers import Servers
from .. import VPCS
from ..ui.vpcs_preferences_page_ui import Ui_VPCSPreferencesPageWidget
from ..settings import VPCS_SETTINGS


class VPCSPreferencesPage(QtGui.QWidget, Ui_VPCSPreferencesPageWidget):
    """
    QWidget preference page for VPCS.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        # connect signals
        self.uiVPCSPathToolButton.clicked.connect(self._vpcsrcPathBrowserSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiUseLocalServercheckBox.stateChanged.connect(self._useLocalServerSlot)
        self.uiTestSettingsPushButton.clicked.connect(self._testSettingsSlot)

    def _testSettingsSlot(self):

        QtGui.QMessageBox.critical(self, "Test settings", "Sorry, not yet implemented!")
        return

        servers = Servers.instance()
        if self.uiUseLocalServercheckBox.isChecked():
            server = servers.localServer()
        else:
            QtGui.QMessageBox.critical(self, "Test settings", "Sorry, not yet implemented!")

        try:
            if not server.connected():
                server.reconnect()
        except OSError as e:
            QtGui.QMessageBox.critical(self, "Local server", "Could not connect to the local server {host} on port {port}: {error}".format(host=server.host,
                                                                                                                                           port=server.port,
                                                                                                                                           error=e))

        self._progress_dialog = QtGui.QProgressDialog("Testing settings...", "Cancel", 0, 0, parent=self)
        self._progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        self._progress_dialog.setWindowTitle("Settings")
        self._progress_dialog.show()

        vpcs_module = VPCS.instance()
        if server not in vpcs_module.servers():
            server_added = True
            vpcs_module.addServer(server)
        self.savePreferences()
        if server_added:
            vpcs_module.removeServer(server)
        server.send_message("vpcs.test_settings", None, self._testSettingsCallback)

    def _testSettingsCallback(self, result, error=False):

        if self._progress_dialog.wasCanceled():
            print("Was canceled")
            return

        self._progress_dialog.accept()

        if error:
            pass
            #log.error("error while allocating an UDP port for {}: {}".format(self.name(), result["message"]))

        print("Report received")
        print(result)

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(VPCS_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not the QTreeWidget for remote servers.
        """

        if state:
            self.uiRemoteServersTreeWidget.setEnabled(False)
        else:
            self.uiRemoteServersTreeWidget.setEnabled(True)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: VPCS settings
        """

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

        self.uiRemoteServersTreeWidget.resizeColumnToContents(0)

    def loadPreferences(self):
        """
        Loads VPCS preferences.
        """

        vpcs_settings = VPCS.instance().settings()
        self._populateWidgets(vpcs_settings)

        servers = Servers.instance()
        servers.updated_signal.connect(self._updateRemoteServersSlot)
        self._updateRemoteServersSlot()

    def savePreferences(self):
        """
        Saves VPCS preferences.
        """

        new_settings = {}
        new_settings["use_local_server"] = self.uiUseLocalServercheckBox.isChecked()
        new_settings["console_start_port_range"] = self.uiConsoleStartPortSpinBox.value()
        new_settings["console_end_port_range"] = self.uiConsoleEndPortSpinBox.value()
        new_settings["udp_start_port_range"] = self.uiUDPStartPortSpinBox.value()
        new_settings["udp_end_port_range"] = self.uiUDPEndPortSpinBox.value()
        VPCS.instance().setSettings(new_settings)
