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

import psutil
import platform
import os
import stat
import sys
import struct

from gns3.qt import QtWidgets
from gns3.ui.doctor_dialog_ui import Ui_DoctorDialog
from gns3.local_server import LocalServer
from gns3.local_config import LocalConfig
from gns3 import version
from gns3.modules.vmware import VMware

import logging
log = logging.getLogger(__name__)


class DoctorDialog(QtWidgets.QDialog, Ui_DoctorDialog):
    """
    This dialog allow user to detect error in his GNS3 installation.

    If you want to add a test add a method starting by check. The
    check return a tuple result and a message in case of failure.
    """

    def __init__(self, parent, console=False):

        super().__init__(parent)
        self._console = console
        self.setupUi(self)
        self.uiOkButton.clicked.connect(self._okButtonClickedSlot)
        for method in sorted(dir(self)):
            if method.startswith('check'):
                try:
                    self.write(getattr(self, method).__doc__ + "...")
                    (res, msg) = getattr(self, method)()
                    if res == 0:
                        self.write('<span style="color: green"><strong>OK</strong></span>')
                    elif res == 1:
                        self.write('<span style="color: orange"><strong>WARNING</strong> {}</span>'.format(msg))
                    elif res == 2:
                        self.write('<span style="color: red"><strong>ERROR</strong> {}</span>'.format(msg))
                except Exception as e:
                    log.error("GNS3 doctor exception detected: {}".format(e), exc_info=1)
                    self.write('<span style="color: red"><strong>FAIL</strong> The doctor failed during this test with error: {} Please check on the forum.</span>'.format(str(e)))
                self.write("<br/>")

    def write(self, text):
        """
        Add text to the text windows
        """
        if self._console:
            print(text)
        self.uiDoctorResultTextEdit.setHtml(self.uiDoctorResultTextEdit.toHtml() + text)

    def _okButtonClickedSlot(self):
        self.accept()

    def checkLocalServerEnabled(self):
        """Checking if the local server is enabled"""
        if LocalServer.instance().shouldLocalServerAutoStart() is False:
            return (2, "The local server is disabled. Go to Preferences -> Server -> Local Server and enable the local server.")
        return (0, None)

    def checkDevVersionOfGNS3(self):
        """Checking for stable GNS3 version"""
        if version.__version_info__[3] != 0:
            return (1, "You are using a unstable version of GNS3.")
        return (0, None)

    def checkExperimentalFeaturesEnabled(self):
        """Checking if experimental features are not enabled"""
        if LocalConfig.instance().experimental():
            return (1, "Experimental features are enabled. Turn them off by going to Preferences -> General -> Miscellaneous.")
        return (0, None)

    def checkAVGInstalled(self):
        """Checking if AVG software is not installed"""

        for proc in psutil.process_iter():
            try:
                psinfo = proc.as_dict(["exe"])
                if psinfo["exe"] and "AVG\\" in psinfo["exe"]:
                    return (2, "AVG has known issues with GNS3, even after you disable it. You must whitelist dynamips.exe in the AVG preferences.")
            except psutil.NoSuchProcess:
                pass
        return (0, None)

    def checkFreeRam(self):
        """Checking for amount of free virtual memory"""

        if int(psutil.virtual_memory().available / (1024 * 1024)) < 600:
            return (2, "You have less than 600MB of available virtual memory, this could prevent nodes to start")
        return (0, None)

    def checkVmrun(self):
        """Checking if vmrun is installed"""
        vmrun = VMware.instance().findVmrun()
        if len(vmrun) == 0:
            return (1, "The vmrun executable could not be found, VMware VMs cannot be used")
        return (0, None)

    def check64Bit(self):
        """Check if processor is 64 bit"""
        if platform.architecture()[0] != "64bit":
            return (2, "The architecture {} is not supported.".format(platform.architecture()[0]))
        return (0, None)

    def checkUbridgePermission(self):
        """Check if ubridge has the correct permission"""
        if not sys.platform.startswith("win") and os.geteuid() == 0:
            # we are root, so we should have privileged access.
            return (0, None)

        path = LocalServer.instance().localServerSettings().get("ubridge_path")
        if path is None:
            return (0, None)
        if not os.path.exists(path):
            return (2, "Ubridge path {path} doesn't exists".format(path=path))

        request_setuid = False
        if sys.platform.startswith("linux"):
            try:
                if "security.capability" in os.listxattr(path):
                    caps = os.getxattr(path, "security.capability")
                    # test the 2nd byte and check if the 13th bit (CAP_NET_RAW) is set
                    if not struct.unpack("<IIIII", caps)[1] & 1 << 13:
                        return (2, "Ubridge requires CAP_NET_RAW. Run sudo setcap cap_net_admin,cap_net_raw=ep {path}".format(path=path))
                else:
                    # capabilities not supported
                    request_setuid = True
            except AttributeError:
                # Due to a Python bug, os.listxattr could be missing: https://github.com/GNS3/gns3-gui/issues/2010
                return (1, "Could not determine if CAP_NET_RAW capability is set for uBridge (Python bug)".format(path=path))

        if sys.platform.startswith("darwin") or request_setuid:
            if os.stat(path).st_uid != 0 or not os.stat(path).st_mode & stat.S_ISUID:
                return (2, "Ubridge should be setuid. Run sudo chown root:admin {path} and sudo chmod 4750 {path}".format(path=path))
        return (0, None)

    def checkDynamipsPermission(self):
        """Check if dynamips has the correct permission"""
        if not sys.platform.startswith("win") and os.geteuid() == 0:
            # we are root, so we should have privileged access.
            return (0, None)

        path = LocalServer.instance().localServerSettings().get("dynamips_path")
        if path is None:
            return (0, None)
        if not os.path.exists(path):
            return (2, "Dynamips path {path} doesn't exists".format(path=path))

        try:
            if sys.platform.startswith("linux") and "security.capability" in os.listxattr(path):
                caps = os.getxattr(path, "security.capability")
                # test the 2nd byte and check if the 13th bit (CAP_NET_RAW) is set
                if not struct.unpack("<IIIII", caps)[1] & 1 << 13:
                    return (2, "Dynamips requires CAP_NET_RAW. Run sudo setcap cap_net_raw,cap_net_admin+eip {path}".format(path=path))
        except AttributeError:
            # Due to a Python bug, os.listxattr could be missing: https://github.com/GNS3/gns3-gui/issues/2010
            return (1, "Could not determine if CAP_NET_RAW capability is set for Dynamips (Python bug)".format(path=path))
        return (0, None)

    def checkGNS3InstalledTwice(self):
        """Check if gns3 is not installed twice"""

        if not sys.platform.startswith("win"):
            return (0, None)

        try:
            if os.path.exists("/usr/local/bin/gns3server") and os.path.exists("/usr/bin/gns3server"):
                return (2, "GNS3 is installed twice please remove it from /usr/local/bin")
        except OSError:
            pass
        return (0, None)

    def _checkWindowsService(self, service_name):

        import pywintypes
        import win32service
        import win32serviceutil

        try:
            if win32serviceutil.QueryServiceStatus(service_name, None)[1] != win32service.SERVICE_RUNNING:
                return False
        except pywintypes.error as e:
            if e.winerror == 1060:
                return False
            else:
                raise
        return True

    def checkRPFServiceIsRunning(self):
        """Check if the RPF service is running (required to use Ethernet NIOs)"""

        if not sys.platform.startswith("win"):
            return (0, None)

        import pywintypes
        try:
            if not self._checkWindowsService("npf") and not self._checkWindowsService("npcap"):
                return (2, "The NPF or NPCAP service is not installed, please install Winpcap or Npcap and reboot")
        except pywintypes.error as e:
            return (2, "Could not check if the NPF or Npcap service is running: {}".format(e.strerror))

        return (0, None)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    dialog = DoctorDialog(main, console=True)
    # dialog.show()
    #exit_code = app.exec_()
