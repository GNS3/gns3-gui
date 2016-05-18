#!/usr/bin/env python
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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


import sys
import shutil
import json
import os
from datetime import datetime


try:
    from gns3.qt import QtGui, QtWidgets
except ImportError:
    raise SystemExit("Can't import Qt modules: Qt and/or PyQt is probably not installed correctly...")

import logging
log = logging.getLogger(__name__)


from gns3.version import __version__
from gns3.local_config import LocalConfig
from gns3.ui.iouvm_converter_wizard_ui import Ui_IOUVMConverterWizard


class IOUVMConverterWizard(QtWidgets.QWizard, Ui_IOUVMConverterWizard):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtWidgets.QWizard.NoDefaultButton)

        # set the window icon
        self.setWindowIcon(QtGui.QIcon(":/images/gns3.ico"))  # this info is necessary for QSettings

        config = self._loadConfig()
        self.uiPushButtonBrowse.clicked.connect(self._browseTopologiesSlot)
        self.uiLineEditTopologiesPath.setText(config['Servers']['local_server']['projects_path'])

    def _browseTopologiesSlot(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a directory')
        self.uiLineEditTopologiesPath.setText(path)

    def validateCurrentPage(self):
        """
        Validates the settings.
        """

        if self.currentPage() == self.uiWizardPageIOURCCheck:
            return self._checkIOURC()
        elif self.currentPage() == self.uiWizardUpdateConfiguration:
            return self._updateConfig()
        elif self.currentPage() == self.uiWizardPagePatchTopologies:
            return self._patchTopologies()
        return True

    def _checkIOURC(self):
        """
        Validate if the IOURC contain an entry for the IOUVM
        """
        config = self._loadConfig()
        iourc_path = config.get("IOU", {}).get("iourc_path", "")
        if len(iourc_path) == 0:
            QtWidgets.QMessageBox.critical(self, "Error", "The IOURC is not configured")
            return False
        try:
            with open(iourc_path) as f:
                if 'gns3vm' not in f.read():
                    QtWidgets.QMessageBox.critical(self, "Error", "The gns3vm doesn't exist in your iourc file".format(iourc_path))
        except OSError:
            QtWidgets.QMessageBox.critical(self, "Error", "IOURC file {} doesn't exist or not accessible".format(iourc_path))
        return True

    def _updateConfig(self):
        """
        Update the config file to use the GNS3 VM instead of IOU VM
        """
        config = self._loadConfig()
        if "devices" in config["IOU"]:
            for device in config["IOU"]["devices"]:
                device["path"] = os.path.basename(device["path"])
                device["server"] = "vm"
        config["Servers"]["remote_servers"] = []
        self._writeConfig(config)
        return True

    def _patchTopologies(self):
        """
        Patch topologies to use the GNS3 VM
        """

        path = self.uiLineEditTopologiesPath.text()
        try:
            for (dirpath, dirnames, filenames) in os.walk(path):
                for filename in filenames:
                    if filename.endswith(".gns3"):
                        self._patchTopology(os.path.join(dirpath, filename))
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Error", "Can't open {}: {}".format(path, str(e)))
            return False
        return True

    def _patchTopology(self, path):
        """
        Path a specific topology
        """
        try:
            shutil.copy(path, "{}.{}.backup".format(path, datetime.now().isoformat()))
            with open(path) as f:
                topo = json.load(f)
            if "topology" in topo and "servers" in topo["topology"]:
                for server in topo["topology"]["servers"]:
                    if server["local"] is False:
                        server["vm"] = True
                with open(path, 'w+') as f:
                    topo = json.dump(topo, f)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Error", "Can't open {}: {}".format(path, str(e)))

    def _loadConfig(self):
        with open(self._configurationFile()) as f:
            return json.load(f)

    def _writeConfig(self, config):
        shutil.copy(self._configurationFile(), "{}.{}.backup".format(self._configurationFile(), datetime.now().isoformat()))
        with open(self._configurationFile(), 'w+') as f:
            json.dump(config, f, indent=4)

    def _configurationFile(self):
        if sys.platform.startswith("win"):
            filename = "gns3_gui.ini"
        else:
            filename = "gns3_gui.conf"
        directory = LocalConfig.configDirectory()
        return os.path.join(directory, filename)


def main():
    app = QtWidgets.QApplication(sys.argv)

    app.setOrganizationName("GNS3")
    app.setOrganizationDomain("gns3.net")
    app.setApplicationName("GNS3")
    app.setApplicationVersion(__version__)

    # We force a full garbage collect before exit
    # for unknow reason otherwise Qt Segfault on OSX in some
    # conditions
    import gc
    gc.collect()

    # Manage Ctrl + C or kill command
    def sigint_handler(*args):
        log.info("Signal received exiting the application")
        app.closeAllWindows()
    # signal.signal(signal.SIGINT, sigint_handler)
    # signal.signal(signal.SIGTERM, sigint_handler)

    mainwindow = IOUVMConverterWizard()
    mainwindow.show()
    exit_code = mainwindow.exec_()

    # We force a full garbage collect before exit
    # for unknow reason otherwise Qt Segfault on OSX in some
    # conditions
    import gc
    gc.collect()

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
