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
from gns3.modules.docker.docker_vm import DockerVM
from gns3.modules.docker import Docker
from gns3.ports.port import Port


def test_docker_vm_init(local_server, project):

    vm = DockerVM(Docker(), local_server, project)


def test_docker_vm_create(project, local_server):

    docker_vm = DockerVM(Docker(), local_server, project)
    with patch('gns3.project.Project.post') as mock:
        docker_vm.create("ubuntu", base_name="ubuntu")
        mock.assert_called_with("/nodes",
                                docker_vm.createNodeCallback,
                                body={
                                    "node_id": docker_vm._node_id,
                                    "compute_id": "local",
                                    "node_type": "docker",
                                    "properties": {
                                        "adapters": 1,
                                        "image": "ubuntu",
                                    },
                                    "name": "ubuntu-{0}"
                                },
                                context={},
                                timeout=None)


def test_createCallback(project, local_server):
    docker_vm = DockerVM(Docker(), local_server, project)

    # Callback
    params = {
        "name": "DOCKER1",
        "node_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
        "properties": {
            "image": "ubuntu"
        }
    }
    docker_vm.createNodeCallback(params)

    assert docker_vm.node_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"
    assert docker_vm.name() == "DOCKER1"
    assert docker_vm._settings["image"] == "ubuntu"
