# -*- coding: utf-8 -*-
from unittest import TestCase

from gns3.topology import Topology
from gns3.main_window import MainWindow


class TestTopology(TestCase):
    def setUp(self):
        self.t = Topology.instance()

    def tearDown(self):
        self.t.reset()

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

    def test_instances(self):
        self.assertEqual(self.t._instances, [])
        self.t.addInstance(name="My instance", id="xyz", size_id="123", image_id="1234567890")
        self.assertEqual(len(self.t._instances), 1)
        self.t.removeInstance("My fake instance")
        self.assertEqual(len(self.t._instances), 1)
        self.t.removeInstance("My instance")
        self.assertEqual(self.t._instances, [])

    def test_instances_dumped(self):
        test_settings = {'project_type': 'cloud'}
        MainWindow.instance() ._project_settings.update(test_settings)
        self.t.addInstance(name="My instance", id="xyz", size_id="123", image_id="1234567890")
        topology = self.t.dump()
        self.assertIn('instances', topology["topology"])
        instances = topology["topology"]["instances"]
        self.assertEqual(len(instances), 1)
        self.assertEqual(instances.pop()["name"], "My instance")

    def test_instaces_load(self):
        topology = {
            'project_type': 'cloud',
            'type': 'topology',
            'version': '3.0',
            'topology': {
                'instances': [
                    {
                        'name': 'Foo Instance',
                        'id': 'xyz',
                        'size_id': 'id1',
                        'image_id': 'id2',
                    },
                    {
                        'name': 'Another Foo Instance',
                        'id': 'xyz',
                        'size_id': 'id123',
                        'image_id': 'id234',
                    }
                ]
            }
        }
        self.t.load(topology)
        instances = self.t.instances()
        self.assertEqual(len(instances), 2)
        self.assertEqual(instances[0].name, 'Foo Instance')
        self.assertEqual(instances[1].name, 'Another Foo Instance')
