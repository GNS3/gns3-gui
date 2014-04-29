# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest import mock
import sys

from PyQt4.QtTest import QTest
from PyQt4.Qt import QApplication, Qt
from PyQt4.QtCore import QTimer
from PyQt4 import QtGui

from gns3.pages.cloud_preferences_page import CloudPreferencesPage


settings_mock = {
    'cloud_user_name': '',
    'cloud_api_key': '',
    'cloud_store_api_key': False,
    'cloud_store_api_key_chosen': False,
}


def getitem(name):
    return settings_mock[name]


def setitem(name, val):
    settings_mock[name] = val


class TestCloudPreferencesPage(TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.app.setOrganizationName("GNS3")
        self.app.setOrganizationDomain("gns3.net")
        self.app.setApplicationName("Testsuite")
        self.page = CloudPreferencesPage()
        # mock settings instance inside the page widget
        self.page.settings = mock.MagicMock()
        self.page.settings.__getitem__.side_effect = getitem
        self.page.settings.__setitem__.side_effect = setitem

    def tearDown(self):
        # Explicitly deallocate QApplication instance to avoid crashes
        del self.app

    def test_defaults(self):
        self.page.loadPreferences()
        self.assertFalse(self.page.uiForgetAPIKeyRadioButton.isChecked())
        self.assertFalse(self.page.uiRememberAPIKeyRadioButton.isChecked())
        # saving preferences without setting "store or not" radio button triggers a message box
        def closeMsgBox():
            self.assertIsInstance(self.app.activeModalWidget(), QtGui.QMessageBox)
            self.app.activeModalWidget().close()
        QTimer.singleShot(50, closeMsgBox)
        valid = self.page._validate()
        self.assertFalse(valid)

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

        self.page.loadPreferences()

        self.assertEqual(self.page.uiUserNameLineEdit.text(), 'Bob')
        self.assertEqual(self.page.uiAPIKeyLineEdit.text(), '1234567890€')
        self.assertFalse(self.page.uiForgetAPIKeyRadioButton.isChecked())
        self.assertTrue(self.page.uiRememberAPIKeyRadioButton.isChecked())
