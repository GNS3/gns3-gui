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


from unittest.mock import patch, Mock, ANY
from gns3.modules.virtualbox.virtualbox_vm import VirtualBoxVM
from gns3.ports.port import Port
from gns3.base_node import BaseNode


def test_virtualbox_vm_init(local_server, project):

    vm = VirtualBoxVM(None, local_server, project)


def test_virtualbox_vm_create(virtualbox_vm, project):

    with patch('gns3.project.Project.post') as mock:
        virtualbox_vm.create("VMNAME")
        mock.assert_called_with("/nodes",
                                virtualbox_vm.createNodeCallback,
                                body={
                                    'node_id': virtualbox_vm._node_id,
                                    'name': 'VMNAME',
                                    'compute_id': 'local',
                                    'node_type': 'virtualbox',
                                    'properties': {
                                        'linked_clone': False,
                                        'vmname': 'VMNAME'
                                    },
                                    'port_name_format': 'Ethernet{0}',
                                    'port_segment_size': 0,
                                    'first_port_name': ''
                                },
                                context={},
                                timeout=120)

        # Callback
        params = {
            "name": "VBOX1",
            "vmname": "VMNAME",
            "linked_clone": False,
            "adapters": 0,
            "project_id": "f91bd115-3b5c-402e-b411-e5919723cf4b",
            "node_id": "aec7a00c-e71c-45a6-8c04-29e40732883c"
        }
        virtualbox_vm.createNodeCallback(params)
        assert virtualbox_vm.node_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"


def test_update(virtualbox_vm):

    new_settings = {
        "name": "VBOX2",
    }

    with patch('gns3.base_node.BaseNode.controllerHttpPut') as mock:
        virtualbox_vm.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes/{node_id}".format(node_id=virtualbox_vm.node_id())
        assert kwargs["body"] == {
            'node_id': virtualbox_vm._node_id,
            'compute_id': 'local', 'node_type': 'virtualbox', 'properties': {}, 'name': 'VBOX2'}

        # Callback
        args[1]({"name": "VBOX2"})
