# -*- coding: utf-8 -*-
import unittest

from PyQt4.QtTest import QTest
from PyQt4.Qt import QApplication

import sys

from gns3.pages.cloud_preferences_page import CloudPreferencesPage


class TestCloudPreferencesPage(unittest.TestCase):
    """
    Test Cloud Preferences Page
    """
    def setUp(self):
        """
        Instantiate a QtApplication and the form to be tested
        """
        self.app = QApplication(sys.argv)
        self.form = CloudPreferencesPage()

    def test_defaults(self):
        """
        Test default values for page widget
        """
        # no default values for these!
        self.assertFalse(self.form.uiForgetAPIKeyRadioButton.isChecked())
        self.assertFalse(self.form.uiRememberAPIKeyRadioButton.isChecked())