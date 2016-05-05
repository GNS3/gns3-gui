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
from gns3.modules.docker.docker_vm import DockerVM
from gns3.modules.docker import Docker
from gns3.ports.port import Port
from gns3.nios.nio_udp import NIOUDP
from gns3.node import Node


def test_docker_vm_init(local_server, project):

    vm = DockerVM(Docker(), local_server, project)


def test_docker_vm_setup(project, local_server):

    docker_vm = DockerVM(Docker(), local_server, project)
    with patch('gns3.node.Node.httpPost') as mock:
        docker_vm.setup("ubuntu", base_name="ubuntu")
        assert docker_vm._settings == {
            'image': 'ubuntu',
            'name': 'ubuntu-1',
            'start_command': '',
            'adapters': 1,
            'console': None,
            'environment': '',
            'console_type': 'telnet',
            'console_resolution': '1024x768',
            'console_http_path': '/',
            'console_http_port': 80,
            'aux': None
        }
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/docker/vms".format(project_id=project.id())
        assert kwargs["body"] == {
            "adapters": 1,
            "image": "ubuntu",
            "name": "ubuntu-1"
        }


def test_setupCallback(project, local_server):
    docker_vm = DockerVM(Docker(), local_server, project)

    # Callback
    params = {
        "name": "DOCKER1",
        "vm_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
    }
    docker_vm._setupCallback(params)

    assert docker_vm.vm_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"
    assert docker_vm.name() == "DOCKER1"


def test_dump(project, local_server):
    vm = DockerVM(Docker(), local_server, project)
    vm._settings["name"] = "ubuntu-1"
    assert vm.dump() == {
        'description': 'Docker container',
        'id': vm.id(),
        'properties': {
            'adapters': 1,
            'name': 'ubuntu-1',
            'console_type': 'telnet',
            'console_resolution': '1024x768',
            'console_http_path': '/',
            'console_http_port': 80
        },
        'server_id': 0,
        'type': 'DockerVM',
        'vm_id': None
    }


def test_load(project, local_server):
    node = {
        "description": "Docker image",
        "id": 1,
        "label": {
          "color": "#ff000000",
          "font": "TypeWriter,10,-1,5,75,0,0,0,0,0",
          "text": "mysql:latest",
          "x": -2.609375,
          "y": -25
        },
        "ports": [
          {
            "adapter_number": 0,
            "id": 1,
            "name": "Ethernet0",
            "port_number": 0
          }
        ],
        "properties": {
          "adapters": 1,
          "console": 6000,
          "image": "mysql:latest",
          "name": "mysql:latest-1",
          "start_command": "/bin/ls"
        },
        "server_id": 1,
        "type": "DockerVM",
        "vm_id": "ec35076f-f6e5-4c72-a594-e94a47419710",
        "x": -102.5,
        "y": -229.5
    }

    docker_vm = DockerVM(Docker(), local_server, project)
    with patch('gns3.node.Node.httpPost') as mock:
        docker_vm.load(node)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/docker/vms".format(project_id=project.id())
        assert kwargs["body"] == {
            "image": "mysql:latest",
            "name": "mysql:latest-1",
            "adapters": 1,
            "start_command": "/bin/ls",
            "console": 6000,
            "vm_id": "ec35076f-f6e5-4c72-a594-e94a47419710",
        }

