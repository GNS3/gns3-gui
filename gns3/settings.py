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
import uuid
import platform

# Default projects directory location
DEFAULT_PROJECTS_PATH = os.path.normpath(os.path.expanduser("~/GNS3/projects"))

# Default images directory location
DEFAULT_IMAGES_PATH = os.path.normpath(os.path.expanduser("~/GNS3/images"))

# Default symbols directory location
DEFAULT_SYMBOLS_PATH = os.path.normpath(os.path.expanduser("~/GNS3/symbols"))

# Default configs directory location
DEFAULT_CONFIGS_PATH = os.path.normpath(os.path.expanduser("~/GNS3/configs"))

DEFAULT_LOCAL_SERVER_HOST = "127.0.0.1"
DEFAULT_LOCAL_SERVER_PORT = 3080

# Pre-configured Telnet console commands on various OSes
if sys.platform.startswith("win"):
    userprofile = os.path.expandvars("%USERPROFILE%")
    if "PROGRAMFILES(X86)" in os.environ:
        # windows 64-bit
        program_files = os.environ["PROGRAMFILES"]
        program_files_x86 = os.environ["PROGRAMFILES(X86)"]
    else:
        # windows 32-bit
        program_files_x86 = program_files = os.environ["PROGRAMFILES"]

    PRECONFIGURED_TELNET_CONSOLE_COMMANDS = {'Putty (included with GNS3)': 'putty.exe -telnet %h %p -wt "%d" -gns3 5 -skin 4',
                                             'MobaXterm': r'"{}\Mobatek\MobaXterm Personal Edition\MobaXterm.exe" -newtab "telnet %h %p"'.format(program_files_x86),
                                             'Royal TS': '{}\code4ward.net\Royal TS V3\RTS3App.exe /connectadhoc:%h /adhoctype:terminal /p:IsTelnetConnection="true" /p:ConnectionType="telnet;Telnet Connection" /p:Port="%p" /p:Name="%d"'.format(program_files),
                                             'SuperPutty (included with GNS3)': r'SuperPutty.exe -telnet "%h -P %p -wt \"%d\""',
                                             'SecureCRT': r'"{}\VanDyke Software\SecureCRT\SecureCRT.exe" /N "%d" /T /TELNET %h %p'.format(program_files),
                                             'SecureCRT (personal profile)': r'"{}\AppData\Local\VanDyke Software\SecureCRT\SecureCRT.exe" /T /N "%d" /TELNET %h %p'.format(userprofile),
                                             'TeraTerm Pro': r'"{}\teraterm\ttermpro.exe" /W="%d" /M="ttstart.macro" /T=1 %h %p'.format(program_files_x86),
                                             'Telnet': 'telnet %h %p',
                                             'Xshell 4': r'"{}\NetSarang\Xshell 4\xshell.exe" -url telnet://%h:%p'.format(program_files_x86),
                                             'Xshell 5': r'"{}\NetSarang\Xshell 5\xshell.exe" -url telnet://%h:%p -newtab %d'.format(program_files_x86),
                                             'ZOC 6': r'"{}\ZOC6\zoc.exe" "/TELNET:%h:%p" /TABBED "/TITLE:%d"'.format(program_files_x86)}

    # default on Windows
    DEFAULT_TELNET_CONSOLE_COMMAND = PRECONFIGURED_TELNET_CONSOLE_COMMANDS["Putty (included with GNS3)"]

elif sys.platform.startswith("darwin"):
    # Mac OS X
    PRECONFIGURED_TELNET_CONSOLE_COMMANDS = {
        'Terminal': "osascript -e 'tell application \"Terminal\"'"
                    " -e 'activate'"
                    " -e 'do script \"echo -n -e \\\"\\\\033]0;%d\\\\007\\\"; clear; telnet %h %p ; exit\"'"
                    " -e 'end tell'",
        'Terminal tabbed (experimental)': "osascript -e 'tell application \"Terminal\"'"
                    " -e 'activate'"
                        " -e 'tell application \"System Events\" to tell process \"Terminal\" to keystroke \"t\" using command down'"
                        " -e 'if (the (count of the window) = 0) then'"
                            " -e 'repeat while contents of selected tab of window 1 starts with linefeed'"
                                " -e 'delay 0.01'"
                            " -e 'end repeat'"
                            " -e 'tell application \"System Events\" to keystroke \"n\" using command down'"
                        " -e 'end if'"
                        " -e 'repeat while the busy of window 1 = true'"
                            " -e 'delay 0.01'"
                        " -e 'end repeat'"
                        " -e 'do script \"echo -n -e \\\"\\\\033]0;%d\\\\007\\\" ; telnet %h %p ; exit\" in window 1'"
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
                 " -e '  end tell'"
                 " -e 'end tell'"
                 " -e 'end tell'",
        'iTerm 2.9': "osascript -e 'tell application \"iTerm\"'"
                    " -e 'activate'"
                    " -e 'if (count of windows) = 0 then'"
                    " -e '   set t to (create window with default profile)'"
                    " -e 'else'"
                    " -e '   set t to current window'"
                    " -e 'end if'"
                    " -e 'tell t'"
                    " -e '    create tab with default profile'"
                    " -e '    set s to current session'"
                    " -e '    tell s'"
                    " -e '        write text \"telnet %h %p\"'"
                    " -e '    end tell'"
                    " -e 'end tell'"
                    " -e 'end tell'",
        'Royal TSX': "open 'rtsx://telnet%3A%2F%2F%h:%p'",
        'SecureCRT': '/Applications/SecureCRT.app/Contents/MacOS/SecureCRT /N "%d" /T /TELNET %h %p',
        'ZOC 6': '/Applications/zoc6.app/Contents/MacOS/zoc6 "/TELNET:%h:%p" /TABBED "/TITLE:%d"',
        'ZOC 7': '/Applications/zoc7.app/Contents/MacOS/zoc7 "/TELNET:%h:%p" /TABBED "/TITLE:%d"'
    }

    # default Mac OS X Telnet console command
    DEFAULT_TELNET_CONSOLE_COMMAND = PRECONFIGURED_TELNET_CONSOLE_COMMANDS["Terminal"]

else:
    PRECONFIGURED_TELNET_CONSOLE_COMMANDS = {'Xterm': 'xterm -T "%d" -e "telnet %h %p"',
                                             'Putty': 'putty -telnet %h %p -title "%d" -sl 2500 -fg SALMON1 -bg BLACK',
                                             'Gnome Terminal': 'gnome-terminal -t "%d" -e "telnet %h %p"',
                                             'Xfce4 Terminal': 'xfce4-terminal --tab -T "%d" -e "telnet %h %p"',
                                             'ROXTerm': 'roxterm -n "%d" --tab -e "telnet %h %p"',
                                             'KDE Konsole': 'konsole --new-tab -p tabtitle="%d" -e "telnet %h %p"',
                                             'SecureCRT': 'SecureCRT /T /N "%d"  /TELNET %h %p',
                                             'Mate Terminal': 'mate-terminal --tab -e "telnet %h %p"  -t "%d"',
                                             'urxvt': 'urxvt -title %d -e telnet %h %p'}

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
    PRECONFIGURED_SERIAL_CONSOLE_COMMANDS = {'Terminal + nc': "/usr/bin/osascript -e 'tell application \"terminal\" to do script with command \"stty raw; /usr/bin/nc -U \\\"%s\\\"; exit\"'",
                                             'Terminal + socat': "/usr/bin/osascript -e 'tell application \"terminal\" to do script with command \"socat UNIX-CONNECT:\\\"%s\\\" stdio,raw,echo=0 ; exit\"'"}

    # default Mac OS X serial console command
    DEFAULT_SERIAL_CONSOLE_COMMAND = PRECONFIGURED_SERIAL_CONSOLE_COMMANDS['Terminal + nc']

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

# Pre-configured VNC console commands on various OSes
if sys.platform.startswith("win"):
    # Windows
    PRECONFIGURED_VNC_CONSOLE_COMMANDS = {'TightVNC (included with GNS3)': 'tvnviewer.exe %h:%p'}

    # default Windows VNC console command
    DEFAULT_VNC_CONSOLE_COMMAND = PRECONFIGURED_VNC_CONSOLE_COMMANDS['TightVNC (included with GNS3)']

elif sys.platform.startswith("darwin"):
    # Mac OS X
    PRECONFIGURED_VNC_CONSOLE_COMMANDS = {
        'OSX builtin screen sharing': "osascript"
        " -e 'tell application \"Screen Sharing\"'"
        " -e '   display dialog \"WARNING OSX VNC support is limited if you have trouble connecting to a device please use an alternative client like Chicken of the VNC.\" buttons {\"OK\"} default button 1 with icon caution with title \"GNS3\"'"
        " -e '  open location \"vnc://%h:%p\"'"
        " -e 'end tell'",
        'Chicken of the VNC': "/Applications/Chicken\ of\ the\ VNC.app/Contents/MacOS/Chicken\ of\ the\ VNC %h:%p",
        'Royal TSX': "open 'rtsx://vnc%3A%2F%2F%h:%p'",
    }

    # default Mac OS X VNC console command
    DEFAULT_VNC_CONSOLE_COMMAND = PRECONFIGURED_VNC_CONSOLE_COMMANDS['OSX builtin screen sharing']

else:
    PRECONFIGURED_VNC_CONSOLE_COMMANDS = {
        'TightVNC': 'vncviewer %h:%p',
        'Vinagre': 'vinagre %h::%p'
    }

    # default VNC console command on other systems
    DEFAULT_VNC_CONSOLE_COMMAND = PRECONFIGURED_VNC_CONSOLE_COMMANDS['TightVNC']

# Pre-configured packet capture reader commands on various OSes
WIRESHARK_NORMAL_CAPTURE = "Wireshark Traditional Capture"
WIRESHARK_LIVE_TRAFFIC_CAPTURE = "Wireshark Live Traffic Capture"

if sys.platform.startswith("win"):
    PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS = {WIRESHARK_NORMAL_CAPTURE: "{}\Wireshark\wireshark.exe %c".format(os.environ["PROGRAMFILES"]),
                                                    WIRESHARK_LIVE_TRAFFIC_CAPTURE: 'tail.exe -f -c +0b %c | "{}\Wireshark\wireshark.exe" -o "gui.window_title:%d" -k -i -'.format(os.environ["PROGRAMFILES"])}

elif sys.platform.startswith("darwin"):
    # Mac OS X
    PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS = {WIRESHARK_NORMAL_CAPTURE: "/usr/bin/open -a /Applications/Wireshark.app %c",
                                                    "Wireshark V1.X Live Traffic Capture": 'tail -f -c +0 %c | /Applications/Wireshark.app/Contents/Resources/bin/wireshark -o "gui.window_title:%d" -k -i -',
                                                    WIRESHARK_LIVE_TRAFFIC_CAPTURE: 'tail -f -c +0 %c | /Applications/Wireshark.app/Contents/MacOS/Wireshark -o "gui.window_title:%d" -k -i -'}

elif sys.platform.startswith("freebsd"):
    # FreeBSD
    PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS = {WIRESHARK_NORMAL_CAPTURE: "wireshark %c",
                                                    WIRESHARK_LIVE_TRAFFIC_CAPTURE: 'gtail -f -c +0b %c | wireshark -o "gui.window_title:%d" -k -i -'}
else:
    PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS = {WIRESHARK_NORMAL_CAPTURE: "wireshark %c",
                                                    WIRESHARK_LIVE_TRAFFIC_CAPTURE: 'tail -f -c +0b %c | wireshark -o "gui.window_title:%d" -k -i -'}

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
    "experimental_features": False,
    "send_stats": True,
    "stats_visitor_id": str(uuid.uuid4()),  # An anonymous id for stats
    "last_check_for_update": 0,
    "slow_device_start_all": 0,
    "link_manual_mode": True,
    "telnet_console_command": DEFAULT_TELNET_CONSOLE_COMMAND,
    "serial_console_command": DEFAULT_SERIAL_CONSOLE_COMMAND,
    "vnc_console_command": DEFAULT_VNC_CONSOLE_COMMAND,
    "auto_close_console": True,
    "bring_console_to_front": True,
    "delay_console_all": 500,
    "default_local_news": False,
    "hide_getting_started_dialog": False,
    "hide_setup_wizard": False,
    "recent_files": [],
    "geometry": "",
    "state": "",
    "preferences_dialog_geometry": "",
    "debug_level": 0,
}

GRAPHICS_VIEW_SETTINGS = {
    "scene_width": 2000,
    "scene_height": 1000,
    "draw_rectangle_selected_item": False,
    "draw_link_status_points": True,
    "default_label_font": "TypeWriter,10,-1,5,75,0,0,0,0,0",
    "default_label_color": "#000000",
}

SERVERS_SETTINGS = {
    "local_server": {
        "path": "",
        "ubridge_path": "",
        "host": DEFAULT_LOCAL_SERVER_HOST,
        "port": DEFAULT_LOCAL_SERVER_PORT,
        "images_path": DEFAULT_IMAGES_PATH,
        "projects_path": DEFAULT_PROJECTS_PATH,
        "symbols_path": DEFAULT_SYMBOLS_PATH,
        "configs_path": DEFAULT_CONFIGS_PATH,
        "report_errors": True,
        "auto_start": True,
        "allow_console_from_anywhere": False,
        "auth": True,
        "user": "",
        "password": "",
        "console_start_port_range": 5000,
        "console_end_port_range": 10000,
        "udp_start_port_range": 10000,
        "udp_end_port_range": 20000,
    },
    "vm": {
        "auto_start": False,
        "auto_stop": True,
        "headless": False,
        "adjust_local_server_ip": True,
        "vmname": "GNS3 VM",
        "vmx_path": "",
        "virtualization": "VMware",
        "remote_vm_url": "",
        "remote_vm_protocol": "http",
        "remote_vm_host": "",
        "remote_vm_port": 3080,
        "remote_vm_user": "",
        "remote_vm_password": ""
    },
    "remote_servers": [],
}

PACKET_CAPTURE_SETTINGS = {
    "packet_capture_reader_command": DEFAULT_PACKET_CAPTURE_READER_COMMAND,
    "command_auto_start": True,
    "packet_capture_analyzer_command": DEFAULT_PACKET_CAPTURE_ANALYZER_COMMAND,
}

CUSTOM_CONSOLE_COMMANDS_SETTINGS = {
    "telnet": {},
    "vnc": {},
    "serial": {}
}
