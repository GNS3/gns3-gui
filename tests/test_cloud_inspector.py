# -*- coding: utf-8 -*-
from . import BaseTest

from PyQt4.QtGui import QIcon

from gns3.cloud_inspector_view import InstanceTableModel

from libcloud.compute.types import NodeState


class TestInstanceModel(BaseTest):
    def test__get_status_icon_path(self):
        model = InstanceTableModel()
        green = ':/icons/led_green.svg'
        yellow = ':/icons/led_yellow.svg'
        red = ':/icons/led_red.svg'
        self.assertEqual(model._get_status_icon_path(NodeState.RUNNING), green)
        self.assertEqual(model._get_status_icon_path(NodeState.REBOOTING), yellow)
        self.assertEqual(model._get_status_icon_path(NodeState.UNKNOWN), yellow)
        self.assertEqual(model._get_status_icon_path(NodeState.PENDING), yellow)
        self.assertEqual(model._get_status_icon_path(NodeState.STOPPED), red)
        self.assertEqual(model._get_status_icon_path(NodeState.TERMINATED), red)
