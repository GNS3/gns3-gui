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
Base class (interface) for modules.
"""

from ..qt import QtCore
from ..local_config import LocalConfig

import logging
log = logging.getLogger(__name__)


class Module(QtCore.QObject):

    """
    Module interface.
    """

    notification_signal = QtCore.Signal(str, str)

    def __init__(self):

        super().__init__()
        LocalConfig.instance().config_changed_signal.connect(self.configChangedSlot)

    def configChangedSlot(self):
        """
        Call when the configuration file has changed
        """

        raise NotImplementedError("Missing configChangedSlot in {}".format(self.__class__.__name__))

    @staticmethod
    def nodes(self):
        """
        Returns all nodes supported by this module.
        Must be overloaded.

        :returns: list of node classes
        """

        raise NotImplementedError()

    @staticmethod
    def preferencePages():
        """
        Returns all the preference pages used by this module.
        Must be overloaded.

        :returns: list of preference page classes
        """

        raise NotImplementedError()
