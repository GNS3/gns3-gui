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
WICS matrix to create Port objects with the correct parameters.
"""

from gns3.ports.ethernet_port import EthernetPort
from gns3.ports.serial_port import SerialPort

WIC_MATRIX = {"WIC-1ENET": {"nb_ports": 1,
                            "port": EthernetPort},

              "WIC-1T": {"nb_ports": 1,
                         "port": SerialPort},

              "WIC-2T": {"nb_ports": 2,
                         "port": SerialPort}
              }
