from gns3.cloud import RackspaceCtrl
import unittest


class TestRackspaceCtrl(unittest.TestCase):

    def setUp(self):
        self.ctrl = RackspaceCtrl('username', 'api_key')

    def test_authenticate_valid_user(self):
        """ Test authentication with a valid user and api key. """

        auth_result = self.ctrl.authenticate()
        self.assertEqual(auth_result, True)
        self.assertIsNotNone(self.ctrl.token)


if __name__ == '__main__':
    unittest.main()
