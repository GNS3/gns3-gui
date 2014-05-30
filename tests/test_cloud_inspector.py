# -*- coding: utf-8 -*-
from . import BaseTest
from . import GUIBaseTest
from . import make_setitem
from . import make_getitem

from PyQt4.Qt import Qt
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import QPoint

from gns3.cloud_inspector_view import InstanceTableModel
from gns3.cloud_inspector_view import CloudInspectorView
from gns3.main_window import MainWindow

from libcloud.compute.types import NodeState
from libcloud.compute.base import NodeSize
from libcloud.compute.drivers.dummy import DummyNodeDriver

from unittest import mock


def gen_fake_nodes(how_many):
    """
    Generate a number of fake nodes, temporary hack
    """
    driver = DummyNodeDriver(0)
    for i in range(how_many):
        yield driver.create_node()


class TestInstanceModel(BaseTest):
    def setUp(self):
        super(TestInstanceModel, self).setUp()
        self.model = InstanceTableModel()

    def test__get_status_icon_path(self):
        green = ':/icons/led_green.svg'
        yellow = ':/icons/led_yellow.svg'
        red = ':/icons/led_red.svg'
        self.assertEqual(self.model._get_status_icon_path(NodeState.RUNNING), green)
        self.assertEqual(self.model._get_status_icon_path(NodeState.REBOOTING), yellow)
        self.assertEqual(self.model._get_status_icon_path(NodeState.UNKNOWN), yellow)
        self.assertEqual(self.model._get_status_icon_path(NodeState.PENDING), yellow)
        self.assertEqual(self.model._get_status_icon_path(NodeState.STOPPED), red)
        self.assertEqual(self.model._get_status_icon_path(NodeState.TERMINATED), red)

    def test_add_instance(self):
        node = list(gen_fake_nodes(1))[0]
        node.name = 'Foo'
        node.size = NodeSize('', '', 2048, 0, 0, 0.0, '')
        node.status = NodeState.RUNNING

        self.model.addInstance(node)

        index = self.model.createIndex(0, 1)
        self.assertIsInstance(self.model.data(index, Qt.DecorationRole), QIcon)
        index = self.model.createIndex(0, 0)
        self.assertEqual(self.model.data(index, Qt.DisplayRole), 'Foo')
        index = self.model.createIndex(0, 2)
        self.assertEqual(self.model.data(index, Qt.DisplayRole), 2048)
        index = self.model.createIndex(0, 3)
        self.assertEqual(self.model.data(index, Qt.DisplayRole), 0)
        index = self.model.createIndex(0, 4)
        self.assertIsNone(self.model.data(index, Qt.DisplayRole))

    def test_get_instance(self):
        node1, node2 = gen_fake_nodes(2)
        self.model.addInstance(node1)
        self.model.addInstance(node2)
        self.assertEqual(self.model.getInstance(0), node1)
        self.assertEqual(self.model.getInstance(1), node2)
        self.assertIsNone(self.model.getInstance(2))

    def test_header_data(self):
        self.assertEqual(self.model.headerData(0, Qt.Vertical, Qt.DisplayRole), 1)
        self.assertEqual(self.model.headerData(0, Qt.Horizontal, Qt.DisplayRole), 'Instance')
        self.assertEqual(self.model.headerData(1, Qt.Horizontal, Qt.DisplayRole), '')
        self.assertEqual(self.model.headerData(2, Qt.Horizontal, Qt.DisplayRole), 'Size')
        self.assertEqual(self.model.headerData(3, Qt.Horizontal, Qt.DisplayRole), 'Devices')
        self.assertIsNone(self.model.headerData(4, Qt.Horizontal, Qt.DisplayRole))

    def test_update_instance_status(self):
        node1, node2 = gen_fake_nodes(2)
        self.model.addInstance(node1)
        self.assertEqual(node1.state, NodeState.RUNNING)
        node = self.model.getInstance(0)
        node.state = NodeState.STOPPED
        self.model.update_instance_status(node)
        node = self.model.getInstance(0)
        self.assertEqual(node.state, NodeState.STOPPED)
        self.model.update_instance_status(node2)  # noop

    def test_update(self):
        pass
        # TODO


class TestCloudInspectorView(GUIBaseTest):
    def setUp(self):
        super(TestCloudInspectorView, self).setUp()
        self.view = CloudInspectorView(None)

    def test_load(self):
        with mock.patch('gns3.cloud_inspector_view.import_from_string') as imp_:
            provider = mock.MagicMock()
            provider.return_value = provider
            provider.list_instances.return_value = list(gen_fake_nodes(2))
            imp_.return_value = provider

            settings = mock.MagicMock()
            settings_copy = MainWindow.instance().cloud_settings().copy()
            settings_copy['cloud_provider'] = 'rackspace'
            settings.__getitem__.side_effect = make_getitem(settings_copy)
            settings.__setitem__.side_effect = make_setitem(settings_copy)

            self.view.load(settings)

            # FIXME should be 2 as soon as we remove fake instances
            self.assertEqual(self.view._model.rowCount(), 7)

    def test_contextMenu(self):
        with mock.patch('gns3.cloud_inspector_view.QMenu') as qmenu:
            m = qmenu.return_value
            actions = []

            def add_action(action):
                actions.append(action)
            m.addAction.side_effect = add_action

            self.view._contextMenu(QPoint(10, 10))

            qmenu.assert_called_with(self.view.uiInstancesTableView)
            self.assertEqual(len(actions), 1)

    def test_delete_instance(self):
        self.view._provider = mock.MagicMock()
        self.view.uiInstancesTableView = mock.MagicMock()
        self.view._model = mock.MagicMock()
        instance = mock.MagicMock()
        self.view._model.getInstance.return_value = instance
        self.view.uiInstancesTableView.selectedIndexes.return_value = [mock.MagicMock()]
        self.view._deleteSelectedInstance()

        self.view._provider.delete_instance.assert_called_with(instance)
