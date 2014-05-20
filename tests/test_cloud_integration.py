"""
Integration tests for RackspaceCtrl.

WARNING: These tests start up real instances in the Rackspace Cloud.

"""

from gns3.cloud.rackspace_ctrl import RackspaceCtrl
from gns3.cloud.exceptions import ItemNotFound, KeyPairExists
from libcloud.compute.base import Node, NodeSize, KeyPair
import pytest
import os
import pytest
import unittest


class StubObject(object):

    def __init__(self, **kwargs):

        for arg in kwargs:
            setattr(self, arg, kwargs[arg])


@pytest.mark.skipif(True, reason="temporarily disable rackspace integration test")
class TestRackspaceCtrl(unittest.TestCase):

    def setUp(self):
        self.username = username
        self.api_key = api_key
        # prefix to identify created objects
        self.object_prefix = "int_test_"
        self.prefix_length = len(self.object_prefix)
        self.ctrl = RackspaceCtrl(self.username, self.api_key)
        self.ctrl.authenticate()
        self.ctrl.set_region('ord')

    def tearDown(self):
        self._remove_instances()
        self._remove_key_pairs()

    def _remove_instances(self):
        """ Remove any instances that were created. """

        for instance in self.ctrl.driver.list_nodes():
            if instance.name[0:self.prefix_length] == self.object_prefix:
                self.ctrl.driver.destroy_node(instance)

    def _remove_key_pairs(self):
        """ Remove any key pairs that were created. """

        for key_pair in self.ctrl.driver.list_key_pairs():
            if key_pair.name[0:self.prefix_length] == self.object_prefix:
                self.ctrl.driver.delete_key_pair(key_pair)

    def test_authenticate_valid_user(self):
        """ Test authentication with a valid user and api key. """

        ctrl = RackspaceCtrl(self.username, self.api_key)

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, True)
        self.assertIsNotNone(ctrl.token)

    def test_authenticate_empty_user(self):
        """ Ensure authentication with empty string as username fails. """

        ctrl = RackspaceCtrl('', self.api_key)

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_authenticate_empty_apikey(self):
        """ Ensure authentication with empty string as api_key fails. """

        ctrl = RackspaceCtrl(self.username, '')

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_authenticate_invalid_user(self):
        """  Ensure authentication with invalid user credentials fails. """

        ctrl = RackspaceCtrl('invalid_user', 'invalid_api_key')

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_set_region(self):
        """ Ensure that set_region sets 'region' and 'driver'. """

        ctrl = RackspaceCtrl(self.username, self.api_key)
        ctrl.authenticate()

        result = ctrl.set_region('iad')

        self.assertEqual(result, True)
        self.assertEqual(ctrl.region, 'iad')
        self.assertIsNotNone(ctrl.driver)

    def test_set_invalid_region(self):
        """ Ensure that calling 'set_region' with an invalid param fails. """

        ctrl = RackspaceCtrl(self.username, self.api_key)
        ctrl.authenticate()

        result = self.ctrl.set_region('invalid')

        self.assertEqual(result, False)
        self.assertIsNone(ctrl.region)
        self.assertIsNone(ctrl.driver)

    def test_create_instance(self):
        """ Test creating an instance. """

        name = "%screate_instance" % self.object_prefix

        image = self.ctrl.driver.list_images()[0]
        size = self.ctrl.driver.list_sizes()[0]
        key_pair = self.ctrl.create_key_pair(name)

        instance = self.ctrl.create_instance(name, size, image, key_pair)
        self.ctrl.driver.wait_until_running([instance])
        self.assertIsInstance(instance, Node)

    def test_delete_instance(self):
        """ Test deleting an instance. """

        name = "%sdelete_instances" % self.object_prefix

        image = self.ctrl.driver.list_images()[0]
        size = self.ctrl.driver.list_sizes()[0]
        key_pair = self.ctrl.create_key_pair(name)

        instance = self.ctrl.create_instance(name, size, image, key_pair)
        self.ctrl.driver.wait_until_running([instance])

        response = self.ctrl.delete_instance(instance)

        self.assertEqual(response, True)

    def test_delete_invalid_instance_id(self):

        fake_instance = StubObject(id='invalid_id')

        self.assertRaises(ItemNotFound, self.ctrl.delete_instance,
                          fake_instance)

    def test_create_key_pair(self):
        """ Test creating a key pair. """

        name = "%screate_key_pair" % self.object_prefix
        key_pair = self.ctrl.create_key_pair(name)

        self.assertIsInstance(key_pair, KeyPair)

        response = self.ctrl.delete_key_pair(key_pair)

        self.assertEqual(response, True)

    def test_create_key_pair_existing_name(self):
        """ Test creating a key pair with an existing name. """

        name = "%screate_key_pair_existing_name" % self.object_prefix
        # Create the first instance
        self.ctrl.create_key_pair(name)

        self.assertRaises(KeyPairExists, self.ctrl.create_key_pair, name)

    def test_delete_key_pair(self):
        """ Test deleting a key pair. """

        name = "%sdelete_key_pair" % self.object_prefix

        key_pair = self.ctrl.create_key_pair(name)

        result = self.ctrl.delete_key_pair(key_pair)

        self.assertEqual(result, True)

    def test_delete_nonexistant_key_pair(self):
        """ Test deleting a key pair that doesn't exist. """

        fake_key_pair = StubObject(name='invalid_name')

        self.assertRaises(ItemNotFound, self.ctrl.delete_key_pair,
                          fake_key_pair)

    def test_list_regions(self):
        """ Ensure that list_regions returns the correct result. """

        regions = self.ctrl.list_regions()

        expected_regions = [
            {'IAD': 'iad'},
            {'DFW': 'dfw'},
            {'SYD': 'syd'},
            {'ORD': 'ord'},
            {'HKG': 'hkg'}
        ]

        self.assertCountEqual(regions, expected_regions)

    def test_list_instances(self):

        name = "%slist_instances" % self.object_prefix

        image = self.ctrl.driver.list_images()[0]
        size = self.ctrl.driver.list_sizes()[0]
        key_pair = self.ctrl.create_key_pair(name)

        instance = self.ctrl.create_instance(name, size, image, key_pair)
        self.ctrl.driver.wait_until_running([instance])

        instances = self.ctrl.list_instances()

        self.assertIsInstance(instances, list)
        self.assertIsInstance(instances[0], Node)

    def test_list_sizes(self):

        sizes = self.ctrl.list_sizes()

        self.assertIsInstance(sizes, list)
        self.assertIsInstance(sizes[0], NodeSize)

    def test_token_parsed(self):
        """ Ensure that the token is set. """

        self.assertIsNotNone(self.ctrl.token)


if __name__ == '__main__':

    if 'RACKSPACE_USERNAME' in os.environ:
        username = os.environ.get('RACKSPACE_USERNAME')
    else:
        username = input('Enter Rackspace username: ')

    if 'RACKSPACE_APIKEY' in os.environ:
        api_key = os.environ.get('RACKSPACE_APIKEY')
    else:
        api_key = input('Enter Rackspace api key: ')

    unittest.main()
