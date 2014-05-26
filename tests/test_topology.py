# -*- coding: utf-8 -*-
from unittest import TestCase

from gns3.topology import Topology


class TestTopology(TestCase):
    def setUp(self):
        self.t = Topology.instance()

    def tearDown(self):
        del Topology._instance

    def test_resources_type(self):
        self.assertIsNone(self.t.resourcesType)
        self.t.setLocalResourcesType()
        self.assertEqual(self.t.resourcesType, 'local')
        self.t.setCloudResourcesType()
        self.assertEqual(self.t.resourcesType, 'cloud')

    def test_resources_type_dumped(self):
        self.t.setCloudResourcesType()
        topology = self.t.dump()
        self.assertIn('resources_type', topology)
        self.assertEqual(topology['resources_type'], 'cloud')

    def test_resources_type_load(self):
        self.assertIsNone(self.t.resourcesType)
        topology = {
            'resources_type': 'cloud',
            'type': 'topology',
            'topology': {},
        }
        self.t.load(topology)
        self.assertEqual(self.t.resourcesType, 'cloud')

    def test_reset(self):
        self.t._links = ['foo', 'baz', 'bar']
        self.t._nodes = ['foo', 'baz', 'bar']
        self.t._initialized_nodes = ['foo', 'baz', 'bar']
        self.t.setCloudResourcesType()

        self.t.reset()

        self.assertEqual(len(self.t._links), 0)
        self.assertEqual(len(self.t._nodes), 0)
        self.assertEqual(len(self.t._initialized_nodes), 0)
        self.assertIsNone(self.t._resources_type)
