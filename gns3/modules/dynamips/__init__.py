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
Dynamips module implementation.
"""

import os
import shutil
import hashlib

from gns3.qt import QtWidgets
from gns3.local_config import LocalConfig
from gns3.image_manager import ImageManager
from gns3.local_server_config import LocalServerConfig

from ..module import Module
from ..module_error import ModuleError
from .nodes.router import Router
from .nodes.c1700 import C1700
from .nodes.c2600 import C2600
from .nodes.c2691 import C2691
from .nodes.c3600 import C3600
from .nodes.c3725 import C3725
from .nodes.c3745 import C3745
from .nodes.c7200 import C7200
from .nodes.etherswitch_router import EtherSwitchRouter
from .nodes.ethernet_switch import EthernetSwitch
from .nodes.ethernet_hub import EthernetHub
from .nodes.frame_relay_switch import FrameRelaySwitch
from .nodes.atm_switch import ATMSwitch
from .settings import DYNAMIPS_SETTINGS
from .settings import IOS_ROUTER_SETTINGS
from .settings import DEFAULT_IDLEPC

PLATFORM_TO_CLASS = {
    "c1700": C1700,
    "c2600": C2600,
    "c2691": C2691,
    "c3600": C3600,
    "c3725": C3725,
    "c3745": C3745,
    "c7200": C7200
}

import logging
log = logging.getLogger(__name__)


class Dynamips(Module):

    """
    Dynamips module.
    """

    def __init__(self):
        super().__init__()

        self._settings = {}
        self._ios_routers = {}
        self._nodes = []
        self._ios_images_cache = {}

        self.configChangedSlot()

    def configChangedSlot(self):
        # load the settings and IOS images.
        self._loadSettings()

    @staticmethod
    def getDefaultIdlePC(path):
        """
        Return the default IDLE PC for an image if the image
        exists or None otherwise
        """
        if not os.path.isfile(path):
            path = os.path.join(ImageManager.instance().getDirectoryForType("DYNAMIPS"), path)
            if not os.path.isfile(path):
                return None
        try:
            md5sum = Dynamips._md5sum(path)
            log.debug("Get idlePC for %s. md5sum %s", path, md5sum)
            if md5sum in DEFAULT_IDLEPC:
                log.debug("IDLEPC found for %s", path)
                return DEFAULT_IDLEPC[md5sum]
        except OSError:
            return None

    @staticmethod
    def _md5sum(path):
        with open(path, "rb") as fd:
            m = hashlib.md5()
            while True:
                data = fd.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, DYNAMIPS_SETTINGS)
        if not os.path.exists(self._settings["dynamips_path"]):
            dynamips_path = shutil.which("dynamips")
            if dynamips_path:
                self._settings["dynamips_path"] = os.path.abspath(dynamips_path)
            else:
                self._settings["dynamips_path"] = ""

        self._loadIOSRouters()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        # save some settings to the local server config file
        server_settings = {
            "allocate_aux_console_ports": self._settings["allocate_aux_console_ports"],
            "ghost_ios_support": self._settings["ghost_ios_support"],
            "sparse_memory_support": self._settings["sparse_memory_support"],
            "mmap_support": self._settings["mmap_support"],
        }

        if self._settings["dynamips_path"]:
            server_settings["dynamips_path"] = os.path.normpath(self._settings["dynamips_path"])
        config = LocalServerConfig.instance()
        config.saveSettings(self.__class__.__name__, server_settings)

    def _loadIOSRouters(self):
        """
        Load the IOS routers from the persistent settings file.
        """

        settings = LocalConfig.instance().settings()
        if "routers" in settings.get(self.__class__.__name__, {}):
            for router in settings[self.__class__.__name__]["routers"]:
                name = router.get("name")
                server = router.get("server")
                router["image"] = router.get("path", router["image"])  # for backward compatibility before version 1.3
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._ios_routers or not name or not server:
                    continue
                router_settings = IOS_ROUTER_SETTINGS.copy()
                router_settings.update(router)
                # for backward compatibility before version 1.4
                if "symbol" not in router_settings:
                    router_settings["symbol"] = router_settings["default_symbol"]
                    router_settings["symbol"] = router_settings["symbol"][:-11] + ".svg" if router_settings["symbol"].endswith("normal.svg") else router_settings["symbol"]
                self._ios_routers[key] = router_settings

    def _saveIOSRouters(self):
        """
        Saves the IOS routers to the persistent settings file.
        """

        self._settings["routers"] = list(self._ios_routers.values())
        self._saveSettings()

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

    def VMs(self):
        """
        Returns IOS routers settings.

        :returns: IOS routers settings (dictionary)
        """

        return self._ios_routers

    def setVMs(self, new_ios_routers):
        """
        Sets IOS images settings.

        :param new_ios_routers: IOS images settings (dictionary)
        """

        self._ios_routers = new_ios_routers.copy()
        self._saveIOSRouters()

    @staticmethod
    def vmConfigurationPage():
        from .pages.ios_router_configuration_page import IOSRouterConfigurationPage
        return IOSRouterConfigurationPage

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
        :param project: Project instance
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

        log.info("configuring node {}".format(node))

        if isinstance(node, Router):
            ios_router = None
            if node_name:
                for ios_key, info in self._ios_routers.items():
                    if node_name == info["name"]:
                        ios_router = self._ios_routers[ios_key]
                        break

            if not ios_router:
                raise ModuleError("No IOS router for platform {}".format(node.settings()["platform"]))

            vm_settings = {}
            for setting_name, value in ios_router.items():
                if setting_name in node.settings() and setting_name != "name" and value != "" and value is not None:
                    vm_settings[setting_name] = value

            default_name_format = IOS_ROUTER_SETTINGS["default_name_format"]
            if ios_router["default_name_format"]:
                default_name_format = ios_router["default_name_format"]

            # Older GNS3 versions may have the following invalid settings in the VM template
            if "console" in vm_settings:
                del vm_settings["console"]
            if "sensors" in vm_settings:
                del vm_settings["sensors"]
            if "power_supplies" in vm_settings:
                del vm_settings["power_supplies"]

            ram = vm_settings.pop("ram")
            image = vm_settings.pop("image", None)
            if image is None:
                raise ModuleError("No IOS image has been associated with this IOS router")
            node.setup(image, ram, additional_settings=vm_settings, default_name_format=default_name_format)
        else:
            node.setup()

    def updateImageIdlepc(self, image_path, idlepc):
        """
        Updates the Idle-PC for an IOS image.

        :param image_path: path to the IOS image
        :param idlepc: Idle-PC value
        """

        for ios_router in self._ios_routers.values():
            if os.path.basename(ios_router["image"]) == image_path:
                if ios_router["idlepc"] != idlepc:
                    ios_router["idlepc"] = idlepc
                    log.info("Idle-PC value {} saved into '{}' template".format(idlepc, ios_router["name"]))
                    self._saveIOSRouters()

    def reset(self):
        """
        Resets the module.
        """

        log.info("Dynamips module reset")
        self._nodes.clear()

    def exportConfigs(self, directory):
        """
        Exports all configs for all nodes to a directory.

        :param directory: destination directory path
        """

        for node in self._nodes:
            if isinstance(node, Router) and node.initialized():
                node.exportConfigToDirectory(directory)

    def importConfigs(self, directory):
        """
        Imports configs to all nodes from a directory.

        :param directory: source directory path
        """

        for node in self._nodes:
            if isinstance(node, Router) and node.initialized():
                node.importConfigFromDirectory(directory)

    def findAlternativeIOSImage(self, image, node):
        """
        Tries to find an alternative IOS image.

        :param image: image name
        :param node: requesting Node instance

        :return: IOS image (dictionary)
        """

        if image in self._ios_images_cache:
            return self._ios_images_cache[image]

        from gns3.main_window import MainWindow
        mainwindow = MainWindow.instance()
        ios_routers = self.VMs()
        candidate_ios_images = {}
        alternative_image = {"image": image,
                             "ram": None,
                             "idlepc": None}

        # find all images with the same platform and local server
        for ios_router in ios_routers.values():
            if ios_router["platform"] == node.settings()["platform"] and ios_router["server"] == "local":
                if "chassis" in node.settings() and ios_router["chassis"] != node.settings()["chassis"]:
                    # continue to look if the chassis is not compatible
                    continue
                candidate_ios_images[ios_router["image"]] = ios_router

        if candidate_ios_images:
            selection, ok = QtWidgets.QInputDialog.getItem(mainwindow,
                                                           "IOS image", "IOS image {} could not be found\nPlease select an alternative from your existing images:".format(image),
                                                           list(candidate_ios_images.keys()), 0, False)
            if ok:
                candidate = candidate_ios_images[selection]
                alternative_image["image"] = candidate["image"]
                alternative_image["ram"] = candidate["ram"]
                alternative_image["idlepc"] = candidate["idlepc"]
                self._ios_images_cache[image] = alternative_image
                return alternative_image

        # no registered IOS image is used, let's just ask for an IOS image path
        msg = "Could not find the {} IOS image \nPlease select a similar IOS image!".format(image)
        log.error(msg)
        QtWidgets.QMessageBox.critical(mainwindow, "IOS image", msg)
        from .pages.ios_router_preferences_page import IOSRouterPreferencesPage
        image_path = IOSRouterPreferencesPage.getIOSImage(mainwindow, None)
        if image_path:
            alternative_image["image"] = image_path
            self._ios_images_cache[image] = alternative_image
        return alternative_image

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

        return [C1700, C2600, C2691, C3600, C3725, C3745, C7200, EtherSwitchRouter, EthernetSwitch, EthernetHub, FrameRelaySwitch, ATMSwitch]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        nodes = []
        for node_class in [EthernetSwitch, EthernetHub, FrameRelaySwitch, ATMSwitch]:
            nodes.append(
                {"class": node_class.__name__,
                 "name": node_class.symbolName(),
                 "categories": node_class.categories(),
                 "symbol": node_class.defaultSymbol(),
                 "builtin": True}
            )

        for ios_router in self._ios_routers.values():
            node_class = PLATFORM_TO_CLASS[ios_router["platform"]]
            nodes.append(
                {"class": node_class.__name__,
                 "name": ios_router["name"],
                 "ram": ios_router["ram"],
                 "server": ios_router["server"],
                 "symbol": ios_router["symbol"],
                 "categories": [ios_router["category"]]}
            )

        return nodes

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.dynamips_preferences_page import DynamipsPreferencesPage
        from .pages.ios_router_preferences_page import IOSRouterPreferencesPage
        return [DynamipsPreferencesPage, IOSRouterPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Dynamips.

        :returns: instance of Dynamips
        """

        if not hasattr(Dynamips, "_instance"):
            Dynamips._instance = Dynamips()
        return Dynamips._instance
