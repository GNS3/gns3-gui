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
import subprocess

from ..qt import QtWidgets
from .progress_dialog import ProgressDialog
from .wait_for_command_worker import WaitForCommandWorker
from .wait_for_runas_worker import WaitForRunAsWorker

import logging
log = logging.getLogger(__name__)


def sudo(command, parent=None, shell=False):
    """
    Run a command  as an administrator.
    """

    if parent is None:
        from ..main_window import MainWindow
        parent = MainWindow.instance()

    while True:
        if not sys.platform.startswith("win32"):
            password, ok = QtWidgets.QInputDialog.getText(parent,
                                                          "Run as administrator",
                                                          "Please enter your password to proceed.\nCommand: {}".format(' '.join(command)),
                                                          QtWidgets.QLineEdit.Password, "")
            if not ok:
                return False

            try:
                # check the password is valid
                subprocess.check_output(["sudo", "-S", "id"], input=(password + "\n").encode(), timeout=30)
            except subprocess.CalledProcessError:
                continue
            except (OSError, subprocess.SubprocessError) as e:
                QtWidgets.QMessageBox.critical(parent, "Run as administrator", "Could not execute sudo: {}".format(e))
                return False

            # sudo shouldn't need the password again.
            waited_command = ["sudo"]
            waited_command.extend(command)
            worker = WaitForCommandWorker(waited_command, shell=shell)

            for line in worker.output().decode("utf-8", errors="ignore").splitlines():
                log.info(line)

        else:
            worker = WaitForRunAsWorker(command)

        progress_dialog = ProgressDialog(worker, "Run as administrator", "Executing command...", "Cancel", busy=True, parent=parent)
        progress_dialog.show()
        if not progress_dialog.exec_():
            return False
        return True
