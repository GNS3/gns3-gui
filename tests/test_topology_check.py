# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
import os
import json

from gns3.topology_check import getTopologyValidationErrors


schemas_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "schemas")


@pytest.mark.parametrize("file", os.listdir(schemas_directory))
def test_load(file):
    with open(os.path.join(schemas_directory, file)) as f:
        topology = json.load(f)
        errors = getTopologyValidationErrors(topology)
        assert errors is None, errors


@pytest.mark.parametrize("file", os.listdir(schemas_directory))
def test_load_invalid(file):
    with open(os.path.join(schemas_directory, file)) as f:
        topology = json.load(f)
        if len(topology["topology"].get("nodes", [])) > 0:

            # Simulate an error
            del topology["topology"]["nodes"][0]["properties"]["name"]

            errors = getTopologyValidationErrors(topology)
            assert errors is not None, errors
