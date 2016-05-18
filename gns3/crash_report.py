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

import sys
import psutil
import os
import platform
import struct

try:
    import raven
    RAVEN_AVAILABLE = True
except ImportError:
    # raven is not installed with deb package in order to simplify packaging
    RAVEN_AVAILABLE = False

from .utils.get_resource import get_resource
from .version import __version__, __version_info__

import logging
log = logging.getLogger(__name__)


# Dev build
if __version_info__[3] != 0:
    import faulthandler
    # Display a traceback in case of segfault crash. Usefull when frozen
    # Not enabled by default for security reason
    log.info("Enable catching segfault")
    faulthandler.enable()


class CrashReport:

    """
    Report crash to a third party service
    """

    DSN = "sync+https://03a292b244b941d9abee28365c999972:038f2bb8fc9145468c3428b17e5f1e44@app.getsentry.com/38506"
    if hasattr(sys, "frozen"):
        cacert = get_resource("cacert.pem")
        if cacert is not None and os.path.isfile(cacert):
            DSN += "?ca_certs={}".format(cacert)
        else:
            log.warning("The SSL certificate bundle file '{}' could not be found".format(cacert))
    _instance = None

    def __init__(self):
        # We don't want sentry making noise if an error is catched when you don't have internet
        sentry_errors = logging.getLogger('sentry.errors')
        sentry_errors.disabled = True

        sentry_uncaught = logging.getLogger('sentry.errors.uncaught')
        sentry_uncaught.disabled = True

    def captureException(self, exception, value, tb):
        from .servers import Servers

        local_server = Servers.instance().localServerSettings()
        if local_server["report_errors"]:
            if not RAVEN_AVAILABLE:
                return
            if os.path.exists(".git"):
                log.warning("A .git directory exist crash report is turn off for developers")
                return

            if hasattr(exception, "fingerprint"):
                client = raven.Client(CrashReport.DSN, release=__version__, fingerprint=['{{ default }}', exception.fingerprint])
            else:
                client = raven.Client(CrashReport.DSN, release=__version__)
            context = {
                "os:name": platform.system(),
                "os:release": platform.release(),
                "os:win_32": " ".join(platform.win32_ver()),
                "os:mac": "{} {}".format(platform.mac_ver()[0], platform.mac_ver()[2]),
                "os:linux": " ".join(platform.linux_distribution()),
                "python:version": "{}.{}.{}".format(sys.version_info[0],
                                                    sys.version_info[1],
                                                    sys.version_info[2]),
                "python:bit": struct.calcsize("P") * 8,
                "python:encoding": sys.getdefaultencoding(),
                "python:frozen": "{}".format(hasattr(sys, "frozen"))
            }
            context = self._add_qt_information(context)
            client.tags_context(context)
            try:
                report = client.captureException((exception, value, tb))
            except Exception as e:
                log.error("Can't send crash report to Sentry: {}".format(e))
                return
            log.info("Crash report sent with event ID: {}".format(client.get_ident(report)))

    def _add_qt_information(self, context):
        try:
            from .qt import QtCore
            import sip
        except ImportError:
            return context
        context["psutil:version"] = psutil.__version__
        context["pyqt:version"] = QtCore.PYQT_VERSION_STR
        context["qt:version"] = QtCore.QT_VERSION_STR
        context["sip:version"] = sip.SIP_VERSION_STR
        return context

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = CrashReport()
        return cls._instance
