# -*- coding: utf-8 -*-
from unittest import TestCase

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QSettings

import sys

from gns3.main_window import MainWindow


class TestCloudPreferencesPage(TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.app.setOrganizationName("GNS3")
        self.app.setOrganizationDomain("gns3.net")
        self.app.setApplicationName("Testsuite")
        self.mw = MainWindow()

    def tearDown(self):
        del self.app

    def test_settings_groups(self):
        settings = QSettings()
        fake_settings = {'foo': 'bar'}

        self.mw.setCloudSettings(fake_settings)
        self.assertIsNone(settings.value('foo'))
        settings.beginGroup('Cloud')
        self.assertEqual(settings.value('foo'), 'bar')
        settings.endGroup()

        self.mw.setSettings(fake_settings)
        self.assertIsNone(settings.value('foo'))
        settings.beginGroup(self.mw.__class__.__name__)
        self.assertEqual(settings.value('foo'), 'bar')
        settings.endGroup()
