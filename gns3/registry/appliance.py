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
import collections.abc
import jsonschema


from gns3.utils.get_resource import get_resource


class ApplianceError(Exception):
    pass


class Appliance(collections.abc.Mapping):

    def __init__(self, registry, path):
        """
        :params registry: Instance of the registry where images are located
        :params path: Path of the appliance file on disk or file content
        """
        self._registry = registry

        if os.path.isabs(path):
            try:
                with open(path, encoding="utf-8") as f:
                    self._appliance = json.load(f)
            except (OSError, ValueError) as e:
                raise ApplianceError("Could not read appliance {}: {}".format(os.path.abspath(path), str(e)))
        else:
            try:
                self._appliance = json.loads(path)
            except ValueError as e:
                raise ApplianceError("Could not read appliance {}: {}".format(os.path.abspath(path), str(e)))
        self._check_config()
        self._resolve_version()

    def _check_config(self):
        """
        :param appliance: Sanity check on the appliance configuration
        """
        if "registry_version" not in self._appliance:
            raise ApplianceError("Invalid appliance configuration please report the issue on https://github.com/GNS3/gns3-registry")
        if self._appliance["registry_version"] > 6:
            raise ApplianceError("Please update GNS3 in order to install this appliance")

        with open(get_resource(os.path.join("schemas", "appliance.json"))) as f:
            schema = json.load(f)
        v = jsonschema.Draft4Validator(schema)
        try:
            v.validate(self._appliance)
        except jsonschema.ValidationError as e:
            error = jsonschema.exceptions.best_match(v.iter_errors(self._appliance)).message
            raise ApplianceError("Invalid appliance file: {}".format(error))

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

        if "versions" not in self._appliance:
            return

        for version in self._appliance["versions"]:
            for image_type, filename in version["images"].items():

                found = False

                for file in self._appliance["images"]:
                    file = copy.copy(file)

                    if "idlepc" in version:
                        file["idlepc"] = version["idlepc"]

                    if "/" in filename:
                        parent = filename.split("/")[0]
                        name = filename.split("/")[-1:][0]
                        filename = os.path.join(parent, name)
                    else:
                        parent = filename

                    if file["filename"] == parent:
                        file["filename"] = filename
                        version["images"][image_type] = file
                        found = True
                        break

                if not found:
                    raise ApplianceError("Broken appliance missing file {} for version {}".format(filename, version["name"]))

    def create_new_version(self, new_version):
        """
        Duplicate a version in order to create a new version
        """

        if "versions" not in self._appliance.keys() or not self._appliance["versions"]:
            raise ApplianceError("Your appliance file doesn't contain any versions")
        self._appliance["versions"].append(new_version)

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
                appliance["images"] = []
                for image_type, image in version["images"].items():
                    image["type"] = image_type

                    img = self._registry.search_image_file(self.emulator(), image["filename"], image.get("md5sum"), image.get("filesize"))
                    if img is None:
                        if "md5sum" in image:
                            raise ApplianceError("File {} with checksum {} not found for {}".format(image["filename"], image["md5sum"], appliance["name"]))
                        else:
                            raise ApplianceError("File {} not found for {}".format(image["filename"], appliance["name"]))

                    image["path"] = img.path
                    image["location"] = img.location

                    if "md5sum" not in image:
                        image["md5sum"] = img.md5sum
                        image["filesize"] = img.filesize

                    appliance["images"].append(image)
                    found = True
                appliance["name"] = "{} {}".format(appliance["name"], version_name)
                break

        if not found:
            raise ApplianceError("Version {} not found for {}".format(version_name, appliance["name"]))

        return appliance

    def copy(self):
        """
        Get a copy of the appliance
        """
        return copy.deepcopy(self._appliance)

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

    def emulator(self):
        if "qemu" in self._appliance:
            return "qemu"
        if "iou" in self._appliance:
            return "iou"
        return "dynamips"
