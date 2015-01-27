# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
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

import pytest
import uuid
from unittest.mock import patch

from gns3.modules.vpcs.vpcs_device import VPCSDevice
from gns3.modules.vpcs import VPCS


@pytest.fixture
def vpcs(local_server, project):
    vpcs = VPCSDevice(VPCS(), local_server, project)
    vpcs._vpcs_id = str(uuid.uuid4())
    return vpcs


def test_vpcs_device_init(local_server, project):

    vpcs = VPCSDevice(None, local_server, project)


def test_vpcs_device_setup(vpcs):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        vpcs.setup()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs"

        # Callback
        params = {
            "console": 2000,
            "name": "PC1",
            "project_uuid": "f91bd115-3b5c-402e-b411-e5919723cf4b",
            "script_file": None,
            "startup_script": None,
            "uuid": "aec7a00c-e71c-45a6-8c04-29e40732883c"
        }
        args[2](params)

        assert vpcs.uuid == "aec7a00c-e71c-45a6-8c04-29e40732883c"

def test_vpcs_device_start(vpcs):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        vpcs.start()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/{uuid}/start".format(uuid=vpcs.uuid)

