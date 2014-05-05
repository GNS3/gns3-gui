from gns3.cloud.rackspace_ctrl import RackspaceCtrl
import json
import unittest

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


class TestRackspaceCtrl(unittest.TestCase):

    def test_authenticate_valid_user(self):
        """ Test authentication with a valid user and api key. """

        ctrl = RackspaceCtrl('valid_user', 'valid_api_key')
        ctrl.post_fn = stub_rackspace_identity_post

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, True)
        self.assertIsNotNone(ctrl.token)

    def test_authenticate_empty_user(self):
        """ Ensure authentication with empty string as username fails. """

        ctrl = RackspaceCtrl('', 'valid_api_key')
        ctrl.post_fn = stub_rackspace_identity_post

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_authenticate_empty_apikey(self):
        """ Ensure authentication with empty string as api_key fails. """

        ctrl = RackspaceCtrl('valid_user', '')
        ctrl.post_fn = stub_rackspace_identity_post

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_invalid_user(self):
        """  Ensure authentication with invalid user credentials fails. """

        ctrl = RackspaceCtrl('invalid_user', 'invalid_api_key')
        ctrl.post_fn = stub_rackspace_identity_post

        auth_result = ctrl.authenticate()
        self.assertEqual(auth_result, False)
        self.assertIsNone(ctrl.token)

    def test_list_regions(self):
        """ Ensure that list_regions returns the correct result. """

        ctrl = RackspaceCtrl('valid_user', 'valid_api_key')
        ctrl.post_fn = stub_rackspace_identity_post

        ctrl.authenticate()
        regions = ctrl.list_regions()

        expected_regions = [
            {'IAD': 'iad'},
            {'DFW': 'dfw'},
            {'SYD': 'syd'},
            {'ORD': 'ord'}
        ]

        self.assertCountEqual(regions, expected_regions)

    def test_token_parsed(self):
        """ Ensure that the token is set. """

        ctrl = RackspaceCtrl('valid_user', 'valid_api_key')
        ctrl.post_fn = stub_rackspace_identity_post

        ctrl.authenticate()

        self.assertEqual('abcdefgh0123456789', ctrl.token)


if __name__ == '__main__':
    unittest.main()
