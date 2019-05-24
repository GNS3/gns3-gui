# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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

import os
import sys
import shlex
import subprocess

from .qt import QtWidgets
from .local_config import LocalConfig
from .settings import PACKET_CAPTURE_SETTINGS
from .dialogs.capture_dialog import CaptureDialog
from .topology import Topology

import logging
log = logging.getLogger(__name__)


class PacketCapture:
    """
    This class manage packet capture, it's a singleton
    """

    def __init__(self):
        self._tail_process = {}
        self._capture_reader_process = {}
        # Auto start the capture program for th link
        self._autostart = {}

        Topology.instance().project_changed_signal.connect(self.killAllCapture)

    def killAllCapture(self):
        """
        Kill all running captures (for example when change project)
        """
        for process in list(self._tail_process.values()):
            try:
                process.kill()
            except OSError:
                pass
        self._tail_process = {}
        self._capture_reader_process = {}

    def topology(self):
        from .topology import Topology
        return Topology.instance()

    def parent(self):
        from .main_window import MainWindow
        return MainWindow.instance()

    def settings(self):
        return LocalConfig.instance().loadSectionSettings("PacketCapture", PACKET_CAPTURE_SETTINGS)

    def startCapture(self, link):
        """
        Start the packet capture reader on this port

        :param vm: Instance of the virtual machine
        :param port: Instance of port where capture should be executed
        :param file_path: capture file path on server
        """
        link.updated_link_signal.connect(self._updatedLinkSlot)
        if link.capturing():
            QtWidgets.QMessageBox.critical(self.parent(), "Packet capture", "A capture is already running")
            return
        if link.sourcePort().linkType() == "Serial":
            ethernet_link = False
        else:
            ethernet_link = True
        dialog = CaptureDialog(self.parent(), link.capture_file_name(), self.settings()["command_auto_start"], ethernet_link)
        if dialog.exec_():
            self._autostart[link] = dialog.commandAutoStart()
            link.startCapture(dialog.dataLink(), dialog.fileName() + ".pcap")

    def _updatedLinkSlot(self, link_id):
        link = self.topology().getLink(link_id)

        if link:
            if link.capturing():
                if self._autostart.get(link) and link not in self._tail_process:
                    self.startPacketCaptureReader(link)
                log.debug("Has successfully started capturing packets on {} to {}".format(link.id(), link.capture_file_path()))
            else:
                self.stopPacketCaptureReader(link)

    def stopCapture(self, link):
        """
        Stop the packet capture reader on this link

        :param vm: Instance of the virtual machine
        :param link: Instance of link where capture should be stopped
        """

        link.stopCapture()
        log.debug("Has successfully stopped capturing packets on {}".format(link.id()))

    def startPacketCaptureReader(self, link):
        """
        Starts the packet capture reader.
        """
        self._startPacketCommand(link, self.settings()["packet_capture_reader_command"])

    def stopPacketCaptureReader(self, link):
        """
        Stop the packet capture reader
        """
        if link in self._tail_process and self._tail_process[link].poll() is None:
            self._tail_process[link].kill()
            del self._tail_process[link]

    def startPacketCaptureAnalyzer(self, link):
        """
        Starts the packet capture analyzer
        """

        if link.capture_file_path() is None:
            QtWidgets.QMessageBox.critical(self.parent(), "Packet Capture Analyzer", "A packet capture is not running")
            return

        capture_file_path = link.capture_file_path()
        if not os.path.isfile(capture_file_path):
            QtWidgets.QMessageBox.critical(self.parent(), "Packet Capture Analyzer", "No packet capture file found at '{}'".format(capture_file_path))
            return

        command = self.settings()["packet_capture_analyzer_command"]

        # PCAP capture file path
        command = command.replace("%c", '"' + capture_file_path + '"')

        # Add description
        description = "{}[{}]->{}[{}]".format(link.sourceNode().name(),
                                              link.sourcePort().name(),
                                              link.destinationNode().name(),
                                              link.destinationPort().name())
        command = command.replace("%d", description)

        if not sys.platform.startswith("win"):
            command = shlex.split(command)
        if len(command) == 0:
            QtWidgets.QMessageBox.critical(self.parent(), "Packet Capture Analyzer", "No packet capture analyzer program configured")
            return
        try:
            subprocess.Popen(command)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self.parent(), "Packet Capture Analyzer", "Can't start packet capture analyzer program {}".format(str(e)))
            return

    def packetAnalyzerAvailable(self):

        command = self.settings()["packet_capture_analyzer_command"]
        return command is not None and len(command) > 0

    def _startPacketCommand(self, link, command):
        """
        Start a command for analyzing the packets
        """

        if link.capture_file_path() is None:
            QtWidgets.QMessageBox.critical(self.parent(), "Packet capture", "A packet capture is not running")
            return

        capture_file_path = link.capture_file_path()

        if not os.path.isfile(capture_file_path):
            try:
                open(capture_file_path, 'w+').close()
            except OSError as e:
                QtWidgets.QMessageBox.critical(self.parent(), "Packet capture", "Can't create packet capture file {}: {}".format(capture_file_path, str(e)))
                return

        if link in self._tail_process and self._tail_process[link].poll() is None:
            try:
                self._tail_process[link].kill()
            except (PermissionError, OSError):
                # Sometimes we have condition on windows where the process is in the process to quit
                pass
            del self._tail_process[link]
        if link in self._capture_reader_process and self._capture_reader_process[link].poll() is None:
            try:
                self._capture_reader_process[link].kill()
            except (PermissionError, OSError):
                pass
            del self._capture_reader_process[link]

        # PCAP capture file path
        command = command.replace("%c", '"' + capture_file_path + '"')

        # Add description
        description = "{} {} to {} {}".format(link.sourceNode().name(),
                                              link.sourcePort().name(),
                                              link.destinationNode().name(),
                                              link.destinationPort().name())
        command = command.replace("%d", description)

        if "|" in command:
            # live traffic capture (using tail)
            command1, command2 = command.split("|", 1)
            info = None
            if sys.platform.startswith("win"):
                # hide tail window on Windows
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                info.wShowWindow = subprocess.SW_HIDE
                if hasattr(sys, "frozen"):
                    tail_path = os.path.dirname(os.path.abspath(sys.executable))  # for Popen to find tail.exe
                else:
                    # We suppose a developer will have tail the standard GNS3 location
                    tail_path = "C:\\Program Files\\GNS3"
                command1 = command1.replace("tail.exe", os.path.join(tail_path, "tail.exe"))
                command1 = command1.strip()
                command2 = command2.strip()
            else:
                try:
                    command1 = shlex.split(command1)
                    command2 = shlex.split(command2)
                except ValueError as e:
                    log.error("Invalid packet capture command {}: {}".format(command, str(e)))
                    return
            try:
                self._tail_process[link] = subprocess.Popen(command1, startupinfo=info, stdout=subprocess.PIPE)
                self._capture_reader_process[link] = subprocess.Popen(
                    command2,
                    stdin=self._tail_process[link].stdout,
                    stdout=subprocess.PIPE)
                self._tail_process[link].stdout.close()
            except OSError as e:
                QtWidgets.QMessageBox.critical(self.parent(), "Packet capture", "Can't start packet capture program {}".format(str(e)))
                return
        else:
            # normal traffic capture
            if not sys.platform.startswith("win"):
                command = shlex.split(command)
            if len(command) == 0:
                QtWidgets.QMessageBox.critical(self.parent(), "Packet capture", "No packet capture program configured")
                return
            try:
                self._capture_reader_process[link] = subprocess.Popen(command)
            except OSError as e:
                QtWidgets.QMessageBox.critical(self.parent(), "Packet capture", "Can't start packet capture program {}".format(str(e)))
                return

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Servers.

        :returns: instance of Servers
        """

        if not hasattr(PacketCapture, "_instance"):
            PacketCapture._instance = PacketCapture()
        return PacketCapture._instance
