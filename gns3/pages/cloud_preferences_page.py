# -*- coding: utf-8 -*-
from ..ui.cloud_preferences_page_ui import Ui_CloudPreferencesPageWidget
from ..settings import CLOUD_PROVIDERS
from ..utils import import_from_string

from ..qt import QtCore, QtGui


class CloudPreferencesPage(QtGui.QWidget, Ui_CloudPreferencesPageWidget):

    """
    QWidget configuration page for cloud preferences.
    """

    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        # the list containing provider controller classes
        self.provider_controllers = {}
        # map region ids to combobox indexes
        self.region_index_id = []
        # map provider ids to combobox indexes
        self.provider_index_id = []
        # map image ids to combobox indexes
        self.image_index_id = []
        # map flavor ids to combobox indexes
        self.flavor_index_id = []

        # insert Terms&Condition link inside the checkbox
        self.uiTermsLabel.setText('Accept <a href="{}">Terms and Conditions</a>'.format('#'))

        from ..main_window import MainWindow
        self.settings = MainWindow.instance().cloudSettings()

    def _get_region_index(self, region_id):
        try:
            return self.region_index_id.index(region_id)
        except ValueError:
            return -1

    def _get_image_index(self, image_name):
        try:
            return self.image_index_id.index(image_name)
        except ValueError:
            return -1

    def _get_flavor_index(self, flavor_id):
        try:
            return self.flavor_index_id.index(flavor_id)
        except ValueError:
            return -1

    def _store_api_key(self):
        """
        helper method, returns whether user wants to store api keys or not
        """
        return self.uiRememberAPIKeyRadioButton.isChecked()

    def _terms_accepted(self):
        return self.uiTermsCheckBox.checkState() == QtCore.Qt.Checked

    def _validate(self):
        """
        Check if settings are ok
        """
        errors = ""
        can_authenticate = self.uiUserNameLineEdit.text() and self.uiAPIKeyLineEdit.text()
        remember_have_been_set = self.uiRememberAPIKeyRadioButton.isChecked() or \
            self.uiForgetAPIKeyRadioButton.isChecked()

        if can_authenticate and not remember_have_been_set:
            errors += "Please choose if you want to persist your API keys or not.\n"

        if can_authenticate and not self._terms_accepted():
            errors += "You have to accept Terms and Conditions to proceed.\n"

        if errors:
            QtGui.QMessageBox.critical(self, "Cloud Preferences", errors)
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
        for k, v in CLOUD_PROVIDERS.items():
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
        default_image = self.settings['default_image']
        default_flavor = self.settings['default_flavor']
        new_instance_flavor = self.settings['new_instance_flavor']

        # instance a provider controller and try to use it
        try:
            provider = self.provider_controllers[provider_id](username, apikey)
            if provider.authenticate():
                provider.set_region(region)
                # fill region combo box
                self.region_index_id = [""]
                self.uiRegionComboBox.addItem("Select region...")
                for r in provider.list_regions():
                    api_region_names = list(r.keys())
                    api_libcloud_names = list(r.values())
                    self.uiRegionComboBox.addItem(api_region_names[0])
                    self.region_index_id.append(api_libcloud_names[0])
                # fill image template list
                self.image_index_id = ["cc6e0096-84f9-4beb-a21e-d80a11a769d8"]
                self.uiImageTemplateComboBox.addItem("Ubuntu 14.04")
                self.uiImageTemplateComboBox.setCurrentIndex(0)
                # fill flavor comboboxes
                for id, name in provider.list_flavors().items():
                    self.uiInstanceFlavorComboBox.addItem(name)
                    self.uiNewInstanceFlavorComboBox.addItem(name)
                    self.flavor_index_id.append(id)
        except KeyError:
            # username/apikey/provider are not set
            pass

        # populate all the cloud stuff
        self.uiUserNameLineEdit.setText(username)
        self.uiAPIKeyLineEdit.setText(apikey)
        self.uiCloudProviderComboBox.setCurrentIndex(self.provider_index_id.index(provider_id))
        self.uiRegionComboBox.setCurrentIndex(self._get_region_index(region))
        if self.settings.get("cloud_store_api_key"):
            self.uiRememberAPIKeyRadioButton.setChecked(True)
        else:
            self.uiForgetAPIKeyRadioButton.setChecked(True)
        self.uiNumOfInstancesSpinBox.setValue(self.settings['instances_per_project'])
        self.uiTermsCheckBox.setChecked(self.settings['accepted_terms'])
        self.uiTimeoutSpinBox.setValue(self.settings['instance_timeout'])
        self.uiImageTemplateComboBox.setCurrentIndex(self._get_image_index(default_image))

        idx = self._get_flavor_index(default_flavor)
        if idx < 0:
            idx = 0
        self.uiInstanceFlavorComboBox.setCurrentIndex(idx)

        idx = self._get_flavor_index(new_instance_flavor)
        if idx < 0:
            idx = 0
        self.uiNewInstanceFlavorComboBox.setCurrentIndex(idx)

    def savePreferences(self):
        """
        Save cloud preferences
        """
        if self._validate():
            self.settings['cloud_user_name'] = self.uiUserNameLineEdit.text()
            self.settings['cloud_api_key'] = self.uiAPIKeyLineEdit.text()
            self.settings['cloud_store_api_key'] = True
            if self.uiCloudProviderComboBox.currentIndex() >= 0:
                self.settings['cloud_provider'] = \
                    self.provider_index_id[self.uiCloudProviderComboBox.currentIndex()]
            if self.uiRegionComboBox.currentIndex() >= 0:
                self.settings['cloud_region'] = \
                    self.region_index_id[self.uiRegionComboBox.currentIndex()]
            self.settings['instances_per_project'] = self.uiNumOfInstancesSpinBox.value()
            if len(self.flavor_index_id):
                self.settings['default_flavor'] = self.flavor_index_id[self.uiInstanceFlavorComboBox.currentIndex()]
                self.settings['new_instance_flavor'] = self.flavor_index_id[self.uiNewInstanceFlavorComboBox.currentIndex()]
            self.settings['accepted_terms'] = self.uiTermsCheckBox.isChecked()
            self.settings['instance_timeout'] = self.uiTimeoutSpinBox.value()
            if self.uiImageTemplateComboBox.currentIndex() >= 0:
                self.settings['default_image'] = \
                    self.image_index_id[self.uiImageTemplateComboBox.currentIndex()]

            if not self.settings['cloud_store_api_key_chosen']:
                # user made a choice at this point
                self.settings['cloud_store_api_key_chosen'] = True

            from ..main_window import MainWindow
            MainWindow.instance().setCloudSettings(self.settings, persist=self._store_api_key())

            return True
        return False
