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

        from ..main_window import MainWindow
        self.settings = MainWindow.instance().settings()

    def _store_api_key(self):
        """
        helper method, returns whether user wants to store api keys or not
        """
        return self.uiRememberAPIKeyRadioButton.isChecked()

    def _validate(self):
        """
        Check if settings are ok
        """
        if not (self.uiRememberAPIKeyRadioButton.isChecked() and
                self.uiForgetAPIKeyRadioButton.isChecked()):
            QtGui.QMessageBox.critical(self, "Cloud Preferences",
                                       "Please choose if you want to persist your API keys or not.")
            return False
        return True

    def loadPreferences(self):
        """
        Load cloud preferences and populate the panel
        """

        self.uiUserNameLineEdit.setText(self.settings['cloud_user_name'])
        self.uiAPIKeyLineEdit.setText(self.settings['cloud_api_key'])
        do_store_api_key = self.settings.get("cloud_store_api_key")

        if not self.settings['cloud_store_api_key_chosen']:
            # do not select any radio button the first time
            pass
        elif do_store_api_key:
            self.uiRememberAPIKeyRadioButton.setChecked(True)
        else:
            self.uiForgetAPIKeyRadioButton.setChecked(True)

    def savePreferences(self):
        """
        Save cloud preferences

        TODO: cloud settings are temporarily hosted in MainWindow settings,
        move elsewhere?
        """
        if self._validate():
            if self._store_api_key():
                self.settings['cloud_user_name'] = self.uiUserNameLineEdit.text()
                self.settings['cloud_api_key'] = self.uiAPIKeyLineEdit.text()
                self.settings["cloud_store_api_key"] = True
            else:
                self.settings['cloud_user_name'] = ""
                self.settings['cloud_api_key'] = ""
                self.settings["cloud_store_api_key"] = False

            if not self.settings['cloud_store_api_key_chosen']:
                # user made a choice
                self.settings['cloud_store_api_key_chosen'] = True

            from ..main_window import MainWindow
            MainWindow.instance().setSettings(self.settings)

            return True
        return False