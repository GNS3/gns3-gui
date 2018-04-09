# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundationeither version 3 of the Licenseor
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If notsee <http://www.gnu.org/licenses/>.

"""
Adapter matrix to create Port objects with the correct parameters.
"""

ADAPTER_MATRIX = {
    "C1700-MB-1FE": {"nb_ports": 1,
                     "wics": 2},
    "C1700-MB-WIC1": {"nb_ports": 0,
                      "wics": 2},
    "C2600-MB-1E": {"nb_ports": 1,
                    "wics": 3},
    "C2600-MB-1FE": {"nb_ports": 1,
                     "wics": 3},
    "C2600-MB-2E": {"nb_ports": 2,
                    "wics": 3},
    "C2600-MB-2FE": {"nb_ports": 2,
                     "wics": 3},
    "C7200-IO-2FE": {"nb_ports": 2,
                     "wics": 0},
    "C7200-IO-FE": {"nb_ports": 1,
                    "wics": 0},
    "C7200-IO-GE-E": {"nb_ports": 1,
                      "wics": 0},
    "GT96100-FE": {"nb_ports": 2,
                   "wics": 3},
    "Leopard-2FE": {"nb_ports": 2,
                    "wics": 0},
    "NM-16ESW": {"nb_ports": 16,
                 "wics": 0},
    "NM-1E": {"nb_ports": 1,
              "wics": 0},
    "NM-1FE-TX": {"nb_ports": 1,
                  "wics": 0},
    "NM-4E": {"nb_ports": 4,
              "wics": 0},
    "NM-4T": {"nb_ports": 4,
              "wics": 0},
    "PA-2FE-TX": {"nb_ports": 2,
                  "wics": 0},
    "PA-4E": {"nb_ports": 4,
              "wics": 0},
    "PA-4T+": {"nb_ports": 4,
               "wics": 0},
    "PA-8E": {"nb_ports": 8,
              "wics": 0},
    "PA-8T": {"nb_ports": 8,
              "wics": 0},
    "PA-A1": {"nb_ports": 1,
              "wics": 0},
    "PA-FE-TX": {"nb_ports": 1,
                 "wics": 0},
    "PA-GE": {"nb_ports": 1,
              "wics": 0},
    "PA-POS-OC3": {"nb_ports": 1,
                   "wics": 0},
}
