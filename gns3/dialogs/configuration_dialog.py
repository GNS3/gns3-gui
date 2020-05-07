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
Dialog to configure and update node settings using widget pages.
"""

from ..qt import QtWidgets
from ..ui.configuration_dialog_ui import Ui_configurationDialog
from .node_properties_dialog import ConfigurationError


class ConfigurationDialog(QtWidgets.QDialog, Ui_configurationDialog):

    """
    Configuration dialog implementation.

    :param name: node template name
    :param settings: node template settings
    :param configuration_page: QWidget page
    :param parent: parent widget
    """

    def __init__(self, name, settings, configuration_page, parent):

        super().__init__(parent)
        self.setupUi(self)

        self.uiTitleLabel.setText(name)
        self.setWindowTitle(configuration_page.windowTitle())
        self.uiConfigStackedWidget.addWidget(configuration_page)
        self.uiConfigStackedWidget.setCurrentWidget(configuration_page)
        self.setModal(True)
        configuration_page.loadSettings(settings)
        self._settings = settings
        self._configuration_page = configuration_page

    def settings(self):
        return self._settings

    def on_uiButtonBox_clicked(self, button):
        """
        Slot called when a button of the uiButtonBox is clicked.

        :param button: button that was clicked (QAbstractButton)
        """

        if button == self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Cancel):
            QtWidgets.QDialog.reject(self)
        else:
            try:
                self._configuration_page.saveSettings(self._settings)
            except ConfigurationError:
                return
            QtWidgets.QDialog.accept(self)
