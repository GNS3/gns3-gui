# -*- coding: utf-8 -*-
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

import psutil


from gns3.version import __version__
from gns3.qt import QtWidgets, QtCore
from gns3.ui.doctor_dialog_ui import Ui_DoctorDialog
from gns3.servers import Servers
from gns3.local_config import LocalConfig
from gns3 import version


import logging
log = logging.getLogger(__name__)


class DoctorDialog(QtWidgets.QDialog, Ui_DoctorDialog):
    """
    This dialog allow user to detect error in his GNS3 installation.

    If you want to add a test add a method starting by check. The
    check return a tuple result and a message in case of failure.
    """

    def __init__(self, parent):

        super().__init__(parent)
        self.setupUi(self)
        self.uiOkButton.clicked.connect(self._okButtonClickedSlot)
        for method in sorted(dir(self)):
            if method.startswith('check'):
                self.write(getattr(self, method).__doc__ + ": ")
                (res, msg) = getattr(self, method)()
                if res:
                    self.write('<span style="color: green"><strong>OK</strong></span>')
                else:
                    self.write('<span style="color: red"><strong>KO</strong> {}</span>'.format(msg))
                self.write("<br/>")

    def write(self, text):
        """
        Add text to the text windows
        """
        self.uiDoctorResultTextEdit.setHtml(self.uiDoctorResultTextEdit.toHtml() + text)

    def _okButtonClickedSlot(self):
        self.accept()

    def checkLocalServerEnabled(self):
        """Check if local server is enabled"""
        if Servers.instance().shouldLocalServerAutoStart() is False:
            return (False, "The local server is disabled. Go to Preferences / Server / Local Server and enable the local server.")
        return (True, None)

    def checkDevVersionOfGNS3(self):
        """Check if it's a stable version of GNS3"""
        if version.__version_info__[3] != 0:
            return (False, "You are using a non stable version of GNS3.")
        return (True, None)

    def checkExperimentalFeaturesEnabled(self):
        """Check if experimental features of GNS3 are not enabled"""
        if LocalConfig.instance().experimental():
            return (False, "Experimental features are enabled. Please turn it off by going to Preferences / General / Miscellaneous.")
        return (True, None)

    def checkAVGInstalled(self):
        """Check if AVG is not installed"""

        for proc in psutil.process_iter():
            try:
                psinfo = proc.as_dict(["exe"])
                if psinfo["exe"] and "AVG\\" in psinfo["exe"]:
                    return (False, "AVG has known troubles with GNS3 even when you disable it. You need to whitelist dynamips.exe in AVG preferences.")
            except psutil.NoSuchProcess:
                pass
        return (True, None)

    def checkFreeRam(self):
        """Check free RAM"""

        if int(psutil.virtual_memory().available / (1024 * 1024)) < 600:
            return (False, "You have less than 600MB of RAM, this could block appliance like CISCO 7200")
        return (True, None)



if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    DoctorDialog(main).show()
    exit_code = app.exec_()
