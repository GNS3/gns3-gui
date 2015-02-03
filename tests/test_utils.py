# -*- coding: utf-8 -*-
from unittest import TestCase

from PyQt4.QtGui import QApplication

from gns3.utils.choices_spinbox import ChoicesSpinBox

import sys


class TestChoicesSpinBox(TestCase):

    def setUp(self):
        self.choices = [-1, 0, 1, 2, 3, 5, 8, 13]
        self.sb = ChoicesSpinBox(choices=self.choices)

    def test_steps(self):
        self.sb.setValue(0)
        self.sb.stepBy(1)
        self.assertEqual(self.sb.value(), 1)
        self.sb.stepBy(3)
        self.assertEqual(self.sb.value(), 5)
        self.sb.stepBy(-1)
        self.assertEqual(self.sb.value(), 3)

    def test_bounds(self):
        self.sb.setValue(100)
        self.assertEqual(self.sb.value(), 13)
        self.sb.setValue(-100)
        self.assertEqual(self.sb.value(), -1)
