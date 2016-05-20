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

import os
import shutil

from gns3.local_server import LocalServer

import logging
log = logging.getLogger(__name__)


def get_default_base_config(base_config_template_path):
    """
    Copy the default base config template to settings directory (if not already present) and returns the path.

    :param base_config_template_path: path to the base config template

    :return: path to the base config
    """

    config_dir = LocalServer.instance().localServerSettings()["configs_path"]
    if base_config_template_path:
        try:
            os.makedirs(config_dir, exist_ok=True)
        except OSError as e:
            log.error("could not create the base configs directory {}: {}".format(config_dir, e))
            return ""
        try:
            base_config_path = os.path.join(config_dir, os.path.basename(base_config_template_path))
            if not os.path.isfile(base_config_path):
                shutil.copyfile(base_config_template_path, base_config_path)
            return os.path.normpath(base_config_path)
        except OSError as e:
            log.error("could not copy {} to {}: {}".format(base_config_template_path, base_config_path, e))
    return ""
