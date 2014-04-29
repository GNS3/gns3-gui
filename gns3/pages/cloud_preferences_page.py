# -*- coding: utf-8 -*-
from ..ui.cloud_preferences_page_ui import Ui_CloudPreferencesPageWidget
from ..settings import CLOUD_PROVIDERS, CLOUD_REGIONS

from PyQt4 import QtGui


class CloudPreferencesPage(QtGui.QWidget, Ui_CloudPreferencesPageWidget):
    """
    QWidget configuration page for cloud preferences.
    """
    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        # fill providers combo box
        self.provider_index_id = [""]
        self.uiCloudProviderComboBox.addItem("Select provider...")
        for k, v in CLOUD_PROVIDERS.items():
            self.uiCloudProviderComboBox.addItem(v)
            self.provider_index_id.append(k)

        # fill region combo box
        self.region_index_id = []
        for k, v in CLOUD_REGIONS.items():
            self.uiRegionComboBox.addItem(v)
            self.region_index_id.append(k)

        from ..main_window import MainWindow
        self.settings = MainWindow.instance().cloud_settings()

    def _store_api_key(self):
        """
        helper method, returns whether user wants to store api keys or not
        """
        return self.uiRememberAPIKeyRadioButton.isChecked()

    def _validate(self):
        """
        Check if settings are ok
        """
        if (not self.uiRememberAPIKeyRadioButton.isChecked() and
                not self.uiForgetAPIKeyRadioButton.isChecked()):
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
            # populate all the cloud stuff
            self.uiRememberAPIKeyRadioButton.setChecked(True)
            cloud_p = self.settings['cloud_provider']
            if cloud_p:
                self.uiCloudProviderComboBox.setCurrentIndex(self.provider_index_id.index(cloud_p))
            self.uiRegionComboBox.setCurrentIndex(
                self.region_index_id.index(self.settings['cloud_region']))

        else:
            self.uiForgetAPIKeyRadioButton.setChecked(True)

    def savePreferences(self):
        """
        Save cloud preferences
        """
        if self._validate():
            if self._store_api_key():
                self.settings['cloud_user_name'] = self.uiUserNameLineEdit.text()
                self.settings['cloud_api_key'] = self.uiAPIKeyLineEdit.text()
                self.settings['cloud_store_api_key'] = True
                self.settings['cloud_provider'] = \
                    self.provider_index_id[self.uiCloudProviderComboBox.currentIndex()]
                self.settings['cloud_region'] = \
                    self.region_index_id[self.uiRegionComboBox.currentIndex()]
            else:
                self.settings['cloud_user_name'] = ""
                self.settings['cloud_api_key'] = ""
                self.settings['cloud_store_api_key'] = False
                del self.settings['cloud_provider']
                del self.settings['cloud_region']

            if not self.settings['cloud_store_api_key_chosen']:
                # user made a choice
                self.settings['cloud_store_api_key_chosen'] = True

            from ..main_window import MainWindow
            MainWindow.instance().setCloudSettings(self.settings, store=self._store_api_key())

            return True
        return False
