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


from unittest.mock import patch, Mock


def test_allocateUDPPort(vpcs_device):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        vpcs_device.allocateUDPPort(1)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/ports/udp"

        # Connect the signal
        signal_mock = Mock()
        vpcs_device.allocate_udp_nio_signal.connect(signal_mock)

        # Callback
        args[1]({"udp_port": 4242}, context=kwargs["context"])

        # Check the signal
        assert signal_mock.called
        args, kwargs = signal_mock.call_args
        assert args[0] == vpcs_device.id()
        assert args[1] == 1
        assert args[2] == 4242
