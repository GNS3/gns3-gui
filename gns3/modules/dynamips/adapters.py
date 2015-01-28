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
Adapter matrix to create Port objects with the correct parameters.
"""

from gns3.ports.atm_port import ATMPort
from gns3.ports.ethernet_port import EthernetPort
from gns3.ports.fastethernet_port import FastEthernetPort
from gns3.ports.gigabitethernet_port import GigabitEthernetPort
from gns3.ports.pos_port import POSPort
from gns3.ports.serial_port import SerialPort


ADAPTER_MATRIX = {"C1700-MB-1FE": {"nb_ports": 1,
                                   "wics": 2,
                                   "port": FastEthernetPort},

                  "C1700-MB-WIC1": {"nb_ports": 0,
                                    "wics": 2},

                  "C2600-MB-1E": {"nb_ports": 1,
                                  "wics": 3,
                                  "port": EthernetPort},

                  "C2600-MB-1FE": {"nb_ports": 1,
                                   "wics": 3,
                                   "port": FastEthernetPort},

                  "C2600-MB-2E": {"nb_ports": 2,
                                  "wics": 3,
                                  "port": EthernetPort},

                  "C2600-MB-2FE": {"nb_ports": 2,
                                   "wics": 3,
                                   "port": FastEthernetPort},

                  "C7200-IO-2FE": {"nb_ports": 2,
                                   "wics": 0,
                                   "port": FastEthernetPort},

                  "C7200-IO-FE": {"nb_ports": 1,
                                  "wics": 0,
                                  "port": FastEthernetPort},

                  "C7200-IO-GE-E": {"nb_ports": 1,
                                    "wics": 0,
                                    "port": GigabitEthernetPort},

                  "GT96100-FE": {"nb_ports": 2,
                                 "wics": 3,
                                 "port": FastEthernetPort},

                  "Leopard-2FE": {"nb_ports": 2,
                                  "wics": 0,
                                  "port": FastEthernetPort},

                  "NM-16ESW": {"nb_ports": 16,
                               "wics": 0,
                               "port": FastEthernetPort},

                  "NM-1E": {"nb_ports": 1,
                            "wics": 0,
                            "port": EthernetPort},

                  "NM-1FE-TX": {"nb_ports": 1,
                                "wics": 0,
                                "port": FastEthernetPort},

                  "NM-4E": {"nb_ports": 4,
                            "wics": 0,
                            "port": EthernetPort},

                  "NM-4T": {"nb_ports": 4,
                            "wics": 0,
                            "port": SerialPort},

                  "PA-2FE-TX": {"nb_ports": 2,
                                "wics": 0,
                                "port": FastEthernetPort},

                  "PA-4E": {"nb_ports": 4,
                            "wics": 0,
                            "port": EthernetPort},

                  "PA-4T+": {"nb_ports": 4,
                             "wics": 0,
                             "port": SerialPort},

                  "PA-8E": {"nb_ports": 8,
                            "wics": 0,
                            "port": EthernetPort},

                  "PA-8T": {"nb_ports": 8,
                            "wics": 0,
                            "port": SerialPort},

                  "PA-A1": {"nb_ports": 1,
                            "wics": 0,
                            "port": ATMPort},

                  "PA-FE-TX": {"nb_ports": 1,
                               "wics": 0,
                               "port": FastEthernetPort},

                  "PA-GE": {"nb_ports": 1,
                            "wics": 0,
                            "port": GigabitEthernetPort},

                  "PA-POS-OC3": {"nb_ports": 1,
                                 "wics": 0,
                                 "port": POSPort},
                  }
