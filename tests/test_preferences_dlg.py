# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest import mock
import sys

from PyQt4.QtTest import QTest
from PyQt4.Qt import QApplication, Qt
from PyQt4.QtCore import QTimer
from PyQt4 import QtGui

from gns3.pages.cloud_preferences_page import CloudPreferencesPage
from gns3.settings import CLOUD_SETTINGS


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
        QTimer.singleShot(50, closeMsgBox)
        self.page.uiUserNameLineEdit.setText('foo')
        self.page.uiAPIKeyLineEdit.setText('bar')
        valid = self.page._validate()
        self.assertFalse(valid)
        self.assertEqual(self.page.uiCloudProviderComboBox.currentIndex(), 0)
        self.assertEqual(self.page.uiRegionComboBox.currentIndex(), 0)

    def test_user_interaction(self):
        """
        Simulate user interactions via keyboard or mouse and check dialog status
        """
        QTest.keyClicks(self.page.uiUserNameLineEdit, "Bob")
        self.assertEqual(self.page.uiUserNameLineEdit.text(), 'Bob')
        QTest.keyClick(self.page.uiAPIKeyLineEdit, Qt.Key_Eacute)
        self.assertEqual(self.page.uiAPIKeyLineEdit.text(), 'É')
        QTest.mouseClick(self.page.uiRememberAPIKeyRadioButton, Qt.LeftButton)
        self.assertTrue(self.page._store_api_key())
        self.assertTrue(self.page._validate())
        QTest.mouseClick(self.page.uiForgetAPIKeyRadioButton, Qt.LeftButton)
        self.assertFalse(self.page._store_api_key())
        self.assertTrue(self.page._validate())

    def test_load_settings(self):
        self.page.settings['cloud_user_name'] = 'Bob'
        self.page.settings['cloud_api_key'] = '1234567890€'
        self.page.settings['cloud_store_api_key'] = True
        self.page.settings['cloud_store_api_key_chosen'] = True
        self.page.settings['cloud_provider'] = 'rackspace'
        self.page.settings['cloud_region'] = 'us'

        self.page.loadPreferences()

        self.assertEqual(self.page.uiUserNameLineEdit.text(), 'Bob')
        self.assertEqual(self.page.uiAPIKeyLineEdit.text(), '1234567890€')
        self.assertFalse(self.page.uiForgetAPIKeyRadioButton.isChecked())
        self.assertTrue(self.page.uiRememberAPIKeyRadioButton.isChecked())
        self.assertEqual(self.page.uiCloudProviderComboBox.currentText(), "Rackspace")
        self.assertEqual(self.page.uiRegionComboBox.currentText(), "United States")
