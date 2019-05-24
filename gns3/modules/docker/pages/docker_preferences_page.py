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
Configuration page for Docker preferences.
"""


from gns3.qt import QtWidgets

from .. import Docker
from ..ui.docker_preferences_page_ui import Ui_DockerPreferencesPageWidget
from ..settings import DOCKER_SETTINGS


class DockerPreferencesPage(QtWidgets.QWidget, Ui_DockerPreferencesPageWidget):
    """
    QWidget preference page for Docker.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # connect signals
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(DOCKER_SETTINGS)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: Docker settings
        """

        pass

    def loadPreferences(self):
        """
        Loads Docker preferences.
        """

        docker_settings = Docker.instance().settings()
        self._populateWidgets(docker_settings)

    def savePreferences(self):
        """
        Saves Docker preferences.
        """

        new_settings = {}
        Docker.instance().setSettings(new_settings)
