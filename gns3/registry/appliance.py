#!/usr/bin/env python
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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


import json
import copy
import os
import collections


class ApplianceError(Exception):
    pass


class Appliance(collections.Mapping):

    def __init__(self, registry, path):
        """
        :params registry: Instance of the registry where images are located
        :params path: Path of the appliance file on disk
        """
        self._registry = registry

        try:
            with open(path, encoding="utf-8") as f:
                self._appliance = json.load(f)
        except (OSError, ValueError) as e:
            raise ApplianceError("Could not read appliance {}: {}".format(os.path.abspath(path), str(e)))
        self._check_config()
        self._resolve_version()

    def _check_config(self):
        """
        :param appliance: Sanity check on the appliance configuration
        """
        if "registry_version" not in self._appliance:
            raise ApplianceError("Invalid appliance configuration please report the issue on https://github.com/GNS3/gns3-registry")
        if self._appliance["registry_version"] > 2:
            raise ApplianceError("Please update GNS3 in order to install this appliance")

    def __getitem__(self, key):
        return self._appliance.__getitem__(key)

    def __iter__(self):
        return self._appliance.__iter__()

    def __len__(self):
        return self._appliance.__len__()

    def _resolve_version(self):
        """
        Replace image field in versions by their the complete information from images
        """

        for version in self._appliance["versions"]:
            for image_type, filename in version["images"].items():

                found = False

                for file in self._appliance["images"]:
                    file = copy.copy(file)

                    if "idlepc" in version:
                        file["idlepc"] = version["idlepc"]

                    if "/" in filename:
                        parent, name = filename.split("/")
                        filename = os.path.join(parent, name)
                    else:
                        parent = filename

                    if file["filename"] == parent:
                        file["filename"] = filename
                        version["images"][image_type] = file
                        found = True
                        break

                if not found:
                    raise ApplianceError("Broken appliance missing file {} for version {}".format(filename, version["name"]))

    def search_images_for_version(self, version_name):
        """
        Search on disk the images required by this version.
        And keep only the require images in the images fields. Add to the images
        their disk type and path.

        :param version_name: Version name
        :returns: Appliance with only require images
        """

        found = False
        appliance = copy.deepcopy(self._appliance)
        for version in appliance["versions"]:
            if version["name"] == version_name:
                appliance["name"] = "{} {}".format(appliance["name"], version["name"])
                appliance["images"] = []
                for image_type, image in version["images"].items():
                    image["type"] = image_type
                    image["path"] = self._registry.search_image_file(image["filename"], image["md5sum"], image["filesize"])
                    if image["path"] is None:
                        raise ApplianceError("File {} with checksum {} not found for {}".format(image["filename"], image["md5sum"], appliance["name"]))

                    appliance["images"].append(image)
                    found = True
                break

        if not found:
            raise ApplianceError("Version {} not found for {}".format(version_name, appliance["name"]))

        return appliance

    def is_version_installable(self, version):
        """
        Search on disk if a version is available for this appliance

        :params version: Version name
        :returns: Boolean true if installable
        """

        try:
            self.search_images_for_version(version)
            return True
        except ApplianceError:
            return False

    def image_dir_name(self):
        """
        :returns: The name of directory where image should be located
        """
        if "qemu" in self._appliance:
            return "QEMU"
        if "iou" in self._appliance:
            return "IOU"
        return "IOS"

