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

import raven
import json

from .version import __version__
from .servers import Servers

import logging
log = logging.getLogger(__name__)


class CrashReport:

    """
    Report crash to a third party service
    """

    DSN = "https://399087fc600b4a2984874af1cd57124c:a0f8323c923f4246917699c9519f2ff2@app.getsentry.com/38506"
    _instance = None

    def __init__(self):
        self._client = None

    def captureException(self, exception, value, tb):
        local_server = Servers.instance().localServerSettings()
        if local_server["report_errors"]:
            if self._client is None:
                self._client = raven.Client(CrashReport.DSN, release=__version__)
            self._client.captureException((exception, value, tb))

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = CrashReport()
        return cls._instance
