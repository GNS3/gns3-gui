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

import os
import shlex

from unittest.mock import patch
from gns3.spice_console import spiceConsole


def test_spice_console_on_linux_and_mac(vpcs_device):

    with patch('subprocess.Popen') as popen, \
            patch('sys.platform', new="linux"):
        vpcs_device.settings()["console_host"] = "localhost"
        spiceConsole(vpcs_device, '2525', 'command %h %p')
        popen.assert_called_with(shlex.split('command localhost 2525'), env=os.environ)
        spiceConsole(vpcs_device, '2525', 'command {host} {port}')
        popen.assert_called_with(shlex.split('command localhost 2525'), env=os.environ)

def test_spice_console_on_windows(vpcs_device):

    with patch('subprocess.Popen') as p, \
            patch('sys.platform', new="win"):
        vpcs_device.settings()["console_host"] = "localhost"
        spiceConsole(vpcs_device, '2525', 'command %h %p')
        p.assert_called_with('command localhost 2525', env=os.environ)
        spiceConsole(vpcs_device, '2525', 'command {host} {port}')
        p.assert_called_with('command localhost 2525', env=os.environ)

# def test_spice_console_on_linux_with_popen_issues():
#     with patch('subprocess.Popen', side_effect=OSError("Dummy")), \
#             patch('sys.platform', new="linux"):
#
#         with pytest.raises(OSError):
#             spiceConsole('localhost', '2525', 'command %h %p')


def test_spice_console_with_ipv6_support(vpcs_device):

    with patch('subprocess.Popen') as popen, \
            patch('sys.platform', new="linux"):
        vpcs_device.settings()["console_host"] = "::1"
        spiceConsole(vpcs_device, '2525', 'command %h %p')
        popen.assert_called_with(shlex.split('command [::1] 2525'), env=os.environ)
        spiceConsole(vpcs_device, '2525', 'command {host} {port}')
        popen.assert_called_with(shlex.split('command [::1] 2525'), env=os.environ)
