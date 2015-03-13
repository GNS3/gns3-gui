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
Default general settings.
"""

import os
import sys
import platform

# Projects directory location
DEFAULT_PROJECTS_PATH = os.path.normpath(os.path.expanduser("~/GNS3/projects"))

# Images directory location
DEFAULT_IMAGES_PATH = os.path.normpath(os.path.expanduser("~/GNS3/images"))

DEFAULT_LOCAL_SERVER_HOST = "127.0.0.1"
DEFAULT_LOCAL_SERVER_PORT = 8000

# Pre-configured Telnet console commands on various OSes
if sys.platform.startswith("win"):
    if "PROGRAMFILES(X86)" in os.environ:
        # windows 64-bit
        program_files = os.environ["PROGRAMFILES"]
        program_files_x86 = os.environ["PROGRAMFILES(X86)"]
    else:
        # windows 32-bit
        program_files_x86 = program_files = os.environ["PROGRAMFILES"]

    PRECONFIGURED_TELNET_CONSOLE_COMMANDS = {'Putty (included with GNS3)': 'putty.exe -telnet %h %p -wt "%d" -gns3 5 -skin 4',
                                             'SuperPutty (included with GNS3)': r'SuperPutty.exe -telnet "%h -P %p -wt \"%d\""',
                                             'SecureCRT': r'"{}\VanDyke Software\SecureCRT\SecureCRT.exe" /SCRIPT securecrt.vbs /ARG "%d" /T /TELNET %h %p'.format(program_files),
                                             'TeraTerm Pro': r'"{}\teraterm\ttermpro.exe" /W="%d" /M="ttstart.macro" /T=1 %h %p'.format(program_files_x86),
                                             'Telnet': 'telnet %h %p',
                                             'Xshell 4': r'"{}\NetSarang\Xshell 4\xshell.exe" -url telnet://%h:%p'.format(program_files_x86),
                                             'ZOC 6': r'"{}\ZOC6\zoc.exe" "/TELNET:%h:%p" /TABBED "/TITLE:%d"'.format(program_files_x86)}

    # default on Windows
    DEFAULT_TELNET_CONSOLE_COMMAND = PRECONFIGURED_TELNET_CONSOLE_COMMANDS["Putty (included with GNS3)"]

elif sys.platform.startswith("darwin"):
    # Mac OS X
    PRECONFIGURED_TELNET_CONSOLE_COMMANDS = {
        'Terminal': "osascript -e 'tell application \"Terminal\"'"
                    " -e 'activate'"
                    " -e 'set _tab to do script \"telnet %h %p ; exit\"'"
                    " -e 'delay 1'"
                    " -e 'repeat while _tab exists'"
                    " -e 'delay 1'"
                    " -e 'end repeat'"
                    " -e 'end tell'",
        'iTerm': "osascript -e 'tell application \"iTerm\"'"
                 " -e 'activate'"
                 " -e 'if (count of terminals) = 0 then'"
                 " -e '  set t to (make new terminal)'"
                 " -e 'else'"
                 " -e '  set t to current terminal'"
                 " -e 'end if'"
                 " -e 'tell t'"
                 " -e '  set s to (make new session at the end of sessions)'"
                 " -e '  tell s'"
                 " -e '    exec command (\"telnet %h %p\")'"
                 " -e '    delay 1'"
                 " -e '    repeat while s exists'"
                 " -e '      delay 1'"
                 " -e '    end repeat'"
                 " -e '  end tell'"
                 " -e 'end tell'"
                 " -e 'end tell'",
        'SecureCRT': '/Applications/SecureCRT.app/Contents/MacOS/SecureCRT /ARG "%d" /T /TELNET %h %p',
        'ZOC 6': '/Applications/zoc6.app/Contents/MacOS/zoc6 "/TELNET:%h:%p" /TABBED "/TITLE:%d"'
    }

    # default Mac OS X Telnet console command
    DEFAULT_TELNET_CONSOLE_COMMAND = PRECONFIGURED_TELNET_CONSOLE_COMMANDS["Terminal"]

else:
    PRECONFIGURED_TELNET_CONSOLE_COMMANDS = {'Xterm': 'xterm -T "%d" -e "telnet %h %p"',
                                             'Putty': 'putty -telnet %h %p -title "%d" -sl 2500 -fg SALMON1 -bg BLACK',
                                             'Gnome Terminal': 'gnome-terminal -t "%d" -e "telnet %h %p"',
                                             'Xfce4 Terminal': 'xfce4-terminal -T "%d" -e "telnet %h %p"',
                                             'ROXTerm': 'roxterm -n "%d" --tab -e "telnet %h %p"',
                                             'KDE Konsole': 'konsole --new-tab -p tabtitle="%d" -e "telnet %h %p"',
                                             'SecureCRT': 'SecureCRT /T /N "%d"  /TELNET %h %p',
                                             'Mate Terminal': 'mate-terminal --tab -e "telnet %h %p"  -t "%d"'}

    # default Telnet console command on other systems
    DEFAULT_TELNET_CONSOLE_COMMAND = PRECONFIGURED_TELNET_CONSOLE_COMMANDS["Xterm"]

    if sys.platform.startswith("linux"):
        distro = platform.linux_distribution()[0]
        if distro == "Debian" or distro == "Ubuntu" or distro == "LinuxMint":
            DEFAULT_TELNET_CONSOLE_COMMAND = PRECONFIGURED_TELNET_CONSOLE_COMMANDS["Gnome Terminal"]

# Pre-configured serial console commands on various OSes
if sys.platform.startswith("win"):
    # Windows
    PRECONFIGURED_SERIAL_CONSOLE_COMMANDS = {'Putty (included with GNS3)': 'putty.exe -serial %s -wt "%d [Local Console]" -gns3 5',
                                             'SuperPutty': r'SuperPutty.exe -serial "%s -wt \"%d\""'}

    # default Windows serial console command
    if os.path.exists(os.getcwd() + os.sep + "SuperPutty.exe"):
        DEFAULT_SERIAL_CONSOLE_COMMAND = PRECONFIGURED_SERIAL_CONSOLE_COMMANDS["SuperPutty"]
    else:
        DEFAULT_SERIAL_CONSOLE_COMMAND = PRECONFIGURED_SERIAL_CONSOLE_COMMANDS["Putty (included with GNS3)"]

elif sys.platform.startswith("darwin"):
    # Mac OS X
    PRECONFIGURED_SERIAL_CONSOLE_COMMANDS = {'Terminal + socat': "/usr/bin/osascript -e 'tell application \"terminal\" to do script with command \"socat UNIX-CONNECT:\\\"%s\\\" stdio,raw,echo=0 ; exit\"'"}

    # default Mac OS X serial console command
    DEFAULT_SERIAL_CONSOLE_COMMAND = PRECONFIGURED_SERIAL_CONSOLE_COMMANDS["Terminal + socat"]

else:
    PRECONFIGURED_SERIAL_CONSOLE_COMMANDS = {'Xterm + socat': 'xterm -T "%d" -e \'socat UNIX-CONNECT:"%s" stdio,raw,echo=0\'',
                                             'Gnome Terminal + socat': 'gnome-terminal -t "%d" -e \'socat UNIX-CONNECT:"%s" stdio,raw,echo=0\'',
                                             'Konsole + socat': 'konsole --new-tab -p tabtitle="%d" -e \'socat UNIX-CONNECT:"%s" stdio,raw,echo=0\''}

    # default serial console command on other systems
    DEFAULT_SERIAL_CONSOLE_COMMAND = PRECONFIGURED_SERIAL_CONSOLE_COMMANDS["Xterm + socat"]

    if sys.platform.startswith("linux"):
        distro = platform.linux_distribution()[0]
        if distro == "Debian" or distro == "Ubuntu" or distro == "LinuxMint":
            DEFAULT_SERIAL_CONSOLE_COMMAND = PRECONFIGURED_SERIAL_CONSOLE_COMMANDS["Gnome Terminal + socat"]

# Pre-configured packet capture reader commands on various OSes
WIRESHARK_NORMAL_CAPTURE = "Wireshark Traditional Capture"
WIRESHARK_LIVE_TRAFFIC_CAPTURE = "Wireshark Live Traffic Capture"

if sys.platform.startswith("win"):
    PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS = {WIRESHARK_NORMAL_CAPTURE: "{}\Wireshark\wireshark.exe %c".format(os.environ["PROGRAMFILES"]),
                                                    WIRESHARK_LIVE_TRAFFIC_CAPTURE: 'tail.exe -f -c +0b %c | "{}\Wireshark\wireshark.exe" -k -i -'.format(os.environ["PROGRAMFILES"])}

elif sys.platform.startswith("darwin"):
    # Mac OS X
    PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS = {WIRESHARK_NORMAL_CAPTURE: "/usr/bin/open -a /Applications/Wireshark.app %c",
                                                    WIRESHARK_LIVE_TRAFFIC_CAPTURE: "tail -f -c +0 %c | /Applications/Wireshark.app/Contents/Resources/bin/wireshark -k -i -"}

elif sys.platform.startswith("freebsd"):
    # FreeBSD
    PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS = {WIRESHARK_NORMAL_CAPTURE: "wireshark %c",
                                                    WIRESHARK_LIVE_TRAFFIC_CAPTURE: "gtail -f -c +0b %c | wireshark -k -i -"}
else:
    PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS = {WIRESHARK_NORMAL_CAPTURE: "wireshark %c",
                                                    WIRESHARK_LIVE_TRAFFIC_CAPTURE: "tail -f -c +0b %c | wireshark -k -i -"}

DEFAULT_PACKET_CAPTURE_READER_COMMAND = PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS[WIRESHARK_LIVE_TRAFFIC_CAPTURE]

DEFAULT_PACKET_CAPTURE_ANALYZER_COMMAND = ""
if sys.platform.startswith("win") and "PROGRAMFILES(X86)" in os.environ:
    # Windows 64-bit
    DEFAULT_PACKET_CAPTURE_ANALYZER_COMMAND = r'"{}\SolarWinds\ResponseTimeViewer\ResponseTimeViewer.exe" %c'.format(os.environ["PROGRAMFILES(X86)"])

STYLES = ["Charcoal", "Classic", "Legacy"]

if sys.platform.startswith("win"):
    DEFAULT_STYLE = "Classic"
else:
    DEFAULT_STYLE = "Charcoal"

GENERAL_SETTINGS = {
    "style": DEFAULT_STYLE,
    "auto_launch_project_dialog": True,
    "auto_screenshot": True,
    "check_for_update": True,
    "last_check_for_update": 0,
    "slow_device_start_all": 0,
    "link_manual_mode": True,
    "telnet_console_command": DEFAULT_TELNET_CONSOLE_COMMAND,
    "serial_console_command": DEFAULT_SERIAL_CONSOLE_COMMAND,
    "auto_close_console": True,
    "bring_console_to_front": True,
    "delay_console_all": 500,
    "default_local_news": False,
    "hide_news_dock_widget": False,
    "debug_level": 0,
}

GENERAL_SETTING_TYPES = {
    "style": str,
    "auto_launch_project_dialog": bool,
    "auto_screenshot": bool,
    "check_for_update": bool,
    "last_check_for_update": int,
    "slow_device_start_all": int,
    "link_manual_mode": bool,
    "telnet_console_command": str,
    "serial_console_command": str,
    "auto_close_console": bool,
    "bring_console_to_front": bool,
    "delay_console_all": int,
    "default_local_news": bool,
    "hide_news_dock_widget": bool,
    "debug_level": int,
}

GRAPHICS_VIEW_SETTINGS = {
    "scene_width": 2000,
    "scene_height": 1000,
    "draw_rectangle_selected_item": False,
    "draw_link_status_points": True,
    "default_label_font": "TypeWriter,10,-1,5,75,0,0,0,0,0",
    "default_label_color": "#000000",
}

GRAPHICS_VIEW_SETTING_TYPES = {
    "scene_width": int,
    "scene_height": int,
    "draw_rectangle_selected_item": bool,
    "draw_link_status_points": bool,
    "default_label_font": str,
    "default_label_color": str,
}

LOCAL_SERVER_SETTINGS = {
    "path": "",
    "host": DEFAULT_LOCAL_SERVER_HOST,
    "port": DEFAULT_LOCAL_SERVER_PORT,
    "images_path": DEFAULT_IMAGES_PATH,
    "projects_path": DEFAULT_PROJECTS_PATH,
    "report_errors": True,
    "auto_start": True,
    "allow_console_from_anywhere": False,
    "console_start_port_range": 2001,
    "console_end_port_range": 5000,
    "udp_start_port_range": 10000,
    "udp_end_port_range": 20000,
}

LOCAL_SERVER_SETTING_TYPES = {
    "path": str,
    "host": str,
    "port": int,
    "images_path": str,
    "projects_path": str,
    "report_errors": bool,
    "auto_start": bool,
    "allow_console_from_anywhere": bool,
    "console_start_port_range": int,
    "console_end_port_range": int,
    "udp_start_port_range": int,
    "udp_end_port_range": int,
}

PACKET_CAPTURE_SETTINGS = {
    "packet_capture_reader_command": DEFAULT_PACKET_CAPTURE_READER_COMMAND,
    "command_auto_start": True,
    "packet_capture_analyzer_command": DEFAULT_PACKET_CAPTURE_ANALYZER_COMMAND,
}

PACKET_CAPTURE_SETTING_TYPES = {
    "packet_capture_reader_command": str,
    "command_auto_start": bool,
    "packet_capture_analyzer_command": str,
}

ENABLE_CLOUD = False

CLOUD_SETTINGS = {
    "cloud_user_name": "",
    "cloud_api_key": "",
    "cloud_store_api_key": False,
    # no default value at startup, users must choose and we need to know if they've already done it
    "cloud_store_api_key_chosen": False,
    "cloud_provider": "rackspace",
    "cloud_region": "",
    "instances_per_project": 0,
    "default_flavor": "",
    "new_instance_flavor": "",
    "accepted_terms": False,
    "instance_timeout": 30,
    "default_image": "",
}

CLOUD_SETTINGS_TYPES = {
    "cloud_user_name": str,
    "cloud_api_key": str,
    "cloud_store_api_key": bool,
    "cloud_store_api_key_chosen": bool,
    "cloud_provider": str,
    "cloud_region": str,
    "instances_per_project": int,
    "default_flavor": str,
    "new_instance_flavor": str,
    "accepted_terms": bool,
    "instance_timeout": int,
    "default_image": str,
}

# TODO proof of concept, needs review
CLOUD_PROVIDERS = {
    "rackspace": ("Rackspace", 'gns3.cloud.rackspace_ctrl.RackspaceCtrl'),
}

# heartbeat_freq is in milliseconds
DEFAULT_HEARTBEAT_FREQ = 60000
