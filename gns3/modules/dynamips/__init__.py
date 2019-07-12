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

from gns3.local_config import LocalConfig
from gns3.image_manager import ImageManager
from gns3.local_server_config import LocalServerConfig
from gns3.controller import Controller
from gns3.template_manager import TemplateManager
from gns3.template import Template

from ..module import Module
from .nodes.router import Router
from .nodes.c1700 import C1700
from .nodes.c2600 import C2600
from .nodes.c2691 import C2691
from .nodes.c3600 import C3600
from .nodes.c3725 import C3725
from .nodes.c3745 import C3745
from .nodes.c7200 import C7200
from .nodes.etherswitch_router import EtherSwitchRouter
from .settings import DYNAMIPS_SETTINGS, IOS_ROUTER_SETTINGS
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
        self._loadSettings()

    @staticmethod
    def getDefaultIdlePC(path):
        """
        Returns the default IDLE PC for an image if the image
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
        """
        Calculate MD5 checksum for image.

        :param path: image path
        :returns: MD5 checksum
        """

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

        # migrate router settings to the controller (templates are managed on server side starting with version 2.0)
        Controller.instance().connected_signal.connect(self._migrateOldRouters)

    def _migrateOldRouters(self):
        """
        Migrate local router settings to the controller.
        """

        if self._settings.get("routers"):
            templates = []
            for router in self._settings.get("routers"):
                router_settings = IOS_ROUTER_SETTINGS.copy()
                router_settings.update(router)
                if router_settings.get("chassis"):
                    del router_settings["chassis"]
                templates.append(Template(router_settings))
            TemplateManager.instance().updateList(templates)
            self._settings["routers"] = []
            self._saveSettings()

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

    def updateImageIdlepc(self, image_path, idlepc):
        """
        Updates the Idle-PC for an IOS image.

        :param image_path: path to the IOS image
        :param idlepc: Idle-PC value
        """

        for template in TemplateManager.instance().templates().values():
            if template.template_type() == "dynamips":
                template_settings = template.settings()
                router_image = template_settings.get("image")
                old_idlepc = template_settings.get("idlepc")
                if os.path.basename(router_image) == image_path and old_idlepc != idlepc:
                    template_settings["idlepc"] = idlepc
                    template.setSettings(template_settings)
                    log.debug("Idle-PC value {} saved into '{}' template".format(idlepc, template.name()))
                    TemplateManager.instance().updateTemplate(template)

    @staticmethod
    def configurationPage():
        """
        Returns the configuration page for this module.

        :returns: QWidget object
        """

        from .pages.ios_router_configuration_page import IOSRouterConfigurationPage
        return IOSRouterConfigurationPage

    @staticmethod
    def getNodeClass(node_type, platform=None):
        """
        Returns the class corresponding to node type.

        :param node_type: node type (string)
        :param platform: Dynamips platform

        :returns: class or None
        """

        if node_type == "dynamips":
            return PLATFORM_TO_CLASS[platform]
        return None

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [C1700, C2600, C2691, C3600, C3725, C3745, C7200, EtherSwitchRouter]

    @staticmethod
    def preferencePages():
        """
        Returns the preference pages for this module.

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

    def __str__(self):
        """
        Returns the module name.
        """

        return "dynamips"
