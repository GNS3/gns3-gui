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


def make_getitem(container):
    def getitem(name):
        return container[name]
    return getitem


def make_setitem(container):
    def setitem(name, val):
        container[name] = val
    return setitem


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

    def tearDown(self):
        # Explicitly deallocate QApplication instance to avoid crashes
        del self.app

    def _init_page(self):
        self.page = CloudPreferencesPage()
        self.page.settings = mock.MagicMock()
        fake_settings = CLOUD_SETTINGS.copy()
        self.page.settings.__getitem__.side_effect = make_getitem(fake_settings)
        self.page.settings.__setitem__.side_effect = make_setitem(fake_settings)

    def test_defaults(self):
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

    def test_user_interaction(self):
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

    def test_load_settings(self):
        self.page.settings['cloud_store_api_key_chosen'] = True

        self.page.loadPreferences()

        self.page.settings['cloud_user_name'] = 'Bob'
        self.page.settings['cloud_api_key'] = '1234567890€'
        self.page.settings['cloud_store_api_key'] = True
        self.page.settings['cloud_store_api_key_chosen'] = True
        self.page.settings['cloud_provider'] = 'rackspace'
        self.page.settings['cloud_region'] = 'United States'
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
        self.assertEqual(self.page.uiRegionComboBox.currentText(), "United States")
        self.assertTrue(self.page.uiTermsCheckBox.isChecked())
        self.assertEqual(self.page.uiNumOfInstancesSpinBox.value(), 3)
        self.assertEqual(self.page.uiMemPerInstanceSpinBox.value(), 2)
        self.assertEqual(self.page.uiMemPerNewInstanceSpinBox.value(), 6)
        self.assertEqual(self.page.uiTimeoutSpinBox.value(), 120)

    def test_save_preferences(self):
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
        self.assertEqual(self.page.settings['cloud_region'], 'United States')
        self.assertTrue(self.page.settings['accepted_terms'])
        self.assertEqual(self.page.settings['instances_per_project'], 8)
        self.assertEqual(self.page.settings['memory_per_instance'], 16)
        self.assertEqual(self.page.settings['memory_per_new_instance'], 32)
        self.assertEqual(self.page.settings['instance_timeout'], 5)

    def test_clear_settings_on_user_request(self):
        # no mocking for this testcase
        page = CloudPreferencesPage()
        # first run, user stores settings on disk
        page.uiRememberAPIKeyRadioButton.setChecked(True)
        page.uiAPIKeyLineEdit.setText("myapikey")
        page.uiUserNameLineEdit.setText("myusername")
        page.uiTermsCheckBox.setChecked(True)
        page.savePreferences()
        settings = MainWindow.instance().cloud_settings()
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
