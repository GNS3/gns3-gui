"""
Integration tests for RackspaceCtrl.

WARNING: These tests start up real instances in the Rackspace Cloud.


Usage:

    You need pytest to run this testsuite, the runner accepts following options:
        --username <username>: Rackspace username
        --apikey <key>: Rackspace apikey
        --run-instances: flag to specify whether tests have to wait for instances to run (very slow)

    If you don't specify username and apikey at the command line, the runner will try to access
    RACKSPACE_USERNAME and RACKSPACE_APIKEY environment vars. If neither the command line options
    nor the env vars are set, this testsuite will be skipped.

"""

import unittest
import time
import hashlib
import tempfile
import os

from libcloud.compute.base import Node, NodeSize, KeyPair
import pytest

from gns3.cloud.rackspace_ctrl import RackspaceCtrl
from gns3.cloud.exceptions import ItemNotFound, KeyPairExists
from io import StringIO




# custom flag to skip tests if rackspace credentials was not provided
rackspace_authentication = pytest.mark.rackspace_authentication


class StubObject(object):

    def __init__(self, **kwargs):

        for arg in kwargs:
            setattr(self, arg, kwargs[arg])


@rackspace_authentication
@pytest.mark.usefixtures("username", "api_key", "run_instances")
class TestRackspaceCtrl(unittest.TestCase):
    def setUp(self):
        # prefix to identify created objects
        self.object_prefix = "int_test_"
        self.prefix_length = len(self.object_prefix)
        self.ctrl = RackspaceCtrl(self.username, self.api_key, 'http://foo.bar:8888')
        self.ctrl.authenticate()
        self.ctrl.set_region('ord')
        self.gns3_image = None

        self.ctrl.GNS3_CONTAINER_NAME = 'TEST_GNS3'

    def tearDown(self):
        self._remove_instances()
        self._remove_key_pairs()
        if self.gns3_image is not None:
            self.ctrl.driver.ex_delete_image(self.gns3_image)

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

        ctrl = RackspaceCtrl(self.username, self.api_key, 'http://foo.bar:8888')

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, True)
        self.assertIsNotNone(ctrl.token)

    def test_authenticate_empty_user(self):
        """ Ensure authentication with empty string as username fails. """

        ctrl = RackspaceCtrl('', self.api_key, 'http://foo.bar:8888')

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_authenticate_empty_apikey(self):
        """ Ensure authentication with empty string as api_key fails. """

        ctrl = RackspaceCtrl(self.username, '', 'http://foo.bar:8888')

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_authenticate_invalid_user(self):
        """  Ensure authentication with invalid user credentials fails. """

        ctrl = RackspaceCtrl('invalid_user', 'invalid_api_key', 'http://foo.bar:8888')

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_set_region(self):
        """ Ensure that set_region sets 'region' and 'driver'. """

        ctrl = RackspaceCtrl(self.username, self.api_key, 'http://foo.bar:8888')
        ctrl.authenticate()

        result = ctrl.set_region('iad')

        self.assertEqual(result, True)
        self.assertEqual(ctrl.region, 'iad')
        self.assertIsNotNone(ctrl.driver)

    def test_set_invalid_region(self):
        """ Ensure that calling 'set_region' with an invalid param fails. """

        ctrl = RackspaceCtrl(self.username, self.api_key, 'http://foo.bar:8888')
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
        if self.run_instances:
            self.ctrl.driver.wait_until_running([instance])
        self.assertIsInstance(instance, Node)

    def test_delete_instance(self):
        """ Test deleting an instance. """

        name = "%sdelete_instances" % self.object_prefix

        image = self.ctrl.driver.list_images()[0]
        size = self.ctrl.driver.list_sizes()[0]
        key_pair = self.ctrl.create_key_pair(name)

        instance = self.ctrl.create_instance(name, size, image, key_pair)
        if self.run_instances:
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
        if self.run_instances:
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

    def test__get_shared_image_not_found(self):
        self.assertRaises(ItemNotFound, self.ctrl._get_shared_images, 'user_foo', 'IAD', 'foo_ver')

    def test__get_shared_image(self):
        name = "%s_get_shared_image" % self.object_prefix
        images = self.ctrl.driver.list_images()
        # use the smallest image available on Rackspace
        image = [i for i in images if 'boot.rackspace.com' in i.name][0]
        size = self.ctrl.driver.list_sizes()[0]
        key_pair = self.ctrl.create_key_pair(name)

        print("Creating an instance...")
        instance = self.ctrl.create_instance(name, size, image, key_pair)

        # we cannot create images until the build is over
        self.ctrl.driver.wait_until_running([instance])
        print("Instance up and running.")


        print("Creating an image...")
        gns3_image1 = self.ctrl.driver.ex_save_image(instance, 'gns3_3.0a', metadata=None)
        # wait until image is active or gns3-ias will ignore it
        while self.ctrl.driver.ex_get_image(gns3_image1.id).extra['status'] != 'ACTIVE':
            time.sleep(2)
        print("Image created.")

        # wait to avoid Exception: 409 Conflict Cannot 'createImage' while instance is in task_state image_uploading
        self.ctrl.driver.wait_until_running([instance])

        print("Creating another image...")
        gns3_image2 = self.ctrl.driver.ex_save_image(instance, 'gns3_3.0b', metadata=None)
        # wait until image is active or gns3-ias will ignore it
        while self.ctrl.driver.ex_get_image(gns3_image2.id).extra['status'] != 'ACTIVE':
            time.sleep(2)
        print("Image created.")

        print("Getting shared images...")
        r_images = self.ctrl._get_shared_images('user_foo', 'ORD', '3.0')

        self.assertTrue('image_id' in r_images[0])
        self.assertTrue('image_id' in r_images[1])
        self.assertTrue('member_id' in r_images[0])
        self.assertTrue('member_id' in r_images[1])
        self.assertTrue('status' in r_images[0])
        self.assertTrue('status' in r_images[1])
        self.assertEqual(r_images[0]['status'], 'pending')
        self.assertEqual(r_images[1]['status'], 'pending')
        print("Done.")

        print("Getting shared images...")
        r_images2 = self.ctrl._get_shared_images('user_foo', 'ORD', '3.0')

        self.assertTrue('image_id' in r_images2[0])
        self.assertTrue('image_id' in r_images2[1])
        self.assertEqual(r_images[0]['image_id'], r_images2[0]['image_id'])
        self.assertEqual(r_images[1]['image_id'], r_images2[1]['image_id'])
        self.assertTrue('member_id' in r_images2[0])
        self.assertTrue('member_id' in r_images2[1])
        self.assertEqual(r_images[0]['member_id'], r_images2[0]['member_id'])
        self.assertEqual(r_images[1]['member_id'], r_images2[1]['member_id'])
        self.assertTrue('status' in r_images2[0])
        self.assertTrue('status' in r_images2[1])
        self.assertEqual(r_images2[0]['status'], 'ALREADYREQUESTED')
        self.assertEqual(r_images2[1]['status'], 'ALREADYREQUESTED')
        print("Done.")

    def test_upload_file(self):
        test_data = 'abcdefg'
        test_file = tempfile.NamedTemporaryFile(mode='w')
        with test_file.file as f:
            f.write(test_data)

        return_value = self.ctrl.upload_file(test_file.name, 'test_folder')

        container = self.ctrl.storage_driver.get_container(self.ctrl.GNS3_CONTAINER_NAME)
        file_object = container.get_object('test_folder/' + os.path.basename(test_file.name))
        hash_object = container.get_object('test_folder/' + os.path.basename(test_file.name) + '.md5')

        cloud_file_hash = ''
        for chunk in hash_object.as_stream():
            cloud_file_hash += chunk.decode('utf8')

        cloud_file_contents = ''
        for chunk in file_object.as_stream():
            cloud_file_contents += chunk.decode('utf8')

        self.assertEqual(cloud_file_hash, hashlib.md5(test_data.encode('utf8')).hexdigest())
        self.assertEqual(cloud_file_contents, test_data)
        self.assertEqual(return_value, True)

        for o in container.iterate_objects():
            o.delete()

        container.delete()

    def test_list_projects(self):
        container = self.ctrl.storage_driver.create_container(self.ctrl.GNS3_CONTAINER_NAME)

        container.upload_object_via_stream(StringIO('abcd'), 'projects/project1.gns3.zip')
        container.upload_object_via_stream(StringIO('abcd'), 'projects/project1.gns3.zip.md5')
        container.upload_object_via_stream(StringIO('abcd'), 'projects/project2.gns3.zip')
        container.upload_object_via_stream(StringIO('abcd'), 'some_file.txt')
        container.upload_object_via_stream(StringIO('abcd'), 'some_file2.zip')

        projects = self.ctrl.list_projects()

        self.assertEqual(len(projects), 2)
        self.assertTrue(('project1.gns3', 'projects/project1.gns3.zip') in projects)
        self.assertTrue(('project2.gns3', 'projects/project2.gns3.zip') in projects)

        for o in container.iterate_objects():
            o.delete()

        container.delete()
