# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Interacts with Cloud API(s) to create and manage cloud instances. """

import json
import requests
from libcloud.compute.drivers.rackspace import ENDPOINT_ARGS_MAP

import logging
log = logging.getLogger(__name__)

RACKSPACE_REGIONS = [{ENDPOINT_ARGS_MAP[k]['region']: k} for k in
                     ENDPOINT_ARGS_MAP]


class BaseCloudCtrl(object):

    """ Base class for interacting with a cloud provider API. """

    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def authenticate(self):
        raise NotImplementedError

    def list_regions(self):
        raise NotImplementedError

    def list_instances(self):
        raise NotImplementedError

    def get_instance(self, instance_id):
        raise NotImplementedError

    def terminate_instance(self, instance_id):
        raise NotImplementedError


class RackspaceCtrl(BaseCloudCtrl):

    """ Controller class for interacting with Rackspace API. """

    def __init__(self, username, api_key):
        super(RackspaceCtrl, self).__init__(username, api_key)

        # set this up so it can be swapped out with a mock for testing
        self.post_fn = requests.post

        self.authenticated = False
        self.identity_ep = \
            "https://identity.api.rackspacecloud.com/v2.0/tokens"

        self.regions = []
        self.token = None

    def authenticate(self):
        """
        Submit username and api key to API service.

        If authentication is successful, set self.regions and self.token.
        Return boolean.

        """

        self.authenticated = False

        data = json.dumps({
            "auth": {
                "RAX-KSKEY:apiKeyCredentials": {
                    "username": self.username,
                    "apiKey": self.api_key
                }
            }
        })

        headers = {'Content-type': 'application/json'}
        response = self.post_fn(self.identity_ep, data=data, headers=headers)

        if response.status_code == 200:

            self.token = self._parse_token(response.json())

            if self.token:
                self.authenticated = True
                user_regions = self._parse_endpoints(response.json())
                self.regions = self._make_region_list(user_regions)

        else:
            self.regions= []
            self.token = None

        return self.authenticated

    def list_regions(self):
        """ Return a list the regions available to the user. """

        return self.regions

    def _parse_endpoints(self, api_data):
        """
        Parse the JSON-encoded data returned by the Identity Service API.

        Return a list of regions available for Compute v2.

        """

        region_codes = []

        for ep_type in api_data['access']['serviceCatalog']:
            if ep_type['name'] == "cloudServersOpenStack" \
                    and ep_type['type'] == "compute":

                for ep in ep_type['endpoints']:
                    if ep['versionId'] == "2":
                        region_codes.append(ep['region'])

        return region_codes

    def _parse_token(self, api_data):
        """ Parse the token from the JSON-encoded data returned by the API. """

        try:
            token = api_data['access']['token']['id']
        except KeyError:
            return None

        return token

    def _make_region_list(self, region_codes):
        """
        Make a list of regions for use in the GUI.

        Returns a list of key-value pairs in the form:
            <API's Region Name>: <libcloud's Region Name>
            eg,
            [
                {'DFW': 'dfw'}
                {'ORD': 'ord'},
                ...
            ]

        """

        region_list = []

        for ep in ENDPOINT_ARGS_MAP:
            if ENDPOINT_ARGS_MAP[ep]['region'] in region_codes:
                region_list.append({ENDPOINT_ARGS_MAP[ep]['region']: ep})

        return region_list
