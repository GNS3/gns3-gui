# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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

"""
QEMU module implementation.
"""

from gns3.qt import QtCore, QtGui
from gns3.local_config import LocalConfig

from ..module import Module
from ..module_error import ModuleError
from .qemu_vm import QemuVM
from .settings import QEMU_SETTINGS, QEMU_SETTING_TYPES
from .settings import QEMU_VM_SETTINGS, QEMU_VM_SETTING_TYPES

import logging
log = logging.getLogger(__name__)


class Qemu(Module):

    """
    QEMU module.
    """

    def __init__(self):
        Module.__init__(self)

        self._settings = {}
        self._qemu_vms = {}
        self._nodes = []

        # load the settings
        self._loadSettings()
        self._loadQemuVMs()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()

        # restore the Qemu settings from QSettings (for backward compatibility)
        legacy_settings = {}
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name in QEMU_SETTINGS.keys():
            if settings.contains(name):
                legacy_settings[name] = settings.value(name, type=QEMU_SETTING_TYPES[name])
        settings.remove("")
        settings.endGroup()

        if legacy_settings:
            local_config.saveSectionSettings(self.__class__.__name__, legacy_settings)
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, QEMU_SETTINGS)

        # keep the config file sync
        self._saveSettings()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

    def _loadQemuVMs(self):
        """
        Load the QEMU VMs from the persistent settings file.
        """

        local_config = LocalConfig.instance()

        # restore the Qemu settings from QSettings (for backward compatibility)
        qemu_vms = []
        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("QemuVMs")
        # load the QEMU VMs
        size = settings.beginReadArray("vm")
        for index in range(0, size):
            settings.setArrayIndex(index)
            vm = {}
            for setting_name, default_value in QEMU_VM_SETTINGS.items():
                vm[setting_name] = settings.value(setting_name, default_value, QEMU_VM_SETTING_TYPES[setting_name])
            qemu_vms.append(vm)
        settings.endArray()
        settings.remove("")
        settings.endGroup()

        if qemu_vms:
            local_config.saveSectionSettings(self.__class__.__name__, {"vms": qemu_vms})

        settings = local_config.settings()
        if "vms" in settings.get(self.__class__.__name__, {}):
            for vm in settings[self.__class__.__name__]["vms"]:
                name = vm.get("name")
                server = vm.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._qemu_vms or not name or not server:
                    continue
                vm_settings = QEMU_VM_SETTINGS.copy()
                vm_settings.update(vm)
                self._qemu_vms[key] = vm_settings

        # keep things sync
        self._saveQemuVMs()

    def _saveQemuVMs(self):
        """
        Saves the QEMU VMs to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, {"vms": list(self._qemu_vms.values())})

    def qemuVMs(self):
        """
        Returns QEMU VMs settings.

        :returns: QEMU VMs settings (dictionary)
        """

        return self._qemu_vms

    def setQemuVMs(self, new_qemu_vms):
        """
        Sets QEMU VM settings.

        :param new_iou_images: IOS images settings (dictionary)
        """

        self._qemu_vms = new_qemu_vms.copy()
        self._saveQemuVMs()

    def addNode(self, node):
        """
        Adds a node to this module.

        :param node: Node instance
        """

        self._nodes.append(node)

    def removeNode(self, node):
        """
        Removes a node from this module.

        :param node: Node instance
        """

        if node in self._nodes:
            self._nodes.remove(node)

    def settings(self):
        """
        Returns the module settings

        :returns: module settings (dictionary)
        """

        return self._settings

    def setSettings(self, settings):
        """
        Sets the module settings

        :param settings: module settings (dictionary)
        """

        self._settings.update(settings)
        self._saveSettings()

    def createNode(self, node_class, server, project):
        """
        Creates a new node.

        :param node_class: Node object
        :param server: HTTPClient instance
        """

        log.info("creating node {}".format(node_class))

        # create an instance of the node class
        return node_class(self, server, project)

    def setupNode(self, node, node_name):
        """
        Setups a node.

        :param node: Node instance
        :param node_name: Node name
        """

        log.info("configuring node {} with id {}".format(node, node.id()))

        vm = None
        if node_name:
            for vm_key, info in self._qemu_vms.items():
                if node_name == info["name"]:
                    vm = vm_key

        if not vm:
            selected_vms = []
            for vm, info in self._qemu_vms.items():
                if info["server"] == node.server().host or (node.server().isLocal() and info["server"] == "local"):
                    selected_vms.append(vm)

            if not selected_vms:
                raise ModuleError("No QEMU VM on server {}".format(node.server().host))
            elif len(selected_vms) > 1:

                from gns3.main_window import MainWindow
                mainwindow = MainWindow.instance()

                (selection, ok) = QtGui.QInputDialog.getItem(mainwindow, "QEMU VM", "Please choose a VM", selected_vms, 0, False)
                if ok:
                    vm = selection
                else:
                    raise ModuleError("Please select a QEMU VM")
            else:
                vm = selected_vms[0]

        settings = {"ram": self._qemu_vms[vm]["ram"],
                    "adapters": self._qemu_vms[vm]["adapters"],
                    "adapter_type": self._qemu_vms[vm]["adapter_type"]}

        # FIXME: this is ugly...
        if self._qemu_vms[vm]["hda_disk_image"]:
            settings["hda_disk_image"] = self._qemu_vms[vm]["hda_disk_image"]

        if self._qemu_vms[vm]["hdb_disk_image"]:
            settings["hdb_disk_image"] = self._qemu_vms[vm]["hdb_disk_image"]

        if self._qemu_vms[vm]["hdc_disk_image"]:
            settings["hdc_disk_image"] = self._qemu_vms[vm]["hdc_disk_image"]

        if self._qemu_vms[vm]["hdd_disk_image"]:
            settings["hdd_disk_image"] = self._qemu_vms[vm]["hdd_disk_image"]

        if self._qemu_vms[vm]["initrd"]:
            settings["initrd"] = self._qemu_vms[vm]["initrd"]

        if self._qemu_vms[vm]["kernel_image"]:
            settings["kernel_image"] = self._qemu_vms[vm]["kernel_image"]

        if self._qemu_vms[vm]["kernel_command_line"]:
            settings["kernel_command_line"] = self._qemu_vms[vm]["kernel_command_line"]

        if self._qemu_vms[vm]["legacy_networking"]:
            settings["legacy_networking"] = self._qemu_vms[vm]["legacy_networking"]

        settings["cpu_throttling"] = self._qemu_vms[vm]["cpu_throttling"]

        if self._qemu_vms[vm]["process_priority"]:
            settings["process_priority"] = self._qemu_vms[vm]["process_priority"]

        if self._qemu_vms[vm]["options"]:
            settings["options"] = self._qemu_vms[vm]["options"]

        qemu_path = self._qemu_vms[vm]["qemu_path"]
        name = self._qemu_vms[vm]["name"]

        if node.server().isCloud():
            settings["cloud_path"] = "images/qemu"

        node.setup(qemu_path, initial_settings=settings, base_name=name)

    def reset(self):
        """
        Resets the servers.
        """

        log.info("QEMU module reset")
        self._nodes.clear()

    def getQemuBinariesFromServer(self, server, callback):
        """
        Gets the QEMU binaries list from a server.

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        """

        server.get("/qemu/binaries", callback)

    @staticmethod
    def getNodeClass(name):
        """
        Returns the object with the corresponding name.

        :param name: object name
        """

        if name in globals():
            return globals()[name]
        return None

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [QemuVM]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        nodes = []
        for qemu_vm in self._qemu_vms.values():
            nodes.append(
                {"class": QemuVM.__name__,
                 "name": qemu_vm["name"],
                 "server": qemu_vm["server"],
                 "default_symbol": qemu_vm["default_symbol"],
                 "hover_symbol": qemu_vm["hover_symbol"],
                 "categories": [qemu_vm["category"]]
                 }
            )
        return nodes

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.qemu_preferences_page import QemuPreferencesPage
        from .pages.qemu_vm_preferences_page import QemuVMPreferencesPage
        return [QemuPreferencesPage, QemuVMPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of QEMU module.

        :returns: instance of Qemu
        """

        if not hasattr(Qemu, "_instance"):
            Qemu._instance = Qemu()
        return Qemu._instance
