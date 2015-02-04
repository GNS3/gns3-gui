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
from gns3.modules.virtualbox.virtualbox_vm import VirtualBoxVM
from gns3.ports.port import Port
from gns3.nios.nio_udp import NIOUDP
from gns3.node import Node


def test_virtualbox_vm_init(local_server, project):

    vm = VirtualBoxVM(None, local_server, project)


def test_virtualbox_vm_setup(virtualbox_vm):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        virtualbox_vm.setup("VMNAME")
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/virtualbox/vms"

        # Callback
        params = {
            "name": "VBOX1",
            "vmname": "VMNAME",
            "linked_clone": False,
            "adapters": 0,
            "project_id": "f91bd115-3b5c-402e-b411-e5919723cf4b",
            "vm_id": "aec7a00c-e71c-45a6-8c04-29e40732883c"
        }
        args[1](params)
        assert virtualbox_vm.vm_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"


def test_virtualbox_vm_start(virtualbox_vm):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        virtualbox_vm.start()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/virtualbox/vms/{vm_id}/start".format(vm_id=virtualbox_vm.vm_id())


def test_virtualbox_vm_stop(virtualbox_vm):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        virtualbox_vm.setStatus(Node.started)
        virtualbox_vm.stop()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/virtualbox/vms/{vm_id}/stop".format(vm_id=virtualbox_vm.vm_id())


def test_virtualbox_vm_reload(virtualbox_vm):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        virtualbox_vm.reload()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/virtualbox/vms/{vm_id}/reload".format(vm_id=virtualbox_vm.vm_id())


def test_allocateUDPPort(virtualbox_vm):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        virtualbox_vm.allocateUDPPort(1)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/ports/udp"

        # Connect the signal
        signal_mock = Mock()
        virtualbox_vm.allocate_udp_nio_signal.connect(signal_mock)

        # Callback
        args[1]({"udp_port": 4242})

        # Check the signal
        assert signal_mock.called
        args, kwargs = signal_mock.call_args
        assert args[0] == virtualbox_vm.id()
        assert args[1] == 1
        assert args[2] == 4242


def test_addNIO(virtualbox_vm):

    with patch('gns3.http_client.HTTPClient.post') as mock:
        port = Port("Port 0")
        port.setPortNumber(0)
        nio = NIOUDP(4242, "127.0.0.1", 4243)
        virtualbox_vm.addNIO(port, nio)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/virtualbox/vms/{vm_id}/adapters/0/nio".format(vm_id=virtualbox_vm.vm_id())

        # Connect the signal
        signal_mock = Mock()
        virtualbox_vm.nio_signal.connect(signal_mock)

        # Callback
        args[1]({})

        # Check the signal
        assert signal_mock.called
        args, kwargs = signal_mock.call_args
        assert args[0] == virtualbox_vm.id()
        assert args[1] == port.id()


def test_deleteNIO(virtualbox_vm):

    with patch('gns3.http_client.HTTPClient.post') as mock_post:
        with patch('gns3.http_client.HTTPClient.delete') as mock_delete:
            port = Port("Port 0")
            port.setPortNumber(0)
            nio = NIOUDP(4242, "127.0.0.1", 4243)
            virtualbox_vm.addNIO(port, nio)

            virtualbox_vm.deleteNIO(port)
            assert mock_delete.called

            args, kwargs = mock_delete.call_args
            assert args[0] == "/virtualbox/vms/{vm_id}/adapters/0/nio".format(vm_id=virtualbox_vm.vm_id())


def test_update(virtualbox_vm):

    new_settings = {
        "name": "VBOX2",
    }

    with patch('gns3.http_client.HTTPClient.put') as mock:
        virtualbox_vm.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/virtualbox/vms/{vm_id}".format(vm_id=virtualbox_vm.vm_id())
        assert kwargs["body"] == new_settings

        # Callback
        args[1]({"name": "VBOX2"})
