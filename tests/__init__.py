# -*- coding: utf-8 -*-
from unittest import TestCase

from PyQt4.QtGui import QApplication

import sys


def make_getitem(container):
    def getitem(name):
        return container[name]
    return getitem


def make_setitem(container):
    def setitem(name, val):
        container[name] = val
    return setitem


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
