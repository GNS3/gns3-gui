# -*- coding: utf-8 -*-
from unittest import TestCase

from PyQt4.QtGui import QApplication

import sys


class BaseTest(TestCase):
    """
    Base class for all the tests
    """
    pass


class GUIBaseTest(BaseTest):
    """
    Base class implementing GUI boilerplates
    """
    def setUp(self):
        self.app = QApplication(sys.argv)

    def tearDown(self):
        del self.app
