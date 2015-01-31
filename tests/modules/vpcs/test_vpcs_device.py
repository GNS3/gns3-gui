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
from gns3.modules.vpcs.vpcs_device import VPCSDevice
from gns3.ports.port import Port
from gns3.nios.nio_udp import NIOUDP
from gns3.node import Node
from gns3.utils.normalize_filename import normalize_filename


def test_vpcs_device_init(local_server, project):

    vpcs_device = VPCSDevice(None, local_server, project)


def test_vpcs_device_setup(vpcs_device):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        vpcs_device.setup()
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
        args[1](params)

        assert vpcs_device.uuid() == "aec7a00c-e71c-45a6-8c04-29e40732883c"


def test_vpcs_device_start(vpcs_device):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        vpcs_device.start()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/{uuid}/start".format(uuid=vpcs_device.uuid())


def test_vpcs_device_stop(vpcs_device):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        vpcs_device.setStatus(Node.started)
        vpcs_device.stop()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/{uuid}/stop".format(uuid=vpcs_device.uuid())


def test_vpcs_device_reload(vpcs_device):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        vpcs_device.reload()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/{uuid}/reload".format(uuid=vpcs_device.uuid())


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
        args[1]({"udp_port": 4242})

        # Check the signal
        assert signal_mock.called
        args, kwargs = signal_mock.call_args
        assert args[0] == vpcs_device.id()
        assert args[1] == 1
        assert args[2] == 4242


def test_addNIO(vpcs_device):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        port = Port("Port 1")
        nio = NIOUDP(4242, "127.0.0.1", 4243)
        vpcs_device.addNIO(port, nio)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/{uuid}/ports/0/nio".format(uuid=vpcs_device.uuid())

        # Connect the signal
        signal_mock = Mock()
        vpcs_device.nio_signal.connect(signal_mock)

        # Callback
        args[1]({})

        # Check the signal
        assert signal_mock.called
        args, kwargs = signal_mock.call_args
        assert args[0] == vpcs_device.id()
        assert args[1] == port.id()


def test_deleteNIO(vpcs_device):

    with patch('gns3.http_client.HTTPClient.post') as mock_post:
        with patch('gns3.http_client.HTTPClient.delete') as mock_delete:
            port = Port("Port 1")
            nio = NIOUDP(4242, "127.0.0.1", 4243)
            vpcs_device.addNIO(port, nio)

            vpcs_device.deleteNIO(port)
            assert mock_delete.called

            args, kwargs = mock_delete.call_args
            assert args[0] == "/vpcs/{uuid}/ports/0/nio".format(uuid=vpcs_device.uuid())


def test_exportConfig(tmpdir, vpcs_device):

    path = tmpdir / 'startup.vpcs'

    with patch('gns3.http_client.HTTPClient.get') as mock:
        vpcs_device.exportConfig(str(path))

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/{uuid}".format(uuid=vpcs_device.uuid())

        # Callback
        args[1]({"startup_script": "echo TEST"})

        assert path.exists()

        with open(str(path)) as f:
            assert f.read() == "echo TEST"


def test_exportConfigToDirectory(tmpdir, vpcs_device):

    path = tmpdir / normalize_filename(vpcs_device.name()) + '_startup.vpc'

    with patch('gns3.http_client.HTTPClient.get') as mock:
        vpcs_device.exportConfigToDirectory(str(tmpdir))

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/{uuid}".format(uuid=vpcs_device.uuid())

        # Callback
        args[1]({"startup_script": "echo TEST"})

        assert path.exists()

        with open(str(path)) as f:
            assert f.read() == "echo TEST"


def test_update(vpcs_device):

    new_settings = {
        "name": "Unreal VPCS",
        "script_file": "echo TEST"
    }

    with patch('gns3.http_client.HTTPClient.put') as mock:
        vpcs_device.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/{uuid}".format(uuid=vpcs_device.uuid())
        assert kwargs["body"] == new_settings

        # Callback
        args[1]({"startup_script": "echo TEST", "name": "Unreal VPCS"})


def test_importConfig(vpcs_device, tmpdir):

    path = str(tmpdir / 'startup.vpcs')
    content = "echo TEST"

    with open(path, 'w+') as f:
        f.write(content)

    with patch('gns3.http_client.HTTPClient.put') as mock:
        vpcs_device.importConfig(path)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/{uuid}".format(uuid=vpcs_device.uuid())
        assert kwargs["body"] == {"startup_script": content}
