# -*- coding: utf-8 -*-
import pytest
import os
import uuid
import unittest
import sys


# If the QT application is not initialized we can got segfault
from PyQt4.QtGui import QApplication
app = QApplication([])


def pytest_addoption(parser):
    parser.addoption("--username", action="store",
                     help="rackspace username for integration tests")
    parser.addoption("--apikey", action="store",
                     help="rackspace apikey for integration tests")
    parser.addoption("--run-instances", action="store_true",
                     help="wait for instances to run while testing")


@pytest.fixture(autouse=True)
def reset_qt_signal():
    """
    Reset the QT signals between tests. Otherwise
    you can get callback on code from previous test.
    """

    from gns3.qt import FakeQtSignal

    FakeQtSignal.reset()


@pytest.fixture(autouse=True)
def reset_modules():
    """
    Reset modules (VPCS, VirtualBox...) internal variables.
    """

    from gns3.http_client import HTTPClient
    from gns3.ports.port import Port
    from gns3.modules.vpcs.vpcs_device import VPCSDevice
    from gns3.modules.virtualbox.virtualbox_vm import VirtualBoxVM
    from gns3.modules.iou.iou_device import IOUDevice

    Port.reset()
    VPCSDevice.reset()
    VirtualBoxVM.reset()
    HTTPClient.reset()
    IOUDevice.reset()


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
def project(local_server):

    from gns3.project import Project

    project = Project()
    project.setId(str(uuid.uuid4()))
    project._created_servers.add(local_server)
    project.setType("local")
    project.setName("unsaved")
    return project


@pytest.fixture(scope="session")
def local_server():

    from gns3.servers import Servers

    return Servers.instance().localServer()


@pytest.fixture(scope="session")
def remote_server():

    from gns3.servers import Servers

    return Servers.instance().localServer()


@pytest.fixture(scope="session")
def remote_server():

    from gns3.servers import Servers

    return Servers.instance().getRemoteServer("127.0.0.1", 8001)


@pytest.fixture
def vpcs_device(local_server, project):

    from gns3.modules.vpcs.vpcs_device import VPCSDevice
    from gns3.modules.vpcs import VPCS

    device = VPCSDevice(VPCS(), local_server, project)
    device._vpcs_device_id = str(uuid.uuid4())
    device._settings = {"name": "VPCS 1", "script_file": "", "console": None, "startup_script": None}
    device.setInitialized(True)
    return device


@pytest.fixture
def iou_device(local_server, project):

    from gns3.modules.iou.iou_device import IOUDevice
    from gns3.modules.iou import IOU

    device = IOUDevice(IOU(), local_server, project)
    device._iou_device_id = str(uuid.uuid4())
    settings = device._settings
    settings["name"] = "IOU 1"
    device._settings = settings
    device.setInitialized(True)
    return device


@pytest.fixture
def virtualbox_vm(local_server, project):

    from gns3.modules.virtualbox.virtualbox_vm import VirtualBoxVM
    from gns3.modules.virtualbox import VirtualBox

    vm = VirtualBoxVM(VirtualBox(), local_server, project)
    vm._virtualbox_vm_id = str(uuid.uuid4())
    vm._settings = {"name": "VBOX1",
                    "vmname": "VBOX1",
                    "console": None,
                    "adapters": 0,
                    "ram": 0,
                    "use_any_adapter": False,
                    "adapter_type": "Intel PRO/1000 MT Desktop (82540EM)",
                    "headless": False,
                    "enable_remote_console": False}
    vm.setInitialized(True)
    return vm


@pytest.fixture
def qemu_vm(local_server, project):

    from gns3.modules.qemu.qemu_vm import QemuVM
    from gns3.modules.qemu import Qemu

    vm = QemuVM(Qemu(), local_server, project)
    vm._qemu_id = str(uuid.uuid4())
    vm._settings = {"name": "QEMU1"}
    vm.setInitialized(True)
    return vm


@pytest.fixture
def main_window():
    """
    Get a mocked main window
    """
    window = unittest.mock.MagicMock()

    uiGraphicsView = unittest.mock.MagicMock()
    uiGraphicsView.settings.return_value = {
        "default_label_font": "TypeWriter,10,-1,5,75,0,0,0,0,0",
        "default_label_color": "#000000"
    }

    window.uiGraphicsView = uiGraphicsView
    return window


def pytest_configure(config):
    """
    Use to detect in code if we are running from pytest

    http://pytest.org/latest/example/simple.html#detect-if-running-from-within-a-pytest-run
    """
    import sys
    sys._called_from_test = True


def pytest_unconfigure(config):
    del sys._called_from_test


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
