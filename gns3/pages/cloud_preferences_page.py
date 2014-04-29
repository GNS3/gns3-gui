# -*- coding: utf-8 -*-
from ..ui.cloud_preferences_page_ui import Ui_CloudPreferencesPageWidget
from ..settings import CLOUD_PROVIDERS, CLOUD_REGIONS

from PyQt4 import QtGui

import importlib
from unittest import mock


# mock api cloud interface until cloud.py module is merged
RackspaceCtrl = mock.MagicMock()
RackspaceCtrl.return_value = RackspaceCtrl
RackspaceCtrl.list_regions.return_value = ['United States', 'Ireland']
FAKE_PROVIDERS = {
    "rackspace": ("Rackspace", 'gns3.pages.cloud_preferences_page.RackspaceCtrl'),
}


def import_from_string(string_val):
    """
    Attempt to import a class from a string representation.
    """
    try:
        parts = string_val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError:
        msg = "Could not import '%s'." % string_val
        raise ImportError(msg)


class CloudPreferencesPage(QtGui.QWidget, Ui_CloudPreferencesPageWidget):
    """
    QWidget configuration page for cloud preferences.
    """
    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        # the list containing provider controller classes
        self.provider_controllers = {}
        # map region ids to combobox indexes
        self.region_index_id = []
        # map provider ids to combobox indexes
        self.provider_index_id = []

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
        check_remember_setting = self.uiUserNameLineEdit.text() and self.uiAPIKeyLineEdit.text()
        remember_have_been_set = self.uiRememberAPIKeyRadioButton.isChecked() or \
            self.uiForgetAPIKeyRadioButton.isChecked()
        if check_remember_setting and not remember_have_been_set:
            QtGui.QMessageBox.critical(self, "Cloud Preferences",
                                       "Please choose if you want to persist your API keys or not.")
            return False
        return True

    def loadPreferences(self):
        """
        Load cloud preferences and populate the panel
        """
        self.provider_controllers.clear()

        # fill provider combobox
        self.provider_index_id = [""]
        self.uiCloudProviderComboBox.addItem("Select provider...")
        for k, v in FAKE_PROVIDERS.items():
            self.uiCloudProviderComboBox.addItem(v[0])
            self.provider_controllers[k] = import_from_string(v[1])
            self.provider_index_id.append(k)

        # do not select anything the very first time this page is loaded
        if not self.settings['cloud_store_api_key_chosen']:
            return

        username = self.settings['cloud_user_name']
        apikey = self.settings['cloud_api_key']
        provider_id = self.settings['cloud_provider']
        region = self.settings['cloud_region']

        # instance a provider controller and try to use it
        provider = self.provider_controllers[provider_id]()
        if provider.authenticate():
            # fill region combo box
            self.region_index_id = [""]
            self.uiRegionComboBox.addItem("Select region...")
            for r in provider.list_regions():
                self.uiRegionComboBox.addItem(r)
                self.region_index_id.append(r)

        # populate all the cloud stuff
        self.uiUserNameLineEdit.setText(username)
        self.uiAPIKeyLineEdit.setText(apikey)
        self.uiCloudProviderComboBox.setCurrentIndex(self.provider_index_id.index(provider_id))
        self.uiRegionComboBox.setCurrentIndex(self.region_index_id.index(region))
        if self.settings.get("cloud_store_api_key"):
            self.uiRememberAPIKeyRadioButton.setChecked(True)
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
