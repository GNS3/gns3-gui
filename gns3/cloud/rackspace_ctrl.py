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

""" Interacts with Rackspace API to create and manage cloud instances. """

from .base_cloud_ctrl import BaseCloudCtrl
import json
import requests
from libcloud.compute.drivers.rackspace import ENDPOINT_ARGS_MAP
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider
from libcloud.storage.providers import get_driver as get_storage_driver
from libcloud.storage.types import Provider as StorageProvider

from .exceptions import ItemNotFound, ApiError
from ..version import __version__

from collections import OrderedDict

import logging
log = logging.getLogger(__name__)

RACKSPACE_REGIONS = [{ENDPOINT_ARGS_MAP[k]['region']: k} for k in
                     ENDPOINT_ARGS_MAP]


class RackspaceCtrl(BaseCloudCtrl):

    """ Controller class for interacting with Rackspace API. """

    def __init__(self, username, api_key, *args, **kwargs):
        super(RackspaceCtrl, self).__init__(username, api_key)

        # set this up so it can be swapped out with a mock for testing
        self.post_fn = requests.post
        self.driver_cls = get_driver(Provider.RACKSPACE)
        self.storage_driver_cls = get_storage_driver(StorageProvider.CLOUDFILES)

        self.driver = None
        self.storage_driver = None
        self.region = None
        self.instances = {}

        self.authenticated = False
        self.identity_ep = \
            "https://identity.api.rackspacecloud.com/v2.0/tokens"

        self.regions = []
        self.token = None
        self.tenant_id = None
        self.flavor_ep = "https://dfw.servers.api.rackspacecloud.com/v2/{username}/flavors"
        self._flavors = OrderedDict([
            ('2', '512MB, 1 VCPU'),
            ('3', '1GB, 1 VCPU'),
            ('4', '2GB, 2 VCPUs'),
            ('5', '4GB, 2 VCPUs'),
            ('6', '8GB, 4 VCPUs'),
            ('7', '15GB, 6 VCPUs'),
            ('8', '30GB, 8 VCPUs'),
            ('performance1-1', '1GB Performance, 1 VCPU'),
            ('performance1-2', '2GB Performance, 2 VCPUs'),
            ('performance1-4', '4GB Performance, 4 VCPUs'),
            ('performance1-8', '8GB Performance, 8 VCPUs'),
            ('performance2-15', '15GB Performance, 4 VCPUs'),
            ('performance2-30', '30GB Performance, 8 VCPUs'),
            ('performance2-60', '60GB Performance, 16 VCPUs'),
            ('performance2-90', '90GB Performance, 24 VCPUs'),
            ('performance2-120', '120GB Performance, 32 VCPUs',)
        ])

    def authenticate(self):
        """
        Submit username and api key to API service.

        If authentication is successful, set self.regions and self.token.
        Return boolean.

        """

        self.authenticated = False

        if len(self.username) < 1:
            return False

        if len(self.api_key) < 1:
            return False

        data = json.dumps({
            "auth": {
                "RAX-KSKEY:apiKeyCredentials": {
                    "username": self.username,
                    "apiKey": self.api_key
                }
            }
        })

        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        response = self.post_fn(self.identity_ep, data=data, headers=headers)

        if response.status_code == 200:

            api_data = response.json()
            self.token = self._parse_token(api_data)

            if self.token:
                self.authenticated = True
                user_regions = self._parse_endpoints(api_data)
                self.regions = self._make_region_list(user_regions)
                self.tenant_id = self._parse_tenant_id(api_data)

        else:
            self.regions = []
            self.token = None

        response.connection.close()

        return self.authenticated

    def list_regions(self):
        """ Return a list the regions available to the user. """

        return self.regions

    def list_flavors(self):
        """ Return the dictionary containing flavors id and names """

        return self._flavors

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

    def _parse_tenant_id(self, api_data):
        """  """
        try:
            roles = api_data['access']['user']['roles']
            for role in roles:
                if 'tenantId' in role and role['name'] == 'compute:default':
                    return role['tenantId']
            return None
        except KeyError:
            return None

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

    def set_region(self, region):
        """ Set self.region and self.driver. Returns True or False. """

        try:
            self.driver = self.driver_cls(self.username, self.api_key,
                                          region=region)
            self.storage_driver = self.storage_driver_cls(self.username, self.api_key,
                                                          region=region)

        except ValueError:
            return False

        self.region = region
        return True

    def get_image(self, image_id):
        return self.driver.get_image(image_id)


def get_provider(cloud_settings):
    """
    Utility function to retrieve a cloud provider instance already authenticated and with the
    region set

    :param cloud_settings: cloud settings dictionary
    :return: a provider instance or None on errors
    """
    try:
        username = cloud_settings['cloud_user_name']
        apikey = cloud_settings['cloud_api_key']
        region = cloud_settings['cloud_region']
    except KeyError as e:
        log.error("Unable to create cloud provider: {}".format(e))
        return

    provider = RackspaceCtrl(username, apikey)

    if not provider.authenticate():
        log.error("Authentication failed for cloud provider")
        return

    if not region:
        region = provider.list_regions().values()[0]

    if not provider.set_region(region):
        log.error("Unable to set cloud provider region")
        return

    return provider
