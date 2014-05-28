# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest import mock
import sys

from PyQt4.QtTest import QTest
from PyQt4.Qt import QApplication, Qt
from PyQt4.QtCore import QTimer
from PyQt4 import QtGui
from PyQt4 import QtCore

from gns3.pages.cloud_preferences_page import CloudPreferencesPage
from gns3.settings import CLOUD_SETTINGS
from gns3.main_window import MainWindow
from gns3.main_window import CLOUD_SETTINGS_GROUP
from gns3.preferences_dialog import PreferencesDialog

import pytest


def make_getitem(container):
    def getitem(name):
        return container[name]
    return getitem


def make_setitem(container):
    def setitem(name, val):
        container[name] = val
    return setitem


class TestPreferencesPage(TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.dialog = PreferencesDialog(None)

    def tearDown(self):
        del self.app

    def test_apply_preferences(self):
        self.assertTrue(self.dialog._applyPreferences())
        mock_page = mock.MagicMock()
        mock_page.data.return_value = mock_page
        mock_page.savePreferences.return_value = False
        self.dialog._items = [mock_page]
        self.assertFalse(self.dialog._applyPreferences())
        mock_page.savePreferences.return_value = None
        self.assertTrue(self.dialog._applyPreferences())


@mock.patch('gns3.pages.cloud_preferences_page.import_from_string')
class TestCloudPreferencesPage(TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.app.setOrganizationName("GNS3")
        self.app.setOrganizationDomain("gns3.net")
        self.app.setApplicationName("Testsuite")
        self.page = CloudPreferencesPage()
        # mock settings instance inside the page widget
        self.page.settings = mock.MagicMock()
        settings_copy = CLOUD_SETTINGS.copy()
        self.page.settings.__getitem__.side_effect = make_getitem(settings_copy)
        self.page.settings.__setitem__.side_effect = make_setitem(settings_copy)
        self._init_page()
        # RackspaceCtrl mock
        self.ctrl_mock = mock.MagicMock()
        self.ctrl_mock.return_value = self.ctrl_mock
        self.ctrl_mock.authenticate.return_value = True
        self.ctrl_mock.list_regions.return_value = [{'ORD': 'ord'}, {'SYD': 'syd'}, {'DFW': 'dfw'},
                                                    {'HKG': 'hkg'}, {'IAD': 'iad'}]

    def tearDown(self):
        # Explicitly deallocate QApplication instance to avoid crashes
        del self.app

    def _init_page(self):
        self.page = CloudPreferencesPage()
        self.page.settings = mock.MagicMock()
        fake_settings = CLOUD_SETTINGS.copy()
        self.page.settings.__getitem__.side_effect = make_getitem(fake_settings)
        self.page.settings.__setitem__.side_effect = make_setitem(fake_settings)

    def test_defaults(self, *args, **kwargs):
        self.page.loadPreferences()
        self.assertFalse(self.page.uiForgetAPIKeyRadioButton.isChecked())
        self.assertFalse(self.page.uiRememberAPIKeyRadioButton.isChecked())
        # saving preferences without setting "store or not" radio button triggers a message box
        def closeMsgBox():
            self.assertIsInstance(self.app.activeModalWidget(), QtGui.QMessageBox)
            self.app.activeModalWidget().close()
        QTimer.singleShot(100, closeMsgBox)
        self.page.uiUserNameLineEdit.setText('foo')
        self.page.uiAPIKeyLineEdit.setText('bar')
        valid = self.page._validate()
        self.assertFalse(valid)
        self.assertEqual(self.page.uiCloudProviderComboBox.currentIndex(), 0)
        self.assertEqual(self.page.uiRegionComboBox.currentIndex(), -1)  # not set
        self.assertEqual(self.page.uiMemPerInstanceSpinBox.value(), 1)
        self.assertEqual(self.page.uiMemPerNewInstanceSpinBox.value(), 1)
        self.assertEqual(self.page.uiNumOfInstancesSpinBox.value(), 0)
        self.assertFalse(self.page.uiTermsCheckBox.isChecked())
        self.assertEqual(self.page.uiTimeoutSpinBox.value(), 30)

    def test_user_interaction(self, *args, **kwargs):
        """
        Simulate user interactions via keyboard or mouse and check dialog status
        """
        # following line is because of https://bugreports.qt-project.org/browse/QTBUG-14483
        self.page.show()

        QTest.keyClicks(self.page.uiUserNameLineEdit, "Bob")
        self.assertEqual(self.page.uiUserNameLineEdit.text(), 'Bob')
        QTest.keyClick(self.page.uiAPIKeyLineEdit, Qt.Key_Eacute)
        self.assertEqual(self.page.uiAPIKeyLineEdit.text(), 'É')
        QTest.mouseClick(self.page.uiRememberAPIKeyRadioButton, Qt.LeftButton)
        self.assertTrue(self.page._store_api_key())
        QTest.mouseClick(self.page.uiTermsCheckBox, Qt.LeftButton)
        self.assertTrue(self.page.uiTermsCheckBox.isChecked())
        QTest.mouseClick(self.page.uiForgetAPIKeyRadioButton, Qt.LeftButton)
        self.assertFalse(self.page._store_api_key())

        self.assertTrue(self.page._validate())

    def test_load_settings(self, mock_1):
        mock_1.return_value = self.ctrl_mock

        self.page.settings['cloud_store_api_key_chosen'] = True

        self.page.loadPreferences()

        self.page.settings['cloud_user_name'] = 'Bob'
        self.page.settings['cloud_api_key'] = '1234567890€'
        self.page.settings['cloud_store_api_key'] = True
        self.page.settings['cloud_store_api_key_chosen'] = True
        self.page.settings['cloud_provider'] = 'rackspace'
        self.page.settings['cloud_region'] = 'ORD'
        self.page.settings['accepted_terms'] = True
        self.page.settings['instances_per_project'] = 3
        self.page.settings['memory_per_instance'] = 2
        self.page.settings['memory_per_new_instance'] = 6
        self.page.settings['instance_timeout'] = 120

        self.page.loadPreferences()

        self.assertEqual(self.page.uiUserNameLineEdit.text(), 'Bob')
        self.assertEqual(self.page.uiAPIKeyLineEdit.text(), '1234567890€')
        self.assertFalse(self.page.uiForgetAPIKeyRadioButton.isChecked())
        self.assertTrue(self.page.uiRememberAPIKeyRadioButton.isChecked())
        self.assertEqual(self.page.uiCloudProviderComboBox.currentText(), "Rackspace")
        self.assertEqual(self.page.uiRegionComboBox.currentText(), "ord")
        self.assertTrue(self.page.uiTermsCheckBox.isChecked())
        self.assertEqual(self.page.uiNumOfInstancesSpinBox.value(), 3)
        self.assertEqual(self.page.uiMemPerInstanceSpinBox.value(), 2)
        self.assertEqual(self.page.uiMemPerNewInstanceSpinBox.value(), 6)
        self.assertEqual(self.page.uiTimeoutSpinBox.value(), 120)

    def test_save_preferences(self, mock_1):
        mock_1.return_value = self.ctrl_mock

        self.page.settings['cloud_store_api_key_chosen'] = True
        self.page.settings['cloud_provider'] = 'rackspace'
        self.page.loadPreferences()

        self.page.uiUserNameLineEdit.setText("foo")
        self.page.uiAPIKeyLineEdit.setText("bar")
        self.page.uiRememberAPIKeyRadioButton.setChecked(True)
        self.page.uiTermsCheckBox.setChecked(True)
        self.page.uiRememberAPIKeyRadioButton.setChecked(True)
        self.page.uiCloudProviderComboBox.setCurrentIndex(1)
        self.page.uiRegionComboBox.setCurrentIndex(1)
        self.page.uiTermsCheckBox.setChecked(True)
        self.page.uiNumOfInstancesSpinBox.setValue(8)
        self.page.uiMemPerInstanceSpinBox.setValue(16)
        self.page.uiMemPerNewInstanceSpinBox.setValue(32)
        self.page.uiTimeoutSpinBox.setValue(5)

        self.page.savePreferences()

        self.assertTrue(self.page.settings['cloud_store_api_key'])
        self.assertEqual(self.page.settings['cloud_provider'], 'rackspace')
        self.assertEqual(self.page.settings['cloud_region'], 'ORD')
        self.assertTrue(self.page.settings['accepted_terms'])
        self.assertEqual(self.page.settings['instances_per_project'], 8)
        self.assertEqual(self.page.settings['memory_per_instance'], 16)
        self.assertEqual(self.page.settings['memory_per_new_instance'], 32)
        self.assertEqual(self.page.settings['instance_timeout'], 5)

    def test_clear_settings_on_user_request(self, *args, **kwargs):
        # no mocking for this testcase
        page = CloudPreferencesPage()
        # first run, user stores settings on disk
        page.uiRememberAPIKeyRadioButton.setChecked(True)
        page.uiAPIKeyLineEdit.setText("myapikey")
        page.uiUserNameLineEdit.setText("myusername")
        page.uiTermsCheckBox.setChecked(True)
        page.savePreferences()
        settings = MainWindow.instance().cloudSettings()
        self.assertTrue(settings.get('cloud_store_api_key'))
        self.assertEqual(settings.get('cloud_api_key'), 'myapikey')
        self.assertEqual(settings.get('cloud_user_name'), 'myusername')
        # now users change their mind
        page.uiForgetAPIKeyRadioButton.setChecked(True)
        page.savePreferences()
        # mainwindow settings should be still valid at this point...
        self.assertTrue(settings.get('cloud_store_api_key'))
        self.assertEqual(settings.get('cloud_api_key'), 'myapikey')
        self.assertEqual(settings.get('cloud_user_name'), 'myusername')
        # ...and values on disk should be gone
        stored_settings = QtCore.QSettings()
        stored_settings.beginGroup(CLOUD_SETTINGS_GROUP)
        self.assertFalse(stored_settings.value('cloud_store_api_key', type=bool))
        self.assertEqual(stored_settings.value('cloud_api_key', type=str), '')
        self.assertEqual(stored_settings.value('cloud_user_name', type=str), '')


@pytest.mark.skipif(not pytest.config.getvalue("username"),
                    reason="--username <user> was not specified")
@pytest.mark.skipif(not pytest.config.getvalue("apikey"),
                    reason="--apikey <key> was not specified")
class TestCloudPreferencesPageIntegration(TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.page = CloudPreferencesPage()

    def tearDown(self):
        del self.app

    def test_fill_region(self):
        self.page.settings['cloud_store_api_key_chosen'] = True
        self.page.settings['cloud_user_name'] = pytest.config.getvalue("username")
        self.page.settings['cloud_api_key'] = pytest.config.getvalue("apikey")
        self.page.settings['cloud_provider'] = 'rackspace'
        self.page.loadPreferences()
        region_labels = []
        for i in range(self.page.uiRegionComboBox.model().rowCount()):
            region_labels.append(self.page.uiRegionComboBox.model().item(i,0).text())
        self.assertTrue(len(region_labels) > 1)
        self.assertIn('ord', region_labels)

