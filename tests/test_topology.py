# -*- coding: utf-8 -*-
from unittest import TestCase

from gns3.topology import Topology


class TestTopology(TestCase):
    def setUp(self):
        self.t = Topology.instance()

    def tearDown(self):
        del Topology._instance

    def test_resources_type(self):
        self.t.resourcesType = 'foo'
        self.assertIsNone(self.t.resourcesType)
        self.t.resourcesType = 'local'
        self.assertEqual(self.t.resourcesType, 'local')
        self.t.resourcesType = 'cloud'
        self.assertEqual(self.t.resourcesType, 'cloud')

    def test_resources_type_dumped(self):
        self.t.resourcesType = 'cloud'
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
