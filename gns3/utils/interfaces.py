# -*- coding: utf-8 -*-
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


import sys
import socket
import psutil

if psutil.version_info < (3, 0, 0):
    raise Exception("psutil version should >= 3.0.0. If you are under Ubuntu/Debian install gns3 via apt instead of pip")

import logging
log = logging.getLogger(__name__)


def _get_windows_interfaces_from_registry():

    import winreg

    # HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces
    interfaces = []
    try:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkCards")
        for index in range(winreg.QueryInfoKey(hkey)[0]):
            network_card_id = winreg.EnumKey(hkey, index)
            hkeycard = winreg.OpenKey(hkey, network_card_id)
            guid, _ = winreg.QueryValueEx(hkeycard, "ServiceName")
            netcard, _ = winreg.QueryValueEx(hkeycard, "Description")
            connection = r"SYSTEM\CurrentControlSet\Control\Network\{4D36E972-E325-11CE-BFC1-08002BE10318}" + "\{}\Connection".format(guid)
            hkeycon = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, connection)
            name, _ = winreg.QueryValueEx(hkeycon, "Name")
            interface = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{}".format(guid)
            hkeyinterface = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interface)
            is_dhcp_enabled, _ = winreg.QueryValueEx(hkeyinterface, "EnableDHCP")
            if is_dhcp_enabled:
                ip_address, _ = winreg.QueryValueEx(hkeyinterface, "DhcpIPAddress")
                netmask, _ = winreg.QueryValueEx(hkeyinterface, "DhcpSubnetMask")
            else:
                ip_address, _ = winreg.QueryValueEx(hkeyinterface, "IPAddress")
                netmask, _ = winreg.QueryValueEx(hkeyinterface, "SubnetMask")
                if ip_address:
                    # get the first IPv4 address only
                    ip_address = ip_address[0]
            npf_interface = "\\Device\\NPF_{guid}".format(guid=guid)
            interfaces.append({"id": npf_interface,
                               "name": name,
                               "ip_address": ip_address,
                               "mac_address": "",  # TODO: find MAC address in registry
                               "netcard": netcard,
                               "netmask": netmask,
                               "type": "ethernet"})
            winreg.CloseKey(hkeyinterface)
            winreg.CloseKey(hkeycon)
            winreg.CloseKey(hkeycard)
        winreg.CloseKey(hkey)
    except OSError as e:
        log.error("could not read registry information: {}".format(e))

    return interfaces


def get_windows_interfaces():
    """
    Get Windows interfaces.

    :returns: list of windows interfaces
    """

    import pywintypes
    interfaces = []
    try:
        import win32com.client
        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = locator.ConnectServer(".", "root\cimv2")
        network_configs = service.InstancesOf("Win32_NetworkAdapterConfiguration")
        # more info on Win32_NetworkAdapter: http://msdn.microsoft.com/en-us/library/aa394216%28v=vs.85%29.aspx
        for adapter in service.InstancesOf("Win32_NetworkAdapter"):
            if adapter.NetConnectionStatus == 2 or adapter.NetConnectionStatus == 7:
                # adapter is connected or media disconnected
                ip_address = ""
                netmask = ""
                for network_config in network_configs:
                    if network_config.InterfaceIndex == adapter.InterfaceIndex:
                        if network_config.IPAddress:
                            # get the first IPv4 address only
                            ip_address = network_config.IPAddress[0]
                            netmask = network_config.IPSubnet[0]
                        break
                npf_interface = "\\Device\\NPF_{guid}".format(guid=adapter.GUID)
                interfaces.append({"id": npf_interface,
                                   "name": adapter.NetConnectionID,
                                   "ip_address": ip_address,
                                   "mac_address": adapter.MACAddress,
                                   "netcard": adapter.name,
                                   "netmask": netmask,
                                   "type": "ethernet"})
    except (ImportError, AttributeError, pywintypes.com_error):
        log.warning("Could not use the COM service to retrieve interface info, trying using the registry...")
        return _get_windows_interfaces_from_registry()

    return interfaces


def interfaces():
    """
    Gets the network interfaces on this server.

    :returns: list of network interfaces
    """

    results = []
    if not sys.platform.startswith("win"):
        net_if_addrs = psutil.net_if_addrs()
        for interface in sorted(net_if_addrs.keys()):
            ip_address = ""
            mac_address = ""
            netmask = ""
            interface_type = "ethernet"
            for addr in net_if_addrs[interface]:
                # get the first available IPv4 address only
                if addr.family == socket.AF_INET:
                    ip_address = addr.address
                    netmask = addr.netmask
                if addr.family == psutil.AF_LINK:
                    mac_address = addr.address
            if interface.startswith("tap"):
                # found no way to reliably detect a TAP interface
                interface_type = "tap"
            results.append({"id": interface,
                            "name": interface,
                            "ip_address": ip_address,
                            "netmask": netmask,
                            "mac_address": mac_address,
                            "type": interface_type})
    else:
        results = get_windows_interfaces()
    return results
