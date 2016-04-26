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

from gns3.qt import QtWidgets, QtCore
from gns3.ui.new_appliance_dialog_ui import Ui_NewApplianceDialog
from gns3.dialogs.preferences_dialog import PreferencesDialog


import logging
log = logging.getLogger(__name__)


class NewApplianceDialog(QtWidgets.QDialog, Ui_NewApplianceDialog):
    """
    This dialog allow user to create a new appliance by opening
    the correct creation dialog
    """

    def __init__(self, parent):

        super().__init__(parent)
        self.setupUi(self)
        self.uiOkButton.clicked.connect(self._okButtonClickedSlot)
        self.uiImportApplianceTemplatePushButton.clicked.connect(self._importApplianceTemplatePushButtonClickedSlot)

    def _importApplianceTemplatePushButtonClickedSlot(self):
        self.accept()
        from gns3.main_window import MainWindow
        MainWindow.instance().openApplianceActionSlot()

    def _okButtonClickedSlot(self):
        self.accept()
        dialog = PreferencesDialog(self.parent())
        if self.uiAddIOSRouterRadioButton.isChecked():
            self._setPreferencesPane(dialog, "Dynamips").uiNewIOSRouterPushButton.clicked.emit(False)
        elif self.uiAddIOUDeviceRadioButton.isChecked():
            self._setPreferencesPane(dialog, "IOS on UNIX").uiNewIOUDevicePushButton.clicked.emit(False)
        elif self.uiAddQemuVMRadioButton.isChecked():
            self._setPreferencesPane(dialog, "QEMU").uiNewQemuVMPushButton.clicked.emit(False)
        elif self.uiAddVirtualBoxVMRadioButton.isChecked():
            self._setPreferencesPane(dialog, "VirtualBox").uiNewVirtualBoxVMPushButton.clicked.emit(False)
        elif self.uiAddVMwareVMRadioButton.isChecked():
            self._setPreferencesPane(dialog, "VMware").uiNewVMwareVMPushButton.clicked.emit(False)
        elif self.uiAddDockerVMRadioButton.isChecked():
            self._setPreferencesPane(dialog, "Docker").uiNewDockerVMPushButton.clicked.emit(False)
        dialog.show()

    def _setPreferencesPane(self, dialog, name):
        """
        Finds the first child of the QTreeWidgetItem name.

        :param dialog: PreferencesDialog instance
        :param name: QTreeWidgetItem name

        :returns: current QWidget
        """

        pane = dialog.uiTreeWidget.findItems(name, QtCore.Qt.MatchFixedString)[0]
        child_pane = pane.child(0)
        dialog.uiTreeWidget.setCurrentItem(child_pane)
        return dialog.uiStackedWidget.currentWidget()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    dialog = NewApplianceDialog(main, console=True)
    dialog.show()
    exit_code = app.exec_()
