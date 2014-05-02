# -*- coding: utf-8 -*-
from unittest import TestCase

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QSettings

import sys

from gns3.main_window import MainWindow
from gns3.main_window import CLOUD_SETTINGS_GROUP


class TestCloudPreferencesPage(TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.app.setOrganizationName("GNS3")
        self.app.setOrganizationDomain("gns3.net")
        self.app.setApplicationName("Testsuite")
        self.mw = MainWindow()
        self.settings = QSettings()

    def tearDown(self):
        del self.app
        self.settings.clear()

    def test_settings_groups(self):
        fake_settings = {'foo': 'bar'}

        self.mw.setCloudSettings(fake_settings, persist=True)
        self.assertIsNone(self.settings.value('foo'))
        self.settings.beginGroup(CLOUD_SETTINGS_GROUP)
        self.assertEqual(self.settings.value('foo'), 'bar')
        self.settings.endGroup()

        self.mw.setSettings(fake_settings)
        self.assertIsNone(self.settings.value('foo'))
        self.settings.beginGroup(self.mw.__class__.__name__)
        self.assertEqual(self.settings.value('foo'), 'bar')
        self.settings.endGroup()

    def test_cloud_settings_store(self):
        fake_settings = {'foo': 'bar'}

        self.mw.setCloudSettings(fake_settings, persist=True)
        self.settings.beginGroup(CLOUD_SETTINGS_GROUP)
        self.assertEqual(self.settings.value('foo'), 'bar')
        self.settings.endGroup()

        self.settings.clear()

        self.mw.setCloudSettings(fake_settings, persist=False)
        self.settings.beginGroup(CLOUD_SETTINGS_GROUP)
        self.assertIsNone(self.settings.value('foo'))
        self.settings.endGroup()
