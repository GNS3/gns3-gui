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
import uuid

from hashlib import md5
from urllib.request import urlopen
from urllib.parse import quote
from ..qt import QtCore
from ..version import __version__


class AnalyticsClient(object):

    """
    Google analytics client to send events.
    """

    _property_id = "UA-55817127-1"
    _visitor_id = None
    _user_agent = "GNS3 {} on {}".format(__version__, platform.system())

    def _generate_visitor_id(self):

        rstring = self._user_agent + str(uuid.uuid4())
        md5_string = md5(rstring.encode()).hexdigest()
        return "0x{}".format(md5_string[:16])

    def send_event(self, category, action, label, value=None):

        if not self._visitor_id:
            self._visitor_id = self._generate_visitor_id()

        url = "http://www.google-analytics.com/__utm.gif?utmwv=5.3.6&utmac={property}" \
            "&utmcc=__utma%3D999.999.999.999.999.1%3B&utmvid={visitor}&utmt=event&" \
            "utme=5%28{category}*{action}*{label}%29".format(property=self._property_id,
                                                             visitor=self._visitor_id,
                                                             category=quote(category),
                                                             action=quote(action),
                                                             label=quote(label))

        if value is not None:
            url += "%28{value}%29".format(value=value)

        locale = QtCore.QLocale.system().name().lower()
        if locale:
            url += "&utmul={}".format(locale)

        try:
            urlopen(url, timeout=3)
        except Exception:
            pass

if __name__ == '__main__':
    client = AnalyticsClient()
    client.send_event("Windows installer", "Install", __version__)
