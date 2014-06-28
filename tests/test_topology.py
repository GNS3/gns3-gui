# -*- coding: utf-8 -*-
from unittest import TestCase

from gns3.topology import Topology
from gns3.main_window import MainWindow


class TestTopology(TestCase):
    def setUp(self):
        self.t = Topology.instance()

    def tearDown(self):
        del self.t

    def test_resources_type(self):
        self.assertEqual(self.t._resources_type, 'local')
        self.t._resources_type = 'cloud'
        self.assertEqual(self.t.resourcesType, 'cloud')
        self.t._resources_type = 'local'
        self.assertEqual(self.t.resourcesType, 'local')

    def test_resources_type_dumped(self):
        test_settings = {'project_type': 'cloud'}
        MainWindow.instance() ._project_settings.update(test_settings)
        topology = self.t.dump()
        self.assertIn('resources_type', topology)
        self.assertEqual(topology['resources_type'], 'cloud')

    def test_resources_type_load(self):
        self.t.reset()
        self.assertEqual(self.t.resourcesType, 'local')  # default value
        topology = {
            'project_type': 'cloud',
            'type': 'topology',
            'topology': {},
            'version': '3.0',
        }
        self.t.load(topology)
        self.assertEqual(self.t.resourcesType, 'cloud')

    def test_reset(self):
        self.t._links = ['foo', 'baz', 'bar']
        self.t._nodes = ['foo', 'baz', 'bar']
        self.t._initialized_nodes = ['foo', 'baz', 'bar']
        test_settings = {'project_type': 'cloud'}
        MainWindow.instance()._project_settings.update(test_settings)

        self.t.reset()

        self.assertEqual(len(self.t._links), 0)
        self.assertEqual(len(self.t._nodes), 0)
        self.assertEqual(len(self.t._initialized_nodes), 0)
        self.assertEqual(self.t._resources_type, 'local')
