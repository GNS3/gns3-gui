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


import platform
import sys
from datetime import datetime

from urllib.parse import quote
from ..version import __version__
from ..qt import QtCore, QtNetwork, QtWidgets
from ..local_config import LocalConfig
from ..settings import GENERAL_SETTINGS

import logging
log = logging.getLogger(__name__)


class AnalyticsClient(QtCore.QObject):
    """
    Google analytics client to send events.
    """

    _property_id = "UA-55817127-3"

    def __init__(self):
        super().__init__()
        self._visitor_id = None
        self._manager = QtNetwork.QNetworkAccessManager(self)

        def finished(network_reply):
            try:
                error = network_reply.error()
            except TypeError:
                # For unknow reason sometimes error is transform to a signal
                # we receive few crash report about that, but we are not able
                # to reproduce. We suspect the problem happen when the
                # application is closing.
                #
                # https://github.com/GNS3/gns3-gui/issues/2011
                return
            if error != QtNetwork.QNetworkReply.NoError:
                log.debug("Error when pushing to Google Analytics %s", network_reply.errorString())

        self._manager.finished.connect(finished)

        #
        # We need to build a user agent for Universal Analytics in order to
        # let analytics guess the OS
        # this could break by analytics at anytime :(
        if sys.platform.startswith("darwin"):
            self._user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X {release}) AppleWebKit/537.36 (KHTML, like Gecko) GNS3/{version}".format(release=platform.mac_ver()[0].replace(".", "_"), version=__version__)
        elif sys.platform.startswith("win"):
            self._user_agent = "Mozilla/5.0 (Windows NT {release}) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 GNS3/{version}".format(release=platform.release(), version=__version__)
        else:
            self._user_agent = "Mozilla/5.0 (X11; Linux {arch}) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36  GNS3/{version}".format(arch=platform.machine(), version=__version__)
        self._rate_limit = {}

    def sendScreenView(self, screen, session_start=None):
        """
        :params session_start: True session start, None during session, False session stop
        """

        if session_start is not False and screen in self._rate_limit:
            if self._rate_limit[screen] + 60 * 1 > datetime.utcnow().timestamp():
                log.debug("Ignore call %s to Google Analytics because of rate limiting", screen)
                return

        self._rate_limit[screen] = datetime.utcnow().timestamp()

        settings = LocalConfig.instance().loadSectionSettings("MainWindow", GENERAL_SETTINGS)
        if settings["send_stats"] is False:
            log.debug("Stats is turn off ignore call %s", screen)
            return

        body = "v=1"  # Version
        body += "&tid={}".format(self._property_id)  # Tracking ID / Property ID
        body += "&cid={}".format(settings["stats_visitor_id"])  # Anonymous Client ID
        body += "&aip=1"  # Anonymize IP
        body += "&t=screenview"  # Screenview hit type
        body += "&an=GNS3"  # App name
        body += "&av={}".format(quote(__version__))  # App version.
        body += "&ua={}".format(quote(self._user_agent))  # User agent
        body += "&cd={}".format(quote(screen))  # Category
        body += "&ds=gns3-gui"  # Data source
        if session_start is True:
            body += "&sc=start"  # Session start
        elif session_start is False:
            body += "&sc=end"  # Session end

        screen = QtWidgets.QApplication.desktop().screenGeometry()
        body += "&sr={}x{}".format(screen.width(), screen.height())  # Screen resolution

        locale = QtCore.QLocale.system().name().lower()
        if locale:
            body += "&ul={}".format(locale)  # User language

        # TODO: HTTPS when possible because it's broken for the moment with Qt on OSX:
        # https://bugreports.qt.io/browse/QTBUG-45487
        if sys.platform.startswith("darwin"):
            url = QtCore.QUrl('http://www.google-analytics.com/collect')
        else:
            url = QtCore.QUrl('https://www.google-analytics.com/collect')
        request_qt = QtNetwork.QNetworkRequest(url)
        request_qt.setRawHeader(b"Content-Type", b"application/x-www-form-urlencoded")
        request_qt.setRawHeader(b"User-Agent", self._user_agent.encode())
        self._manager.post(request_qt, body.encode())

        log.debug("Send stats to Google Analytics: %s", body)

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of AnalyticsClient.
        :returns: instance of AnalyticsClient
        """

        if not hasattr(AnalyticsClient, '_instance') or AnalyticsClient._instance is None:
            AnalyticsClient._instance = AnalyticsClient()
        return AnalyticsClient._instance
