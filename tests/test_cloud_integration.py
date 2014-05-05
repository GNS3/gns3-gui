"""
Integration tests for RackspaceCtrl.

WARNING: These tests start up real instances in the Rackspace Cloud.

"""

from gns3.cloud.rackspace_ctrl import RackspaceCtrl
import unittest


class StubNodeObject(object):

    def __init__(self, **kwargs):

        for arg in kwargs:
            setattr(self, arg, kwargs[arg])


class TestRackspaceCtrl(unittest.TestCase):

    def setUp(self):
        self.username = username
        self.api_key = api_key
        self.ctrl = RackspaceCtrl(self.username, self.api_key)
        self.ctrl.authenticate()

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

    def test_delete_instance(self):
        """ Test deleting an instance. """

        self.ctrl.set_region('ord')

        # TODO: create an instance first, and get its ID

        #self.ctrl.delete_instance('invalid_instance_id')

    def test_deleted_invalid_instance_id(self):

        self.ctrl.set_region('ord')

        fake_instance = StubNodeObject(id='invalid_id')

        self.assertRaises(LookupError, self.ctrl.delete_instance,
                          fake_instance)

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

        self.ctrl.set_region('ord')

        instances = self.ctrl.list_instances()

        self.assertIsInstance(instances, list)

    def test_token_parsed(self):
        """ Ensure that the token is set. """

        self.assertIsNotNone(self.ctrl.token)

    def test_set_region(self):
        """ Ensure that set_region sets 'region' and 'driver'. """

        result = self.ctrl.set_region('iad')

        self.assertEqual(result, True)
        self.assertEqual(self.ctrl.region, 'iad')
        self.assertIsNotNone(self.ctrl.driver)

    def test_set_invalid_region(self):
        """ Ensure that calling 'set_region' with an invalid param fails. """

        result = self.ctrl.set_region('invalid')

        self.assertEqual(result, False)
        self.assertIsNone(self.ctrl.region)
        self.assertIsNone(self.ctrl.driver)


if __name__ == '__main__':
    username = 'kieronbulloch'
    api_key = '2d907b75752b4650b230469213d97cd3'
    #username = input('Enter username: ')
    #api_key = input('Enter api key: ')
    unittest.main()
