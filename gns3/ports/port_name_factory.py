#!/usr/bin/env python
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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

import logging
log = logging.getLogger(__name__)


class StandardPortNameFactory:
    """
    Generate default port names.
    """

    def __new__(cls, ethernet_adapters, first_port_name, port_name_format, port_segment_size):
        ports = []
        adapter_number = interface_number = segment_number = 0

        for adapter_number in range(adapter_number, ethernet_adapters + adapter_number):
            if first_port_name and adapter_number == 0:
                port_name = first_port_name
            else:
                port_name = port_name_format.format(interface_number,
                                                    segment_number,
                                                    adapter=adapter_number,
                                                    **cls._generate_replacement(interface_number, segment_number))
                interface_number += 1
                if port_segment_size:
                    if interface_number % port_segment_size == 0:
                        segment_number += 1
                        interface_number = 0
                else:
                    segment_number += 1
            ports.append(port_name)
        return ports

    @staticmethod
    def _generate_replacement(interface_number, segment_number):
        """
        This will generate replacement string for
        {port0} => {port9}
        {segment0} => {segment9}
        """

        replacements = {}
        for i in range(0, 9):
            replacements["port" + str(i)] = interface_number + i
            replacements["segment" + str(i)] = segment_number + i
        return replacements
