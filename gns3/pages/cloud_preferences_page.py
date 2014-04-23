# -*- coding: utf-8 -*-
from ..ui.cloud_preferences_page_ui import Ui_CloudPreferencesPageWidget

from PyQt4 import QtGui


class CloudPreferencesPage(QtGui.QWidget, Ui_CloudPreferencesPageWidget):
    """
    QWidget configuration page for cloud preferences.
    """
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
