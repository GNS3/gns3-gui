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
import os
import platform
import struct
import distro

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_SDK_AVAILABLE = True
except ImportError:
    # Sentry SDK is not installed with deb package in order to simplify packaging
    SENTRY_SDK_AVAILABLE = False

from .version import __version__, __version_info__

import logging
log = logging.getLogger(__name__)


# Dev build
if __version_info__[3] != 0:
    import faulthandler
    # Display a traceback in case of segfault crash. Usefull when frozen
    # Not enabled by default for security reason
    log.debug("Enable catching segfault")
    faulthandler.enable()


class CrashReport:

    """
    Report crash to a third party service
    """

    DSN = "https://4c7f622318895db756d831ed45f65940@o19455.ingest.us.sentry.io/38506"
    _instance = None

    def __init__(self):
        # We don't want sentry making noise if an error is caught when we don't have internet
        sentry_errors = logging.getLogger('sentry.errors')
        sentry_errors.disabled = True

        sentry_uncaught = logging.getLogger('sentry.errors.uncaught')
        sentry_uncaught.disabled = True
        self._sentry_initialized = False

        if SENTRY_SDK_AVAILABLE:
            # Don't send log records as events.
            sentry_logging = LoggingIntegration(level=logging.INFO, event_level=None)
            try:
                sentry_sdk.init(dsn=CrashReport.DSN,
                                release=__version__,
                                default_integrations=False,
                                integrations=[sentry_logging])
            except Exception as e:
                log.error("Crash report could not be sent: {}".format(e))
                return

            tags = {
                "os:name": platform.system(),
                "os:release": platform.release(),
                "os:win_32": " ".join(platform.win32_ver()),
                "os:mac": "{} {}".format(platform.mac_ver()[0], platform.mac_ver()[2]),
                "os:linux": distro.name(pretty=True),

            }

            self._add_qt_information(tags)

            with sentry_sdk.configure_scope() as scope:
                for key, value in tags.items():
                    scope.set_tag(key, value)

            extra_context = {
                "python:version": "{}.{}.{}".format(sys.version_info[0],
                                                    sys.version_info[1],
                                                    sys.version_info[2]),
                "python:bit": struct.calcsize("P") * 8,
                "python:encoding": sys.getdefaultencoding(),
                "python:frozen": "{}".format(hasattr(sys, "frozen"))
            }

            # extra controller and compute information
            from .controller import Controller
            from .compute_manager import ComputeManager
            extra_context["controller:version"] = Controller.instance().version()
            extra_context["controller:host"] = Controller.instance().host()
            extra_context["controller:connected"] = Controller.instance().connected()

            for index, compute in enumerate(ComputeManager.instance().computes()):
                extra_context["compute{}:id".format(index)] = compute.id()
                extra_context["compute{}:name".format(index)] = compute.name(),
                extra_context["compute{}:host".format(index)] = compute.host(),
                extra_context["compute{}:connected".format(index)] = compute.connected()
                extra_context["compute{}:platform".format(index)] = compute.capabilities().get("platform")
                extra_context["compute{}:version".format(index)] = compute.capabilities().get("version")

            with sentry_sdk.configure_scope() as scope:
                for key, value in extra_context.items():
                    scope.set_extra(key, value)

    def captureException(self, exception, value, tb):

        from .local_server import LocalServer
        from .local_config import LocalConfig

        local_server = LocalServer.instance().localServerSettings()
        if local_server["report_errors"]:

            if not SENTRY_SDK_AVAILABLE:
                log.warning("Cannot capture exception: Sentry SDK is not available")
                return

            if os.path.exists(LocalConfig.instance().runAsRootPath()):
                log.warning("User is running application as root. Crash reports disabled.")
                return

            if not hasattr(sys, "frozen") and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".git")):
                log.warning(".git directory detected, crash reporting is turned off for developers.")
                return

            try:
                error = (exception, value, tb)
                sentry_sdk.capture_exception(error=error)
                log.info("Crash report sent with event ID: {}".format(sentry_sdk.last_event_id()))
            except Exception as e:
                log.warning("Can't send crash report to Sentry: {}".format(e))

    def _add_qt_information(self, tags):

        try:
            from .qt import QtCore
            from .qt import sip
        except ImportError:
            return tags
        tags["pyqt:version"] = QtCore.PYQT_VERSION_STR
        tags["qt:version"] = QtCore.QT_VERSION_STR
        tags["sip:version"] = sip.SIP_VERSION_STR
        return tags

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = CrashReport()
        return cls._instance
