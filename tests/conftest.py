# -*- coding: utf-8 -*-
import pytest
import os
import uuid

from gns3.project import Project
from gns3.servers import Servers
from gns3.modules.vpcs.vpcs_device import VPCSDevice
from gns3.modules.vpcs import VPCS


def pytest_addoption(parser):
    parser.addoption("--username", action="store",
                     help="rackspace username for integration tests")
    parser.addoption("--apikey", action="store",
                     help="rackspace apikey for integration tests")
    parser.addoption("--run-instances", action="store_true",
                     help="wait for instances to run while testing")


@pytest.fixture(scope="class")
def username(request):
    request.cls.username = request.config.getoption("--username") or os.environ.get('RACKSPACE_USERNAME')


@pytest.fixture(scope="class")
def api_key(request):
    request.cls.api_key = request.config.getoption("--apikey") or os.environ.get('RACKSPACE_APIKEY')


@pytest.fixture(scope="class")
def run_instances(request):
    request.cls.run_instances = request.config.getoption("--run-instances")


@pytest.fixture(scope="session")
def project():
    project = Project.instance()
    project.uuid = str(uuid.uuid4())
    project.type = 'local'
    project.name = 'unsaved'
    return project


@pytest.fixture(scope="session")
def local_server():
    return Servers.instance().localServer()


@pytest.fixture
def vpcs_device(local_server, project):
    vpcs_device = VPCSDevice(VPCS(), local_server, project)
    vpcs_device._vpcs_device_id = str(uuid.uuid4())
    vpcs_device.setInitialized(True)
    return vpcs_device


def pytest_runtest_setup(item):
    """
    Skip all tests marked with @rackspace_authentication if username and apikey were neither
    passed to command line nor set as environment vars
    """
    user = item.config.getoption("--username") or os.environ.get('RACKSPACE_USERNAME')
    key = item.config.getoption("--apikey") or os.environ.get('RACKSPACE_APIKEY')

    credentials_passed = user and key

    if 'rackspace_authentication' in item.keywords and not credentials_passed:
        pytest.skip("need rackspace authentication options to run")
