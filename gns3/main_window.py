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
Main window for the GUI.
"""

import os
import tempfile
import socket
import shutil
import json
from .qt import QtGui, QtCore
from .servers import Servers
from .node import Node
from .ui.main_window_ui import Ui_MainWindow
from .preferences_dialog import PreferencesDialog
from .settings import GENERAL_SETTINGS, GENERAL_SETTING_TYPES
from .utils.progress_dialog import ProgressDialog
from .utils.process_files_thread import ProcessFilesThread
from .utils.wait_for_connection_thread import WaitForConnectionThread
from .utils.message_box import MessageBox
from .items.node_item import NodeItem
from .topology import Topology

import logging
log = logging.getLogger(__name__)


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """
    Main window implementation.

    :param parent: parent widget
    """

    # signal to tell the view if the user is adding a link or not
    adding_link_signal = QtCore.Signal(bool)

    # for application reboot
    reboot_signal = QtCore.Signal()
    exit_code_reboot = -123456789

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self._settings = {}
        self._loadSettings()
        self._connections()
        self._ignore_unsaved_state = False

        self._temporary_project = True
        self._project_path = None
        self._project_files_dir = None

        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # load initial stuff once the event loop isn't busy
        QtCore.QTimer.singleShot(0, self.startupLoading)

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # restore the geometry and state of the main window.
        settings = QtCore.QSettings()
        self.restoreGeometry(settings.value("GUI/geometry", QtCore.QByteArray()))
        self.restoreState(settings.value("GUI/state", QtCore.QByteArray()))

        # restore the general settings
        settings.beginGroup(self.__class__.__name__)
        for name, value in GENERAL_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=GENERAL_SETTING_TYPES[name])
        settings.endGroup()

    def settings(self):
        """
        Returns the general settings.

        :returns: settings dictionary
        """

        return self._settings

    def setSettings(self, new_settings):
        """
        Set new general settings.

        :param new_settings: settings dictionary
        """

        # save the settings
        self._settings.update(new_settings)
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in self._settings.items():
            settings.setValue(name, value)
        settings.endGroup()

    def _connections(self):
        """
        Connect widgets to slots
        """

        # to reboot
        self.reboot_signal.connect(self.rebootSlot)

        # file menu connections
        self.uiNewProjectAction.triggered.connect(self._newProjectActionSlot)
        self.uiOpenProjectAction.triggered.connect(self._openProjectActionSlot)
        self.uiSaveProjectAction.triggered.connect(self._saveProjectActionSlot)
        self.uiSaveProjectAsAction.triggered.connect(self._saveProjectAsActionSlot)
        self.uiImportExportStartupConfigsAction.triggered.connect(self._importExportStartupConfigsActionSlot)
        self.uiScreenshotAction.triggered.connect(self._screenshotActionSlot)
        self.uiSnapshotAction.triggered.connect(self._snapshotActionSlot)

        # edit menu connections
        self.uiSelectAllAction.triggered.connect(self._selectAllActionSlot)
        self.uiSelectNoneAction.triggered.connect(self._selectNoneActionSlot)
        self.uiPreferencesAction.triggered.connect(self._preferencesActionSlot)

        # view menu connections
        self.uiZoomInAction.triggered.connect(self._zoomInActionSlot)
        self.uiZoomOutAction.triggered.connect(self._zoomOutActionSlot)
        self.uiZoomResetAction.triggered.connect(self._zoomResetActionSlot)
        self.uiFitInViewAction.triggered.connect(self._fitInViewActionSlot)
        self.uiShowLayersAction.triggered.connect(self._showLayersActionSlot)
        self.uiResetPortLabelsAction.triggered.connect(self._resetPortLabelsActionSlot)
        self.uiShowNamesAction.triggered.connect(self._showNamesActionSlot)

        # style menu connections
        self.uiDefaultStyleAction.triggered.connect(self._defaultStyleActionSlot)
        self.uiEnergySavingStyleAction.triggered.connect(self._energySavingStyleActionSlot)

        # control menu connections
        self.uiStartAllAction.triggered.connect(self._startAllActionSlot)
        self.uiSuspendAllAction.triggered.connect(self._suspendAllActionSlot)
        self.uiStopAllAction.triggered.connect(self._stopAllActionSlot)
        self.uiReloadAllAction.triggered.connect(self._reloadAllActionSlot)
        self.uiAuxConsoleAllAction.triggered.connect(self._auxConsoleAllActionSlot)
        self.uiConsoleAllAction.triggered.connect(self._consoleAllActionSlot)

        # annotate menu connections
        self.uiAddNoteAction.triggered.connect(self._addNoteActionSlot)
        self.uiInsertImageAction.triggered.connect(self._insertImageActionSlot)
        self.uiDrawRectangleAction.triggered.connect(self._drawRectangleActionSlot)
        self.uiDrawEllipseAction.triggered.connect(self._drawEllipseActionSlot)

        # help menu connections
        self.uiOnlineHelpAction.triggered.connect(self._onlineHelpActionSlot)
        self.uiCheckForUpdateAction.triggered.connect(self._checkForUpdateActionSlot)
        self.uiNewsAction.triggered.connect(self._newsActionSlot)
        self.uiLabInstructionsAction.triggered.connect(self._labInstructionsActionSlot)
        self.uiAboutQtAction.triggered.connect(self._aboutQtActionSlot)
        self.uiAboutAction.triggered.connect(self._aboutActionSlot)

        # browsers tool bar connections
        self.uiBrowseRoutersAction.triggered.connect(self._browseRoutersActionSlot)
        self.uiBrowseSwitchesAction.triggered.connect(self._browseSwitchesActionSlot)
        self.uiBrowseEndDevicesAction.triggered.connect(self._browseEndDevicesActionSlot)
        self.uiBrowseSecurityDevicesAction.triggered.connect(self._browseSecurityDevicesActionSlot)
        self.uiBrowseAllDevicesAction.triggered.connect(self._browseAllDevicesActionSlot)
        self.uiAddLinkAction.triggered.connect(self._addLinkActionSlot)

        # connect the signal to the view
        self.adding_link_signal.connect(self.uiGraphicsView.addingLinkSlot)

    def telnetConsoleCommand(self):
        """
        Returns the Telnet console command line.

        :returns: command (string)
        """

        return self._settings["telnet_console_command"]

    def setUnsavedState(self):
        """
        Sets the project in a unsaved state.
        """

        if not self._ignore_unsaved_state:
            self.setWindowModified(True)
            self.uiSaveProjectAction.setEnabled(True)

    def ignoreUnsavedState(self, value):
        """
        Activates or deactivates the possibility to
        set the project in unsaved state.

        :param value: boolean
        """

        self._ignore_unsaved_state = value

    def _newProjectActionSlot(self):
        """
        Slot called to create a new project.
        """

        if self.checkForUnsavedChanges():
            self._createTemporaryProject()

    def _openProjectActionSlot(self):
        """
        Slot called to open a project.
        """

        directory = self._settings["projects_path"]
        path = QtGui.QFileDialog.getOpenFileName(self, "Open project", directory)
        if path and self.checkForUnsavedChanges():
            self._loadProject(path)

    def _saveProjectActionSlot(self):
        """
        Slot called to save a project.
        """

        if self._temporary_project:
            return self._saveProjectAs()
        else:
            return self._saveProject(self._project_path)

    def _saveProjectAsActionSlot(self):
        """
        Slot called to save a project to another location/name.
        """

        self._saveProjectAs()

    def _importExportStartupConfigsActionSlot(self):
        """
        Slot called when importing and exporting startup-configs
        for the entire topology.
        """

        #TODO: mass import/export of startup-configs
        pass

    def _createScreenshot(self, path):
        """
        Create a screenshot of the scene.

        :returns: True if the image was successfully saved; otherwise returns False
        """

        scene = self.uiGraphicsView.scene()
        scene.clearSelection()
        scene.setSceneRect(scene.itemsBoundingRect().adjusted(-20.0, -20.0, 20.0, 20.0))
        image = QtGui.QImage(scene.sceneRect().size().toSize(), QtGui.QImage.Format_RGB32)
        image.fill(QtCore.Qt.white)
        painter = QtGui.QPainter(image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        scene.render(painter)
        painter.end()
        #TODO: quality option
        return image.save(path)

    def _screenshotActionSlot(self):
        """
        Slot called to take a screenshot of the scene.
        """

        # supported image file formats
        file_formats = "PNG File (*.png);;JPG File (*.jpeg *.jpg);;BMP File (*.bmp);;XPM File (*.xpm *.xbm);;PPM File (*.ppm);;TIFF File (*.tiff)"

        path, selected_filter = QtGui.QFileDialog.getSaveFileNameAndFilter(self, "Screenshot", ".", file_formats)
        if not path:
            return

        # add the extension if missing
        file_format = "." + selected_filter[:4].lower().strip()
        if not path.endswith(file_format):
            path = path + file_format

        if not self._createScreenshot(path):
            QtGui.QMessageBox.critical(self, "Screenshot", "Could not create screenshot file {}".format(path))

    def _snapshotActionSlot(self):
        """
        Slot called to open the snapshot dialog.
        """

        #TODO: snapshot support.
        pass

    def _selectAllActionSlot(self):
        """
        Slot called to select all the items on the scene.
        """

        scene = self.uiGraphicsView.scene()
        for item in scene.items():
            item.setSelected(True)

    def _selectNoneActionSlot(self):
        """
        Slot called to none of the items on the scene.
        """

        scene = self.uiGraphicsView.scene()
        for item in scene.items():
            item.setSelected(False)

    def _zoomInActionSlot(self):
        """
        Slot called to scale in the view.
        """

        factor_in = pow(2.0, 120 / 240.0)
        self.uiGraphicsView.scaleView(factor_in)

    def _zoomOutActionSlot(self):
        """
        Slot called to scale out the view.
        """

        factor_out = pow(2.0, -120 / 240.0)
        self.uiGraphicsView.scaleView(factor_out)

    def _zoomResetActionSlot(self):
        """
        Slot called to reset the zoom.
        """

        self.uiGraphicsView.resetMatrix()

    def _fitInViewActionSlot(self):
        """
        Slot called to fit the topology in the view.
        """

        view = self.uiGraphicsView
        bounding_rect = view.scene().itemsBoundingRect().adjusted(-20.0, -20.0, 20.0, 20.0)
        view.ensureVisible(bounding_rect)
        view.fitInView(bounding_rect, QtCore.Qt.KeepAspectRatio)

    def _showLayersActionSlot(self):
        """
        Slot called to show the layer positions on the scene.
        """

        #TODO: show layers
        pass

    def _resetPortLabelsActionSlot(self):
        """
        Slot called to reset the port labels on the scene.
        """

        #TODO: reset port labels
        pass

    def _showNamesActionSlot(self):
        """
        Slot called to show the node names on the scene.
        """

        #TODO: show/hide node names
        pass

    def _defaultStyleActionSlot(self):
        """
        Slot called to set the default style.
        """

        self.setStyleSheet("")
        self.uiEnergySavingStyleAction.setChecked(False)

    def _energySavingStyleActionSlot(self):
        """
        Slot called to set the energy saving style.
        """

        self.setStyleSheet("QMainWindow {} QMenuBar { background: black; } QDockWidget { background: black; color: white; } QToolBar { background: black; } QFrame { background: gray; } QToolButton { width: 30px; height: 30px; /*border:solid 1px black opacity 0.4;*/ /*background-none;*/ } QStatusBar { /*    background-image: url(:/pictures/pictures/texture_blackgrid.png);*/     background: black; color: rgb(255,255,255); }")
        self.uiDefaultStyleAction.setChecked(False)

    def _startAllActionSlot(self):
        """
        Slot called when starting all the nodes.
        """

        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "start"):
                item.node().start()

    def _suspendAllActionSlot(self):
        """
        Slot called when suspending all the nodes.
        """

        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "suspend"):
                item.node().suspend()

    def _stopAllActionSlot(self):
        """
        Slot called when stopping all the nodes.
        """

        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "stop"):
                item.node().stop()

    def _reloadAllActionSlot(self):
        """
        Slot called when reloading all the nodes.
        """

        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "reload"):
                item.node().reload()

    def _auxConsoleAllActionSlot(self):
        """
        Slot called when connecting to all the nodes using the AUX console.
        """

        #TODO: connect to AUX consoles
        pass

    def _consoleAllActionSlot(self):
        """
        Slot called when connecting to all the nodes using the console.
        """

        from .telnet_console import telnetConsole
        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "console"):
                node = item.node()
                name = node.name()
                console_port = node.console()
                console_host = node.server().host
                try:
                    telnetConsole(name, console_host, console_port)
                except (OSError, ValueError) as e:
                    QtGui.QMessageBox.critical(self, "Console", 'could not start console: {}'.format(e))
                    break

    def _addNoteActionSlot(self):
        """
        Slot called when adding a new note on the scene.
        """

        #TODO: add notes
        pass

    def _insertImageActionSlot(self):
        """
        Slot called when inserting an image on the scene.
        """

        #TODO: insert images
        pass

    def _drawRectangleActionSlot(self):
        """
        Slot called when adding a rectangle on the scene.
        """

        #TODO: draw rectangles
        pass

    def _drawEllipseActionSlot(self):
        """
        Slot called when adding a ellipse on the scene.
        """

        #TODO: draw ellipse
        pass

    def _onlineHelpActionSlot(self):
        """
        Slot to launch a browser pointing to the documentation page.
        """

        QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://www.gns3.net/documentation/"))

    def _checkForUpdateActionSlot(self):
        """
        Slot to check if a newer version is available.
        """

        #TODO: check for update
        QtGui.QMessageBox.critical(self, "Check For Update", "Sorry, to be implemented!")

    def _newsActionSlot(self):
        """
        Slot to open the news dialog.
        """

        #TODO: news dialog implementation
        QtGui.QMessageBox.critical(self, "News", "Sorry, to be implemented!")

    def _labInstructionsActionSlot(self):
        """
        Slot to open lab instructions.
        """

        #TODO: lab instructions
        QtGui.QMessageBox.critical(self, "Lab instructions", "Sorry, to be implemented!")

    def _aboutQtActionSlot(self):
        """
        Slot to display the Qt About dialog.
        """

        QtGui.QMessageBox.aboutQt(self)

    def _aboutActionSlot(self):
        """
        Slot to display the GNS3 About dialog.
        """

        #TODO: about dialog.
        QtGui.QMessageBox.critical(self, "About", "Sorry, to be implemented!")

#     def _doSlidingWindow(self, type):
#         """
#         Make the NodeDock appear (sliding effect is in progress)
#         with the appropriate title and the devices concerned listed.
#         Make window disappear if click on same category.
#         """
# 
#         if self.dockWidget_NodeTypes.windowTitle() == type:
#             self.dockWidget_NodeTypes.setVisible(False)
#             self.dockWidget_NodeTypes.setWindowTitle('')
#         else:
#             self.dockWidget_NodeTypes.setWindowTitle(type)
#             self.dockWidget_NodeTypes.setVisible(True)
#             self.nodesDock.clear()
#             self.nodesDock.populateNodeDock(type)

    def _browseRoutersActionSlot(self):
        """
        Slot to browse all the routers.
        """

        #TODO
        pass

    def _browseSwitchesActionSlot(self):
        """
        Slot to browse all the switches.
        """

        #TODO
        pass

    def _browseEndDevicesActionSlot(self):
        """
        Slot to browse all the end devices.
        """

        #TODO
        pass

    def _browseSecurityDevicesActionSlot(self):
        """
        Slot to browse all the security devices.
        """

        #TODO
        pass

    def _browseAllDevicesActionSlot(self):
        """
        Slot to browse all the devices.
        """

        #TODO
        pass

    def _addLinkActionSlot(self):
        """
        Slot to receive events from the add a link action.
        """

        if not self.uiAddLinkAction.isChecked():
            self.uiAddLinkAction.setText("Add a link")
            link_icon = QtGui.QIcon()
            link_icon.addPixmap(QtGui.QPixmap(":/icons/connection-new.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            link_icon.addPixmap(QtGui.QPixmap(":/icons/connection-new-hover.svg"), QtGui.QIcon.Active, QtGui.QIcon.On)
            self.uiAddLinkAction.setIcon(link_icon)
            self.adding_link_signal.emit(False)
        else:
#TODO: handle automatic linking based on the link type
#             modifiers = QtGui.QApplication.keyboardModifiers()
#             if not globals.GApp.systconf['general'].manual_connection or modifiers == QtCore.Qt.ShiftModifier:
#                 menu = QtGui.QMenu()
#                 for linktype in globals.linkTypes.keys():
#                     menu.addAction(linktype)
#                 menu.connect(menu, QtCore.SIGNAL("triggered(QAction *)"), self.__setLinkType)
#                 menu.exec_(QtGui.QCursor.pos())
#             else:
#                 globals.currentLinkType = globals.Enum.LinkType.Manual
            self.uiAddLinkAction.setText("Cancel")
            self.uiAddLinkAction.setIcon(QtGui.QIcon(':/icons/cancel-connection.svg'))
            self.adding_link_signal.emit(True)

    def _preferencesActionSlot(self):
        """
        Slot to show the preferences dialog.
        """

        dialog = PreferencesDialog(self)
        dialog.show()
        dialog.exec_()

    def keyPressEvent(self, event):
        """
        Handles all key press events for the main window.

        :param event: QKeyEvent
        """

        key = event.key()
        # if the user is adding a link and press Escape, then cancel the link addition.
        if self.uiAddLinkAction.isChecked() and key == QtCore.Qt.Key_Escape:
            self.uiAddLinkAction.setChecked(False)
            self._addLinkActionSlot()
        else:
            QtGui.QMainWindow.keyPressEvent(self, event)

    def closeEvent(self, event):
        """
        Handles the event when the main window is closed.

        :param event: QCloseEvent
        """

        if self.checkForUnsavedChanges():

            # save the geometry and state of the main window.
            settings = QtCore.QSettings()
            settings.setValue("GUI/geometry", self.saveGeometry())
            settings.setValue("GUI/state", self.saveState())
            event.accept()

            servers = Servers.instance()
            servers.stopLocalServer()
        else:
            event.ignore()

    def rebootSlot(self):
        """
        Slot to receive the reboot signal.
        """

        QtGui.QApplication.exit(self.exit_code_reboot)

    def checkForUnsavedChanges(self):
        """
        Checks if there are any unsaved changes.

        :returns: boolean
        """

        if self.testAttribute(QtCore.Qt.WA_WindowModified):
            if self._temporary_project:
                destination_file = "untitled.net"
            else:
                destination_file = os.path.basename(self._project_path)
            reply = QtGui.QMessageBox.warning(self, "Unsaved changes", 'Save changes to project "{}" before closing?'.format(destination_file),
                                              QtGui.QMessageBox.Discard | QtGui.QMessageBox.Save | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Save:
                if self._temporary_project:
                    return self._saveProjectAs()
                return self._saveProject(self._project_path)
            elif reply == QtGui.QMessageBox.Cancel:
                return False
        self._deleteTemporaryProject()
        return True

    def startupLoading(self):
        """
        Called by QTimer.singleShot to load everything needed at startup.
        """

        self._createTemporaryProject()

        # connect to the local server
        servers = Servers.instance()
        server = servers.localServer()

        if not server.connected():
            try:
                server.connect()
                log.info("use an already started local server on {}:{}".format(server.host, server.port))
            except socket.error as e:
                log.info("starting local server {} on {}:{}".format(servers.localServerPath(), server.host, server.port))
                if servers.startLocalServer(servers.localServerPath(), server.host, server.port):
                    thread = WaitForConnectionThread(server.host, server.port)
                    dialog = ProgressDialog(thread, "Local server", "Connecting...", "Cancel", busy=True, parent=self)
                    dialog.show()
                    if dialog.exec_() == False:
                        return
                else:
                    QtGui.QMessageBox.critical(self, "Local server", "Could not start the local server process: {}".format(servers.localServerPath()))
                    return
                try:
                    server.connect()
                except socket.error as e:
                    QtGui.QMessageBox.critical(self, "Local server", "Could not connect to the local server {host} on port {port}: {error}".format(host=server.host,
                                                                                                                                                   port=server.port,
                                                                                                                                                   error=e))

    def _saveProjectAs(self):
        """
        Saves a project to another location/name.
        """

        # first check if any node that can be started is running
        topology = Topology.instance()
        running_nodes = []
        for node in topology.nodes():
            if hasattr(node, "start") and node.status() == Node.started:
                running_nodes.append(node.name())

        if running_nodes:
            nodes = "\n".join(running_nodes)
            MessageBox(self, "Save project", "Please stop the following nodes before saving the topology", nodes)
            return

        if self._temporary_project:
            destination_file = os.path.join(self._settings["projects_path"], "untitled.net")
        else:
            destination_file = os.path.join(self._settings["projects_path"], os.path.basename(self._project_path))
        path = QtGui.QFileDialog.getSaveFileName(self, "Save project", destination_file, "NET File (*.net)")
        if not path:
            return False

        new_project_files_dir = path
        if path.endswith(".net"):
            new_project_files_dir = path[:-4]
        else:
            path = path + ".net"
        new_project_files_dir += "-files"

        if self._temporary_project:
            # move files if saving from a temporary project
            log.info("moving project files from {} to {}".format(self._project_files_dir, new_project_files_dir))
            thread = ProcessFilesThread(self._project_files_dir, new_project_files_dir, move=True)
            dialog = ProgressDialog(thread, "Project", "Moving project files...", "Cancel", parent=self)
        else:
            # else, just copy the files
            log.info("copying project files from {} to {}".format(self._project_files_dir, new_project_files_dir))
            thread = ProcessFilesThread(self._project_files_dir, new_project_files_dir)
            dialog = ProgressDialog(thread, "Project", "Copying project files...", "Cancel", parent=self)
        dialog.show()
        if not dialog.exec_():
            return False

        self._deleteTemporaryProject()
        self._project_files_dir = new_project_files_dir
        self.uiGraphicsView.setLocalBaseWorkingDirtoAllModules(self._project_files_dir)
        return self._saveProject(path)

    def _saveProject(self, path):
        """
        Saves a project.

        :param path: path to project file
        """

        topology = Topology.instance()
        try:
            with open(path, "w") as f:
                log.info("saving project: {}".format(path))
                json.dump(topology.dump(), f, sort_keys=True, indent=4)
        except EnvironmentError as e:
            QtGui.QMessageBox.critical(self, "Save", "Could not save project to {}: {}".format(path, e))
            return False

        self.uiStatusBar.showMessage("Project saved to {}".format(path), 2000)
        self._project_path = path
        self._setCurrentFile(path)
        return True

    def _loadProject(self, path):
        """
        Loads a project into GNS3.

        :param path: path to project file
        """

        self.uiGraphicsView.reset()

        project_files_dir = path
        if path.endswith(".net"):
            project_files_dir = path[:-4]
        self._project_files_dir = project_files_dir + "-files"

        if not os.path.exists(self._project_files_dir):
            QtGui.QMessageBox.warning(self, "Load", "Project files directory doesn't exist: {}".format(self._project_files_dir))

        self.uiGraphicsView.setLocalBaseWorkingDirtoAllModules(self._project_files_dir)

        topology = Topology.instance()
        try:
            with open(path, "r") as f:
                log.info("loading project: {}".format(path))
                topology.load(json.load(f))
        except EnvironmentError as e:
            QtGui.QMessageBox.critical(self, "Load", "Could not load project from {}: {}".format(path, e))
            return False
        except ValueError as e:
            QtGui.QMessageBox.critical(self, "Load", "Invalid file: {}".format(e))
            return False

        self.uiStatusBar.showMessage("Project loaded {}".format(path), 2000)
        self._project_path = path
        self._setCurrentFile(path)

    def _deleteTemporaryProject(self):
        """
        Deletes a temporary project.
        """

        if self._temporary_project and self._project_path:
            # delete the temporary project files
            log.info("deleting temporary project files directory: {}".format(self._project_files_dir))
            shutil.rmtree(self._project_files_dir, ignore_errors=True)
            try:
                log.info("deleting temporary topology file: {}".format(self._project_path))
                os.remove(self._project_path)
            except EnvironmentError as e:
                log.warning("could not delete temporary topology file: {}: e".format(self._project_path, e))

    def _createTemporaryProject(self):
        """
        Creates a temporary project.
        """

        self.uiGraphicsView.reset()
        try:
            with tempfile.NamedTemporaryFile(prefix="gns3-", suffix=".net", delete=False) as f:
                log.info("creating temporary topology file: {}".format(f.name))
                project_files_dir = f.name[:-4] + "-files"
                if not os.path.exists(project_files_dir):
                    log.info("creating temporary project files directory: {}".format(project_files_dir))
                    os.mkdir(project_files_dir)

                self._project_files_dir = project_files_dir
                self._project_path = f.name

        except EnvironmentError as e:
            QtGui.QMessageBox.critical(self, "Save", "Could not create project: {}".format(e))

        self.uiGraphicsView.setLocalBaseWorkingDirtoAllModules(self._project_files_dir)
        self._setCurrentFile()

    def _setCurrentFile(self, path=None):
        """
        Sets the current project file path.

        :param path: path to project file
        """

        if not path:
            self._temporary_project = True
            self.setWindowFilePath("Unsaved project")
        else:
            self._temporary_project = False
            self.setWindowFilePath(path)
        self.setWindowModified(False)
        self.uiSaveProjectAction.setEnabled(False)

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of MainWindow.

        :returns: instance of MainWindow
        """

        if not hasattr(MainWindow, "_instance"):
            MainWindow._instance = MainWindow()
        return MainWindow._instance
