# -*- coding: utf-8 -*-
import pytest
import os
import uuid
from unittest.mock import MagicMock
import tempfile
import sys
sys._called_from_test = True

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#  We can get segfault if the QT application is not initialized
from gns3.qt.QtWidgets import QApplication
app = QApplication([])


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

    from gns3.ports.port import Port
    from gns3.modules.vpcs.vpcs_node import VPCSNode
    from gns3.modules.virtualbox.virtualbox_vm import VirtualBoxVM
    from gns3.modules.iou.iou_device import IOUDevice
    from gns3.compute_manager import ComputeManager

    ComputeManager.reset()
    VPCSNode.reset()
    VirtualBoxVM.reset()
    IOUDevice.reset()


@pytest.fixture
def project():

    from gns3.project import Project

    project = Project()
    project.setId(str(uuid.uuid4()))
    project._created = True
    project.setName("unsaved")
    return project


@pytest.fixture
def local_server():
    from gns3.compute_manager import ComputeManager
    return ComputeManager.instance().getCompute("local")


@pytest.fixture
def remote_server():
    from gns3.compute_manager import ComputeManager
    return ComputeManager.instance().getCompute("example.org")


@pytest.fixture
def controller():
    from gns3.controller import Controller

    Controller._instance = None
    c = Controller.instance()
    c._http_client = MagicMock()
    c._http_client.fullUrl.return_value = "http://localhost:3080"
    return c


@pytest.fixture
def vpcs_device(local_server, project):

    from gns3.modules.vpcs.vpcs_node import VPCSNode
    from gns3.modules.vpcs import VPCS

    device = VPCSNode(VPCS(), local_server, project)
    device._node_id = str(uuid.uuid4())
    device._settings = {"name": "VPCS 1", "script_file": "", "console": None, "startup_script": None}
    device.setInitialized(True)
    return device


@pytest.fixture
def iou_device(local_server, project):

    from gns3.modules.iou.iou_device import IOUDevice
    from gns3.modules.iou import IOU

    device = IOUDevice(IOU(), local_server, project)
    device._node_id = str(uuid.uuid4())
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
    vm._node_id = str(uuid.uuid4())
    vm._settings = {"name": "VBOX1",
                    "vmname": "VBOX1",
                    "console": None,
                    "adapters": 0,
                    "ram": 0,
                    "use_any_adapter": False,
                    "adapter_type": "Intel PRO/1000 MT Desktop (82540EM)",
                    "headless": False}
    vm.setInitialized(True)
    return vm


@pytest.fixture
def qemu_vm(local_server, project):

    from gns3.modules.qemu.qemu_vm import QemuVM
    from gns3.modules.qemu import Qemu

    vm = QemuVM(Qemu(), local_server, project)
    vm._node_id = str(uuid.uuid4())
    vm._settings = {"name": "QEMU1"}
    vm.setInitialized(True)
    return vm


@pytest.fixture
def local_config():
    from gns3.local_config import LocalConfig

    (fd, config_path) = tempfile.mkstemp()
    os.close(fd)

    LocalConfig._instance = LocalConfig(config_file=config_path)
    return LocalConfig.instance()


@pytest.fixture(autouse=True)
def run_around_tests(local_config, main_window):
    """
    This setup a temporary environment around tests
    """

    from gns3.main_window import MainWindow
    MainWindow._instance = main_window
    yield


@pytest.fixture
def main_window():
    """
    Get a mocked main window
    """
    window = MagicMock()

    uiGraphicsView = MagicMock()
    uiGraphicsView.settings.return_value = {
        "default_label_font": "TypeWriter,10,-1,5,75,0,0,0,0,0",
        "default_label_color": "#000000",
        "default_note_font": "TypeWriter,10,-1,5,75,0,0,0,0,0",
        "default_note_color": "#000000"
    }

    window.uiGraphicsView = uiGraphicsView
    return window


@pytest.fixture
def images_dir(tmpdir):
    os.makedirs(os.path.join(str(tmpdir), "images", "QEMU"), exist_ok=True)
    os.makedirs(os.path.join(str(tmpdir), "images", "IOS"), exist_ok=True)
    os.makedirs(os.path.join(str(tmpdir), "images", "IOU"), exist_ok=True)
    return os.path.join(str(tmpdir), "images")


@pytest.fixture
def symbols_dir(tmpdir):
    os.makedirs(os.path.join(str(tmpdir), "symbols"), exist_ok=True)
    return os.path.join(str(tmpdir), "symbols")


@pytest.fixture
def linux_microcore_img(images_dir):
    """
    Create a fake image and return the path. The md5sum of the file will be 5d41402abc4b2a76b9719d911017c592
    """

    path = os.path.join(images_dir, "QEMU", "linux-microcore-3.4.1.img")
    with open(path, 'w+') as f:
        f.write("hello")
    return path


@pytest.fixture
def iou_l3(images_dir):
    """
    Create a fake image and return the path. The md5sum of the file will be 5d41402abc4b2a76b9719d911017c592
    """

    path = os.path.join(images_dir, "IOU", "i86bi-linux-l3-adventerprisek9-15.4.1T.bin")
    with open(path, 'w+') as f:
        f.write("hello")
    return path


@pytest.fixture
def cisco_3745(images_dir):
    """
    Create a fake image and return the path. The md5sum of the file will be 5d41402abc4b2a76b9719d911017c592
    """

    path = os.path.join(images_dir, "IOS", "c3745-adventerprisek9-mz.124-25d.image")
    with open(path, 'w+') as f:
        f.write("hello")
    return path


def pytest_configure(config):
    """
    Use to detect in code if we are running from pytest

    http://pytest.org/latest/example/simple.html#detect-if-running-from-within-a-pytest-run
    """
    import sys
    sys._called_from_test = True


def pytest_unconfigure(config):
    del sys._called_from_test
