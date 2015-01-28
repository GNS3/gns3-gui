import os
import json
import unittest
from unittest import mock
import hashlib
import tempfile

from gns3.cloud.rackspace_ctrl import RackspaceCtrl
from gns3.cloud.exceptions import OverLimit, BadRequest, ServiceUnavailable
from gns3.cloud.exceptions import Unauthorized, ApiError, KeyPairExists
from gns3.cloud.exceptions import ItemNotFound


RACKSPACE_VALID_CREDENTIALS_RESPONSE = {
    "access": {
        "token": {
            "id": "abcdefgh0123456789",
            "expires": "2014-04-29T11:51:38.470Z",
            "tenant": {
                "id": "000001",
                "name": "000001"
            },
            "RAX-AUTH:authenticatedBy": [
                "APIKEY"
            ]
        },
        "serviceCatalog": [
            {
                "name": "cloudServersOpenStack",
                "endpoints": [
                    {
                        "region": "IAD",
                        "tenantId": "000001",
                        "publicURL": "https://iad.servers.api.rackspacecloud.com/v2/000001",
                        "versionInfo": "https://iad.servers.api.rackspacecloud.com/v2",
                        "versionList": "https://iad.servers.api.rackspacecloud.com/",
                        "versionId": "2"
                    },
                    {
                        "region": "DFW",
                        "tenantId": "000001",
                        "publicURL": "https://dfw.servers.api.rackspacecloud.com/v2/000001",
                        "versionInfo": "https://dfw.servers.api.rackspacecloud.com/v2",
                        "versionList": "https://dfw.servers.api.rackspacecloud.com/",
                        "versionId": "2"
                    },
                    {
                        "region": "SYD",
                        "tenantId": "000001",
                        "publicURL": "https://syd.servers.api.rackspacecloud.com/v2/000001",
                        "versionInfo": "https://syd.servers.api.rackspacecloud.com/v2",
                        "versionList": "https://syd.servers.api.rackspacecloud.com/",
                        "versionId": "2"
                    },
                    {
                        "region": "ORD",
                        "tenantId": "000001",
                        "publicURL": "https://ord.servers.api.rackspacecloud.com/v2/000001",
                        "versionInfo": "https://ord.servers.api.rackspacecloud.com/v2",
                        "versionList": "https://ord.servers.api.rackspacecloud.com/",
                        "versionId": "2"
                    }
                ],
                "type": "compute"
            }
        ]
    }
}

RACKSPACE_INVALID_CREDENTIALS_RESPONSE = {
    "unauthorized": {
        "code": 401,
        "message": "Username or api key is invalid."
    }
}

RACKSPACE_BAD_REQUEST_RESPONSE = {
    "badRequest": {
        "code": 400,
        "message": "Invalid json request body"
    }
}


class MockApiResponse(object):

    """ Emulate a requests.Response object. """

    class Connection(object):

        def close(self):
            pass

    def __init__(self, status_code, response_text):
        self.status_code = status_code
        self.text = response_text
        self.connection = MockApiResponse.Connection()

    def json(self):
        """ Return self.text. """

        return self.text


def stub_rackspace_identity_post(identity_ep, data=None, headers=None):
    """ Fake the responses of the Rackspace Identity service. """

    r_data = json.loads(data)

    try:
        credentials = r_data['auth']['RAX-KSKEY:apiKeyCredentials']
        username = credentials['username']
        api_key = credentials['apiKey']

    except KeyError:
        status_code = 400
        response_text = RACKSPACE_BAD_REQUEST_RESPONSE

    if username == 'valid_user' and api_key == 'valid_api_key':
        status_code = 200
        response_text = RACKSPACE_VALID_CREDENTIALS_RESPONSE

    else:
        status_code = 401
        response_text = RACKSPACE_INVALID_CREDENTIALS_RESPONSE

    return MockApiResponse(status_code, response_text)


class MockLibCloudDriver(object):

    def __init__(self, username, api_key, region):
        pass

    def create_node(self, name, size, image, auth, *args, **kwargs):

        if name == 'bad_request':
            raise Exception("400 Bad request")

        elif name == 'over_limit':
            raise Exception("413 Over Limit")

        elif name == 'service_unavailable':
            raise Exception("503 Service Unavailable")

        elif name == 'unauthorized':
            raise Exception("401 Unauthorized")

        elif name == 'api_error':
            raise Exception("500 Compute Error")

        return True

    def destroy_node(self, node):

        if node.name == 'nonexistant':
            raise Exception("404 Instance not found")

    def create_key_pair(self, name):

        if name == 'duplicate_name':
            raise Exception("409 Key Pair exists.")

        return True

    def list_images(self, *args, **kwargs):
        return []

    def ex_get_size(self, *args, **kwargs):
        return ''


class MockStorageObject(object):

    def __init__(self, name, data=None):
        self.name = name
        self.stream = [data].__iter__() if data else None

    def as_stream(self):
        return self.stream


class TestRackspaceCtrl(unittest.TestCase):

    def setUp(self):
        """ Set up the objects used by most of the tests. """

        self.ctrl = RackspaceCtrl('valid_user', 'valid_api_key', 'http://foo.bar:8888')
        self.ctrl.post_fn = stub_rackspace_identity_post
        self.driver_cls = MockLibCloudDriver

    def test_authenticate_valid_user(self):
        """ Test authentication with a valid user and api key. """

        auth_result = self.ctrl.authenticate()
        self.assertEqual(auth_result, True)
        self.assertIsNotNone(self.ctrl.token)

    def test_authenticate_empty_user(self):
        """ Ensure authentication with empty string as username fails. """

        ctrl = RackspaceCtrl('', 'valid_api_key', 'http://foo.bar:8888')
        ctrl.post_fn = stub_rackspace_identity_post

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_authenticate_empty_apikey(self):
        """ Ensure authentication with empty string as api_key fails. """

        ctrl = RackspaceCtrl('valid_user', '', 'http://foo.bar:8888')
        ctrl.post_fn = stub_rackspace_identity_post

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_authenticate_invalid_user(self):
        """  Ensure authentication with invalid user credentials fails. """

        ctrl = RackspaceCtrl('invalid_user', 'invalid_api_key', 'http://foo.bar:8888')
        ctrl.post_fn = stub_rackspace_identity_post

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_list_regions(self):
        """ Ensure that list_regions returns the correct result. """

        self.ctrl.authenticate()
        regions = self.ctrl.list_regions()

        expected_regions = [
            {'IAD': 'iad'},
            {'DFW': 'dfw'},
            {'SYD': 'syd'},
            {'ORD': 'ord'}
        ]

        self.assertCountEqual(regions, expected_regions)

    def test_set_region(self):
        """ Ensure that set_region sets 'region' and 'driver'. """

        self.ctrl.authenticate()

        result = self.ctrl.set_region('iad')

        self.assertEqual(result, True)
        self.assertEqual(self.ctrl.region, 'iad')
        self.assertIsNotNone(self.ctrl.driver)

    def test_set_invalid_region(self):
        """ Ensure that calling 'set_region' with an invalid param fails. """

        self.ctrl.authenticate()

        result = self.ctrl.set_region('invalid')

        self.assertEqual(result, False)
        self.assertIsNone(self.ctrl.region)
        self.assertIsNone(self.ctrl.driver)

    def test_token_parsed(self):
        """ Ensure that the token is set. """

        ctrl = RackspaceCtrl('valid_user', 'valid_api_key', 'http://foo.bar:8888')
        ctrl.post_fn = stub_rackspace_identity_post

        ctrl.authenticate()

        self.assertEqual('abcdefgh0123456789', ctrl.token)

    def test_upload_file(self):
        self.ctrl.storage_driver = mock.MagicMock()
        mock_container = mock.MagicMock()
        mock_container.list_objects = mock.MagicMock(return_value=[])
        self.ctrl.storage_driver.create_container = mock.MagicMock(return_value=mock_container)
        test_data = b'abcdef'
        test_data_hash = hashlib.md5(test_data).hexdigest()

        test_file = tempfile.NamedTemporaryFile()
        with test_file.file as f:
            f.write(test_data)

        return_value = self.ctrl.upload_file(test_file.name, 'test_folder/test.txt')

        upload_file_args = self.ctrl.storage_driver.upload_object_via_stream.call_args_list[0]
        upload_hash_args = self.ctrl.storage_driver.upload_object_via_stream.call_args_list[1]

        self.assertEqual(upload_file_args[0][2], 'test_folder/test.txt')
        self.assertEqual(upload_hash_args[0][2], 'test_folder/test.txt.md5')
        self.assertEqual(upload_file_args[0][0].name, test_file.name)
        self.assertEqual(upload_hash_args[0][0].read(), test_data_hash)
        self.assertEqual(return_value, True)

    def test_upload_file__exists(self):
        test_data = b'abcdef'
        test_data_hash = hashlib.md5(test_data).hexdigest()

        test_file = tempfile.NamedTemporaryFile()
        with test_file.file as f:
            f.write(test_data)

        self.ctrl.storage_driver = mock.MagicMock()
        mock_container = mock.MagicMock()
        mock_container.list_objects = mock.MagicMock(return_value=[
            MockStorageObject('test_folder/test.txt'),
            MockStorageObject('test_folder/test.txt.md5')
        ])
        self.ctrl.storage_driver.create_container = mock.MagicMock(return_value=mock_container)

        mock_container.get_object = mock.MagicMock(
            return_value=MockStorageObject('', bytes(test_data_hash, 'utf8')))

        return_value = self.ctrl.upload_file(test_file.name, 'test_folder/test.txt')

        self.assertFalse(self.ctrl.storage_driver.upload_object_via_stream.called)
        self.assertEqual(return_value, False)

    def test_download_file__exists__same_hash(self):
        test_data = b'abcdefghi'
        test_data_hash = hashlib.md5(test_data).hexdigest()
        test_file = tempfile.NamedTemporaryFile()
        with test_file.file as f:
            f.write(test_data)

        self.ctrl.storage_driver = mock.MagicMock()
        mock_container = mock.MagicMock()
        self.ctrl.storage_driver.get_container = mock.MagicMock(return_value=mock_container)

        file_object = MockStorageObject('test_file.txt')
        file_object.download = mock.MagicMock()
        file_hash_object = MockStorageObject('test_file.txt', bytes(test_data_hash, 'utf8'))

        mock_container.get_object = lambda name: {
            'test_file.txt': file_object,
            'test_file.txt.md5': file_hash_object
        }[name]

        self.ctrl.download_file('test_file.txt', test_file.name)

        self.assertFalse(file_object.download.called)

    def test_download_file__exists__different_hash(self):
        test_data = b'abcdefghij'
        test_data_hash = 'some_garbage_hash'
        test_file = tempfile.NamedTemporaryFile()
        with test_file.file as f:
            f.write(test_data)

        self.ctrl.storage_driver = mock.MagicMock()
        mock_container = mock.MagicMock()
        self.ctrl.storage_driver.get_container = mock.MagicMock(return_value=mock_container)

        file_object = MockStorageObject('test_file.txt')
        file_object.download = mock.MagicMock()
        file_hash_object = MockStorageObject('test_file.txt', bytes(test_data_hash, 'utf8'))

        mock_container.get_object = lambda name: {
            'test_file.txt': file_object,
            'test_file.txt.md5': file_hash_object
        }[name]

        self.ctrl.download_file('test_file.txt', test_file.name)

        file_object.download.assert_called_once_with(test_file.name)

    def test_find_storage_image_names(self):
        self.ctrl.storage_driver = mock.MagicMock()
        mock_container = mock.MagicMock()
        self.ctrl.storage_driver.get_container = mock.MagicMock(return_value=mock_container)
        mock_container.list_objects = mock.MagicMock(return_value=[
            MockStorageObject('images/IOS/test_image_1.image'),
            MockStorageObject('images/IOS/test_image_1.image.md5'),
            MockStorageObject('images/IOS/test_image_2.img'),
            MockStorageObject('images/IOS/test_image_2.img.md5'),
            MockStorageObject('images/IOS/test_image_3.img'),
            MockStorageObject('projects/project1.zip'),
            MockStorageObject('test_image_1.image')
        ])

        image_names = self.ctrl.find_storage_image_names(['test_image_1.image', 'test_image_2.img'])

        self.assertDictEqual(image_names, {
            'test_image_1.image': 'images/IOS/test_image_1.image',
            'test_image_2.img': 'images/IOS/test_image_2.img'
        })

    def test_find_storage_image_names__missing(self):
        self.ctrl.storage_driver = mock.MagicMock()
        mock_container = mock.MagicMock()
        self.ctrl.storage_driver.get_container = mock.MagicMock(return_value=mock_container)
        mock_container.list_objects = mock.MagicMock(return_value=[
            MockStorageObject('images/IOS/test_image_1.image'),
            MockStorageObject('images/IOS/test_image_1.image.md5'),
            MockStorageObject('images/IOS/test_image_2.img.md5'),
            MockStorageObject('projects/project1.zip'),
            MockStorageObject('test_image_1.image')
        ])

        self.assertRaises(Exception, self.ctrl.find_storage_image_names, ['test_image_1.image', 'test_image_2.img'])


class TestRackspaceCtrlDriver(unittest.TestCase):

    """ Test the libcloud Rackspace driver. """

    class StubObject(object):

        def __init__(self, **kwargs):

            for arg in kwargs:
                setattr(self, arg, kwargs[arg])

    def setUp(self):
        """ Set up the objects used by most of the tests. """

        self.ctrl = RackspaceCtrl('valid_user', 'valid_api_key', 'http://foo.bar:8888')
        self.ctrl.post_fn = stub_rackspace_identity_post
        self.ctrl.driver_cls = MockLibCloudDriver
        self.ctrl.authenticate()
        self.ctrl.set_region('iad')
        self.ctrl.get_image = mock.MagicMock()
        self.ctrl.get_image.return_value = ''
        self.key_pair = TestRackspaceCtrlDriver.StubObject(public_key='keystr')

    def test_create_instance_over_limit(self):
        """ Ensure '413 Over Limit' error is handled properly. """

        self.assertRaises(OverLimit, self.ctrl.create_instance,
                          'over_limit', 'size', 'image', self.key_pair)

    def test_create_instance_bad_request(self):
        """ Ensure '400 Bad Request' error is handled properly. """

        self.assertRaises(BadRequest, self.ctrl.create_instance,
                          'bad_request', 'size', 'image', self.key_pair)

    def test_delete_instance_nonexistant(self):
        """ Ensure '404 Instance not found' error is handled properly. """

        instance = TestRackspaceCtrlDriver.StubObject(name='nonexistant')

        self.assertRaises(ItemNotFound, self.ctrl.delete_instance,
                          instance)

    def test_create_key_pair_duplicate_name(self):
        """ Ensure '409 Key Pair exists' error is handled properly. """

        self.assertRaises(KeyPairExists, self.ctrl.create_key_pair,
                          'duplicate_name')

    def test_service_uavailable(self):
        """ Ensure '503 Service Unavailable' error is handled properly. """

        self.assertRaises(ServiceUnavailable, self.ctrl.create_instance,
                          'service_unavailable', 'size', 'image',
                          self.key_pair)

    def test_unauthorized(self):
        """ Ensure '401 Unauthroized' error is handled properly. """

        self.assertRaises(Unauthorized, self.ctrl.create_instance,
                          'unauthorized', 'size', 'image', self.key_pair)

    def test_api_error(self):
        """ Ensure '500 ...' error is handled properly. """

        self.assertRaises(ApiError, self.ctrl.create_instance, 'api_error',
                          'size', 'image', self.key_pair)

    def test_list_images(self):
        self.ctrl.tenant_id = '1234567890'
        self.ctrl._get_shared_images = mock.MagicMock()
        self.ctrl._get_shared_images.return_value = [
            {
                "image_name": "foo",
                "schema": "/v2/schemas/member",
                "status": "pending",
                "image_id": "1c6ba38d-5960-4cc1-a3db-bab521e99afa",
                "member_id": "user_foo",
                "created_at": "2014-06-25T13:49:56Z",
                "updated_at": "2014-06-25T13:49:56Z"
            },
            {
                "image_name": "foo2",
                "schema": "/v2/schemas/member",
                "status": "pending",
                "image_id": "a44a6c31-a437-498e-b4e4-3a6cb9d1d733",
                "member_id": "user_foo",
                "created_at": "2014-06-25T13:49:59Z",
                "updated_at": "2014-06-25T13:49:59Z"
            },
            {
                "image_name": "foo3",
                "member_id": "user_foo",
                "image_id": "64c3b6e5-05c1-4407-82b9-5690cdfaa887",
                "status": "ALREADYREQUESTED"
            },
            {
                "image_name": "foo4",
                "member_id": "user_foo",
                "image_id": "a6893756-b108-4667-9bf3-7a02d076b3e2",
                "status": "ALREADYREQUESTED"
            }
        ]
        images = self.ctrl.list_images()
        self.assertEqual({'foo', 'foo2', 'foo3', 'foo4'}, set(images.values()))


if __name__ == '__main__':
    unittest.main()
