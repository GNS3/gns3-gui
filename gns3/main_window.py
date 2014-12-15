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

import traceback
import sys
import os
import platform
import time
import tempfile
import socket
import shutil
import json
import glob
import logging
import functools
import posixpath
import stat

from pkg_resources import parse_version

from .modules import MODULES
from .version import __version__
from .qt import QtGui, QtCore, QtNetwork
from .servers import Servers
from .node import Node
from .ui.main_window_ui import Ui_MainWindow
from .dialogs.about_dialog import AboutDialog
from .dialogs.new_project_dialog import NewProjectDialog
from .dialogs.preferences_dialog import PreferencesDialog
from .dialogs.snapshots_dialog import SnapshotsDialog
from .dialogs.import_cloud_project_dialog import ImportCloudProjectDialog
from .settings import GENERAL_SETTINGS, GENERAL_SETTING_TYPES, CLOUD_SETTINGS, CLOUD_SETTINGS_TYPES, ENABLE_CLOUD
from .utils.progress_dialog import ProgressDialog
from .utils.process_files_thread import ProcessFilesThread
from .utils.wait_for_connection_thread import WaitForConnectionThread
from .utils.message_box import MessageBox
from .utils.analytics import AnalyticsClient
from .ports.port import Port
from .items.node_item import NodeItem
from .items.link_item import LinkItem
from .items.shape_item import ShapeItem
from .items.image_item import ImageItem
from .items.note_item import NoteItem
from .topology import Topology
from .cloud.utils import UploadProjectThread, UploadFilesThread, ssh_client, DownloadImagesThread, DeleteInstanceThread
from .cloud.rackspace_ctrl import get_provider
from .cloud.exceptions import KeyPairExists
from .cloud_instances import CloudInstances


log = logging.getLogger(__name__)

CLOUD_SETTINGS_GROUP = "Cloud"


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

    # signal to tell a project was closed
    project_about_to_close_signal = QtCore.pyqtSignal(str)
    # signal to tell a new project was created
    project_new_signal = QtCore.pyqtSignal(str)

    def __init__(self, project, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        MainWindow._instance = self

        self._settings = {}
        self._project_from_cmdline = project
        self._cloud_settings = {}
        self._loadSettings()
        self._connections()
        self._ignore_unsaved_state = False
        self._temporary_project = True
        self._max_recent_files = 5
        self._recent_file_actions = []
        self._start_time = time.time()

        self._project_settings = {
            "project_name": "unsaved",
            "project_path": None,
            "project_files_dir": None,
            "project_type": "local",
        }

        try:
            from .news_dock_widget import NewsDockWidget
            self._uiNewsDockWidget = NewsDockWidget(self)
            self.addDockWidget(QtCore.Qt.DockWidgetArea(QtCore.Qt.RightDockWidgetArea), self._uiNewsDockWidget)
        except ImportError:
            self._uiNewsDockWidget = None

        # restore the geometry and state of the main window.
        settings = QtCore.QSettings()
        self.restoreGeometry(settings.value("GUI/geometry", QtCore.QByteArray()))
        self.restoreState(settings.value("GUI/state", QtCore.QByteArray()))

        # do not show the nodes dock widget my default
        if not ENABLE_CLOUD:
            self.uiNodesDockWidget.setVisible(False)

        # populate the view -> docks menu
        self.uiDocksMenu.addAction(self.uiTopologySummaryDockWidget.toggleViewAction())
        self.uiDocksMenu.addAction(self.uiConsoleDockWidget.toggleViewAction())
        self.uiDocksMenu.addAction(self.uiNodesDockWidget.toggleViewAction())
        if ENABLE_CLOUD:
            self.uiDocksMenu.addAction(self.uiCloudInspectorDockWidget.toggleViewAction())

        # set the images directory
        self.uiGraphicsView.updateImageFilesDir(self.imagesDirPath())

        # add recent file actions to the File menu
        for i in range(0, self._max_recent_files):
            action = QtGui.QAction(self.uiFileMenu)
            action.setVisible(False)
            action.triggered.connect(self.openRecentFileSlot)
            self._recent_file_actions.append(action)
        self.uiFileMenu.insertActions(self.uiQuitAction, self._recent_file_actions)
        self._recent_file_actions_separator = self.uiFileMenu.insertSeparator(self.uiQuitAction)
        self._recent_file_actions_separator.setVisible(False)
        self._updateRecentFileActions()

        self._cloud_provider = None
        CloudInstances.instance().clear()
        CloudInstances.instance().load()

        # set the window icon
        self.setWindowIcon(QtGui.QIcon(":/images/gns3.ico"))

        # Network Manager (used to check for update)
        self._network_manager = QtNetwork.QNetworkAccessManager(self)

        # load initial stuff once the event loop isn't busy
        QtCore.QTimer.singleShot(0, self.startupLoading)

    @property
    def cloudProvider(self):
        if self._cloud_provider is None:
            self._cloud_provider = get_provider(self.cloudSettings())
        return self._cloud_provider

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # restore the general settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in GENERAL_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=GENERAL_SETTING_TYPES[name])
        settings.endGroup()

        # restore cloud settings
        settings.beginGroup(CLOUD_SETTINGS_GROUP)
        for name, value in CLOUD_SETTINGS.items():
            self._cloud_settings[name] = settings.value(name, value, type=CLOUD_SETTINGS_TYPES[name])
        settings.endGroup()

        # restore the style
        self._setStyle(self._settings["style"])

        # restore packet capture settings
        Port.loadPacketCaptureSettings()

    def settings(self):
        """
        Returns the general settings.

        :returns: settings dictionary
        """

        return self._settings

    def projectSettings(self):
        """
        Returns the project settings.

        :returns: project settings dictionary
        """

        return self._project_settings

    def cloudSettings(self):
        """
        Returns the cloud settings.

        :returns: cloud settings dictionary
        """

        return self._cloud_settings

    def setSettings(self, new_settings):
        """
        Set new general settings.

        :param new_settings: settings dictionary
        """

        # set a new images directory
        if new_settings.get("images_path", '') != self.imagesDirPath():
            self.uiGraphicsView.updateImageFilesDir(self.imagesDirPath())

        style = new_settings.get("style")
        if style and new_settings["style"] != self._settings["style"]:
            if not self._setStyle(style):
                self._setLegacyStyle()

        # save the settings
        self._settings.update(new_settings)
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in self._settings.items():
            settings.setValue(name, value)
        settings.endGroup()

    def setCloudSettings(self, new_settings, persist):
        """
        Set new cloud settings and store them only when the user asks for it

        :param new_settings: cloud settings dictionary
        :param persist: whether to persist settings on disk or not
        """

        self._cloud_settings.update(new_settings)

        settings = QtCore.QSettings()
        settings.beginGroup(CLOUD_SETTINGS_GROUP)

        settings_to_persist = self._cloud_settings if persist else CLOUD_SETTINGS
        for name, value in settings_to_persist.items():
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
        self.uiOpenProjectAction.triggered.connect(self.openProjectActionSlot)
        self.uiSaveProjectAction.triggered.connect(self._saveProjectActionSlot)
        self.uiSaveProjectAsAction.triggered.connect(self._saveProjectAsActionSlot)
        self.uiExportProjectAction.triggered.connect(self._exportProjectActionSlot)
        self.uiImportProjectAction.triggered.connect(self._importProjectActionSlot)
        self.uiMoveLocalProjectToCloudAction.triggered.connect(self._moveLocalProjectToCloudActionSlot)
        self.uiMoveCloudProjectToLocalAction.triggered.connect(self._moveCloudProjectToLocalActionSlot)
        self.uiImportExportConfigsAction.triggered.connect(self._importExportConfigsActionSlot)
        self.uiScreenshotAction.triggered.connect(self._screenshotActionSlot)
        self.uiSnapshotAction.triggered.connect(self._snapshotActionSlot)

        # edit menu connections
        self.uiSelectAllAction.triggered.connect(self._selectAllActionSlot)
        self.uiSelectNoneAction.triggered.connect(self._selectNoneActionSlot)
        self.uiPreferencesAction.triggered.connect(self._preferencesActionSlot)

        # view menu connections
        self.uiActionFullscreen.triggered.connect(self._fullScreenActionSlot)
        self.uiZoomInAction.triggered.connect(self._zoomInActionSlot)
        self.uiZoomOutAction.triggered.connect(self._zoomOutActionSlot)
        self.uiZoomResetAction.triggered.connect(self._zoomResetActionSlot)
        self.uiFitInViewAction.triggered.connect(self._fitInViewActionSlot)
        self.uiShowLayersAction.triggered.connect(self._showLayersActionSlot)
        self.uiResetPortLabelsAction.triggered.connect(self._resetPortLabelsActionSlot)
        self.uiShowNamesAction.triggered.connect(self._showNamesActionSlot)
        self.uiShowPortNamesAction.triggered.connect(self._showPortNamesActionSlot)

        # control menu connections
        self.uiStartAllAction.triggered.connect(self._startAllActionSlot)
        self.uiSuspendAllAction.triggered.connect(self._suspendAllActionSlot)
        self.uiStopAllAction.triggered.connect(self._stopAllActionSlot)
        self.uiReloadAllAction.triggered.connect(self._reloadAllActionSlot)
        self.uiAuxConsoleAllAction.triggered.connect(self._auxConsoleAllActionSlot)
        self.uiConsoleAllAction.triggered.connect(self._consoleAllActionSlot)

        # device menu is contextual and is build on-the-fly
        self.uiDeviceMenu.aboutToShow.connect(self._deviceMenuActionSlot)

        # annotate menu connections
        self.uiAddNoteAction.triggered.connect(self._addNoteActionSlot)
        self.uiInsertImageAction.triggered.connect(self._insertImageActionSlot)
        self.uiDrawRectangleAction.triggered.connect(self._drawRectangleActionSlot)
        self.uiDrawEllipseAction.triggered.connect(self._drawEllipseActionSlot)

        # help menu connections
        self.uiOnlineHelpAction.triggered.connect(self._onlineHelpActionSlot)
        self.uiCheckForUpdateAction.triggered.connect(self._checkForUpdateActionSlot)
        self.uiGettingStartedAction.triggered.connect(self._gettingStartedActionSlot)
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

        # project
        self.project_about_to_close_signal.connect(self.shutdown_cloud_instances)
        self.project_new_signal.connect(self.project_created)

        # cloud inspector
        self.CloudInspectorView.instanceSelected.connect(self._cloud_instance_selected)

    def telnetConsoleCommand(self):
        """
        Returns the Telnet console command line.

        :returns: command (string)
        """

        return self._settings["telnet_console_command"]

    def serialConsoleCommand(self):
        """
        Returns the Serial console command line.

        :returns: command (string)
        """

        return self._settings["serial_console_command"]

    def setUnsavedState(self):
        """
        Sets the project in a unsaved state.
        """

        if not self._ignore_unsaved_state:
            self.setWindowModified(True)

    def ignoreUnsavedState(self, value):
        """
        Activates or deactivates the possibility to
        set the project in unsaved state.

        :param value: boolean
        """

        self._ignore_unsaved_state = value

    def _createNewProject(self, new_project_settings):
        """
        Creates a new project.

        :param new_project_settings: project settings (dict)
        """

        self.uiGraphicsView.reset()
        # create the destination directory for project files
        try:
            os.makedirs(new_project_settings["project_files_dir"])
        except FileExistsError:
            pass
        except OSError as e:
            QtGui.QMessageBox.critical(self, "New project", "Could not create project files directory {}: {}".format(new_project_settings["project_files_dir"]), str(e))
            return

        # let all modules know about the new project files directory
        self.uiGraphicsView.updateProjectFilesDir(new_project_settings["project_files_dir"])

        topology = Topology.instance()
        for instance in CloudInstances.instance().instances:
            topology.addInstance2(instance)

        self._project_settings.update(new_project_settings)
        self.saveProject(new_project_settings["project_path"])

    def _newProjectActionSlot(self):
        """
        Slot called to create a new project.
        """

        if self.checkForUnsavedChanges():
            project_dialog = NewProjectDialog(self)
            project_dialog.show()
            create_new_project = project_dialog.exec_()
            # Close the device dock so it repopulates.  Done in case switching
            # between cloud and local.
            self.uiNodesDockWidget.setVisible(False)
            self.uiNodesDockWidget.setWindowTitle("")

            self.project_about_to_close_signal.emit(self._project_settings["project_path"])

            if create_new_project:
                new_project_settings = project_dialog.getNewProjectSettings()
                self._createNewProject(new_project_settings)
            else:
                self._createTemporaryProject()

            self.project_new_signal.emit(self._project_settings["project_path"])

    def openProjectActionSlot(self):
        """
        Slot called to open a project.
        """

        path, _ = QtGui.QFileDialog.getOpenFileNameAndFilter(self,
                                                             "Open project",
                                                             self.projectsDirPath(),
                                                             "All files (*.*);;GNS3 project files (*.gns3);;NET files (*.net)",
                                                             "GNS3 project files (*.gns3)")
        if path and self.checkForUnsavedChanges():
            self.project_about_to_close_signal.emit(self._project_settings["project_path"])
            if self.loadProject(path):
                self.project_new_signal.emit(path)

    def openRecentFileSlot(self):
        """
        Slot called to open recent file from the File menu.
        """

        action = self.sender()
        if action:
            path = action.data()
            if not os.path.isfile(path):
                QtGui.QMessageBox.critical(self, "Recent file", "{}: no such file".format(path))
                return
            if self.checkForUnsavedChanges():
                self.project_about_to_close_signal.emit(self._project_settings["project_path"])
                if self.loadProject(path):
                    self.project_new_signal.emit(path)

    def _saveProjectActionSlot(self):
        """
        Slot called to save a project.
        """

        if self._temporary_project:
            return self.saveProjectAs()
        else:
            return self.saveProject(self._project_settings["project_path"])

    def _saveProjectAsActionSlot(self):
        """
        Slot called to save a project to another location/name.
        """

        self.saveProjectAs()

    def _importExportConfigsActionSlot(self):
        """
        Slot called when importing and exporting configs
        for the entire topology.
        """

        options = ["Export configs to a directory", "Import configs from a directory"]
        selection, ok = QtGui.QInputDialog.getItem(self, "Import/Export configs", "Please choose an option:", options, 0, False)
        if ok:
            if selection == options[0]:
                self._exportConfigs()
            else:
                self._importConfigs()

    def _exportConfigs(self):
        """
        Exports all configs to a directory.
        """

        path = QtGui.QFileDialog.getExistingDirectory(self, "Export directory", ".", QtGui.QFileDialog.ShowDirsOnly)
        if path:
            for module in MODULES:
                instance = module.instance()
                if hasattr(instance, "exportConfigs"):
                    instance.exportConfigs(path)

    def _importConfigs(self):
        """
        Imports all configs from a directory.
        """

        path = QtGui.QFileDialog.getExistingDirectory(self, "Import directory", ".", QtGui.QFileDialog.ShowDirsOnly)
        if path:
            for module in MODULES:
                instance = module.instance()
                if hasattr(instance, "importConfigs"):
                    instance.importConfigs(path)

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

        path, selected_filter = QtGui.QFileDialog.getSaveFileNameAndFilter(self, "Screenshot", self.projectsDirPath(), file_formats)
        if not path:
            return

        # add the extension if missing
        file_format = "." + selected_filter[:4].lower().strip()
        if not path.endswith(file_format):
            path += file_format

        if not self._createScreenshot(path):
            QtGui.QMessageBox.critical(self, "Screenshot", "Could not create screenshot file {}".format(path))

    def _snapshotActionSlot(self):
        """
        Slot called to open the snapshot dialog.
        """

        # first check if any node doesn't run locally
        topology = Topology.instance()
        for node in topology.nodes():
            if node.server() != Servers.instance().localServer():
                QtGui.QMessageBox.critical(self, "Snapshots", "Snapshot can only be created if all the nodes run locally")
                return

        dialog = SnapshotsDialog(self,
                                 self._project_settings["project_path"],
                                 self._project_settings["project_files_dir"])
        dialog.show()
        dialog.exec_()

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

    def _fullScreenActionSlot(self):
        """
        Slot to switch to full screen.
        """

        if not self.windowState() & QtCore.Qt.WindowFullScreen:
            # switch to full screen
            self.setWindowState(self.windowState() | QtCore.Qt.WindowFullScreen)
        else:
            # switch back to normal
            self.setWindowState(self.windowState() & ~QtCore.Qt.WindowFullScreen)

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

        NodeItem.show_layer = self.uiShowLayersAction.isChecked()
        ShapeItem.show_layer = self.uiShowLayersAction.isChecked()
        ImageItem.show_layer = self.uiShowLayersAction.isChecked()
        NoteItem.show_layer = self.uiShowLayersAction.isChecked()
        for item in self.uiGraphicsView.items():
            item.update()

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

    def _showPortNamesActionSlot(self):
        """
        Slot called to show the port names on the scene.
        """

        LinkItem.showPortLabels(self.uiShowPortNamesAction.isChecked())
        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, LinkItem):
                item.adjust()

    def _startAllActionSlot(self):
        """
        Slot called when starting all the nodes.
        """

        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "start") and item.node().initialized():
                item.node().start()

    def _suspendAllActionSlot(self):
        """
        Slot called when suspending all the nodes.
        """

        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "suspend") and item.node().initialized():
                item.node().suspend()

    def _stopAllActionSlot(self):
        """
        Slot called when stopping all the nodes.
        """

        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "stop") and item.node().initialized():
                item.node().stop()

    def _reloadAllActionSlot(self):
        """
        Slot called when reloading all the nodes.
        """

        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "reload") and item.node().initialized():
                item.node().reload()

    def _deviceMenuActionSlot(self):
        """
        Slot to contextually show the device menu.
        """

        self.uiDeviceMenu.clear()
        self.uiGraphicsView.populateDeviceContextualMenu(self.uiDeviceMenu)

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

        delay = self._settings["delay_console_all"]
        counter = 0
        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "console") and item.node().initialized() and item.node().status() == Node.started:
                callback = functools.partial(self.uiGraphicsView.consoleToNode, item.node())
                QtCore.QTimer.singleShot(counter, callback)
                counter += delay

    def _addNoteActionSlot(self):
        """
        Slot called when adding a new note on the scene.
        """

        self.uiGraphicsView.addNote(self.uiAddNoteAction.isChecked())

    def _insertImageActionSlot(self):
        """
        Slot called when inserting an image on the scene.
        """

        # supported image file formats
        file_formats = "PNG File (*.png);;JPG File (*.jpeg *.jpg);;BMP File (*.bmp);;XPM File (*.xpm *.xbm);;PPM File (*.ppm);;TIFF File (*.tiff);;All files (*.*)"

        path = QtGui.QFileDialog.getOpenFileName(self, "Image", self.projectsDirPath(), file_formats)
        if not path:
            return

        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            QtGui.QMessageBox.critical(self, "Image", "Image file format not supported")
            return

        destination_dir = os.path.join(self._project_settings["project_files_dir"], "images")
        try:
            os.makedirs(destination_dir)
        except FileExistsError:
            pass
        except OSError as e:
            QtGui.QMessageBox.critical(self, "Image", "Could not create the image directory: {}".format(e))
            return

        destination_image_path = os.path.join(destination_dir, os.path.basename(path))
        if not os.path.isfile(destination_image_path):
            # copy the image to the project files directory
            try:
                shutil.copyfile(path, destination_image_path)
            except OSError as e:
                QtGui.QMessageBox.critical(self, "Image", "Could not copy the image to the project image directory: {}".format(e))
                return

        self.uiGraphicsView.addImage(pixmap, destination_image_path)

    def _drawRectangleActionSlot(self):
        """
        Slot called when adding a rectangle on the scene.
        """

        self.uiGraphicsView.addRectangle(self.uiDrawRectangleAction.isChecked())

    def _drawEllipseActionSlot(self):
        """
        Slot called when adding a ellipse on the scene.
        """

        self.uiGraphicsView.addEllipse(self.uiDrawEllipseAction.isChecked())

    def _onlineHelpActionSlot(self):
        """
        Slot to launch a browser pointing to the documentation page.
        """

        QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://www.gns3.net/documentation/"))

    def _checkForUpdateActionSlot(self, silent=False):
        """
        Slot to check if a newer version is available.

        :param silent: do not display any message
        """

        request = QtNetwork.QNetworkRequest(QtCore.QUrl("http://update.gns3.net/"))
        request.setRawHeader("User-Agent", "GNS3 Check For Update")
        request.setAttribute(QtNetwork.QNetworkRequest.User, silent)
        reply = self._network_manager.get(request)
        reply.finished.connect(self._checkForUpdateReplySlot)

    def _checkForUpdateReplySlot(self):
        """
        Process reply for check for update.
        """

        network_reply = self.sender()
        is_silent = network_reply.request().attribute(QtNetwork.QNetworkRequest.User)

        if network_reply.error() != QtNetwork.QNetworkReply.NoError and not is_silent:
            QtGui.QMessageBox.critical(self, "Check For Update", "Cannot check for update: {}".format(network_reply.errorString()))
        else:
            latest_release = bytes(network_reply.readAll()).decode().rstrip()
            if parse_version(__version__) < parse_version(latest_release):
                    reply = QtGui.QMessageBox.question(self,
                                                       "Check For Update",
                                                       "Newer GNS3 version {} is available, do you want to visit our website to download it?".format(latest_release),
                                                       QtGui.QMessageBox.Yes,
                                                       QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://www.gns3.net/download/"))
            elif not is_silent:
                QtGui.QMessageBox.information(self, "Check For Update", "GNS3 is up-to-date!")
            return

        network_reply.deleteLater()

    def _gettingStartedActionSlot(self, auto=False):
        """
        Slot to open the news dialog.
        """

        try:
            # QtWebKit which is used by GettingStartedDialog is not installed
            # by default on FreeBSD, Solaris and possibly other systems.
            from .dialogs.getting_started_dialog import GettingStartedDialog
        except ImportError:
            return

        dialog = GettingStartedDialog(self)
        if auto is True and dialog.showit() is False:
            return
        dialog.show()
        dialog.exec_()

    def _labInstructionsActionSlot(self, silent=False):
        """
        Slot to open lab instructions.
        """

        project_dir = os.path.dirname(self._project_settings["project_path"])
        instructions_files = glob.glob(project_dir + os.sep + "instructions.*")
        instructions_files += glob.glob(os.path.join(project_dir, "instructions") + os.sep + "instructions*")
        if len(instructions_files):
            path = instructions_files[0]
            if QtGui.QDesktopServices.openUrl(QtCore.QUrl('file:///' + path, QtCore.QUrl.TolerantMode)) == False and silent == False:
                QtGui.QMessageBox.critical(self, "Lab instructions", "Could not open {}".format(path))
        elif silent is False:
            QtGui.QMessageBox.critical(self, "Lab instructions", "No instructions found")


    def _aboutQtActionSlot(self):
        """
        Slot to display the Qt About dialog.
        """

        QtGui.QMessageBox.aboutQt(self)

    def _aboutActionSlot(self):
        """
        Slot to display the GNS3 About dialog.
        """

        dialog = AboutDialog(self)
        dialog.show()
        dialog.exec_()

    def _showNodesDockWidget(self, title, category=None):
        """
        Makes the NodesDockWidget appear with the appropriate title and the devices
        from the specified category listed.
        Makes the dock disappear if the same category is selected.

        :param title: NodesDockWidget title
        :param category: category of device to list
        """

        if self.uiNodesDockWidget.windowTitle() == title:
            self.uiNodesDockWidget.setVisible(False)
            self.uiNodesDockWidget.setWindowTitle("")
        else:
            self.uiNodesDockWidget.setWindowTitle(title)
            self.uiNodesDockWidget.setVisible(True)
            self.uiNodesView.clear()
            self.uiNodesView.populateNodesView(category, self._project_settings["project_type"])

    def _browseRoutersActionSlot(self):
        """
        Slot to browse all the routers.
        """

        self._showNodesDockWidget("Routers", Node.routers)

    def _browseSwitchesActionSlot(self):
        """
        Slot to browse all the switches.
        """

        self._showNodesDockWidget("Switches", Node.switches)

    def _browseEndDevicesActionSlot(self):
        """
        Slot to browse all the end devices.
        """

        self._showNodesDockWidget("End devices", Node.end_devices)

    def _browseSecurityDevicesActionSlot(self):
        """
        Slot to browse all the security devices.
        """

        self._showNodesDockWidget("Security devices", Node.security_devices)

    def _browseAllDevicesActionSlot(self):
        """
        Slot to browse all the devices.
        """

        self._showNodesDockWidget("All devices")

    def _addLinkActionSlot(self):
        """
        Slot to receive events from the add a link action.
        """

        if not self.uiAddLinkAction.isChecked():
            self.uiAddLinkAction.setText("Add a link")
            self.adding_link_signal.emit(False)
        else:
            self.uiAddLinkAction.setText("Cancel")
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
            self.project_about_to_close_signal.emit(self._project_settings["project_path"])

            # save the geometry and state of the main window.
            settings = QtCore.QSettings()
            settings.setValue("GUI/geometry", self.saveGeometry())
            settings.setValue("GUI/state", self.saveState())
            event.accept()

            servers = Servers.instance()
            servers.stopLocalServer(wait=True)

            for cs in servers.cloud_servers.values():
                cs.close_connection()

            time_spent = "{:.0f}".format(time.time() - self._start_time)
            AnalyticsClient().send_event("GNS3", "Close", "Version {} on {}".format(__version__, platform.system()), time_spent)
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
                destination_file = "untitled.gns3"
            else:
                destination_file = os.path.basename(self._project_settings["project_path"])
            reply = QtGui.QMessageBox.warning(self, "Unsaved changes", 'Save changes to project "{}" before closing?'.format(destination_file),
                                              QtGui.QMessageBox.Discard | QtGui.QMessageBox.Save | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Save:
                if self._temporary_project:
                    return self.saveProjectAs()
                return self.saveProject(self._project_settings["project_path"])
            elif reply == QtGui.QMessageBox.Cancel:
                return False
        self._deleteTemporaryProject()
        return True

    def startupLoading(self):
        """
        Called by QTimer.singleShot to load everything needed at startup.
        """

        if self._uiNewsDockWidget and not self._uiNewsDockWidget.isVisible():
            self.addDockWidget(QtCore.Qt.DockWidgetArea(QtCore.Qt.RightDockWidgetArea), self._uiNewsDockWidget)

        self._gettingStartedActionSlot(auto=True)

        # connect to the local server
        servers = Servers.instance()
        server = servers.localServer()

        if not server.connected():

            try:
                # check if the local address still exists
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.bind((server.host, 0))
            except OSError as e:
                QtGui.QMessageBox.critical(self, "Local server", "Could not bind with {host}: {error} (please check your host binding setting)".format(host=server.host, error=e))
                return

            try:
                server.connect()
                log.info("use an already started local server on {}:{}".format(server.host, server.port))
            except OSError as e:

                if not e.errno:
                    # not a normal OSError, thrown from the Websocket client.
                    MessageBox(self, "Local server", "Something other than a GNS3 server is already running on {} port {}, please adjust the local server port setting".format(server.host,
                                                                                                                                                                               server.port),
                                                                                                                                                                               str(e))
                    return

                if not servers.localServerAutoStart():
                    return

                log.info("starting local server {} on {}:{}".format(servers.localServerPath(), server.host, server.port))

                local_server_path = servers.localServerPath()

                if not local_server_path:
                    log.info("no local server is configured")
                    return

                if not os.path.isfile(local_server_path):
                    QtGui.QMessageBox.critical(self, "Local server", "Could not find local server {}".format(local_server_path))
                    return

                elif not os.access(local_server_path, os.X_OK):
                    QtGui.QMessageBox.critical(self, "Local server", "{} is not an executable".format(local_server_path))
                    return

                if servers.startLocalServer(servers.localServerPath(), server.host, server.port):
                        self._thread = WaitForConnectionThread(server.host, server.port)
                        progress_dialog = ProgressDialog(self._thread,
                                                         "Local server",
                                                         "Connecting to server {} on port {}...".format(server.host, server.port),
                                                         "Cancel", busy=True, parent=self)
                        progress_dialog.show()
                        if not progress_dialog.exec_():
                            return
                else:
                    QtGui.QMessageBox.critical(self, "Local server", "Could not start the local server process: {}".format(servers.localServerPath()))
                    return
                try:
                    servers.localServer().reconnect()
                except OSError as e:
                    QtGui.QMessageBox.critical(self, "Local server", "Could not connect to the local server {host} on port {port}: {error}".format(host=server.host,
                                                                                                                                                   port=server.port,
                                                                                                                                                   error=e))

        self._createTemporaryProject()
        if self._project_from_cmdline:
            time.sleep(0.5)  # give so time to the server to initialize
            self.loadProject(self._project_from_cmdline)
        elif self._settings["auto_launch_project_dialog"]:
            project_dialog = NewProjectDialog(self, showed_from_startup=True)
            project_dialog.show()
            create_new_project = project_dialog.exec_()
            if create_new_project:
                new_project_settings = project_dialog.getNewProjectSettings()
                self._createNewProject(new_project_settings)
                self.project_new_signal.emit(self._project_settings["project_path"])

        if self._settings["check_for_update"]:
            # automatic check for update every week (604800 seconds)
            current_epoch = int(time.mktime(time.localtime()))
            if current_epoch - self._settings["last_check_for_update"] >= 604800:
                # let's check for an update
                self._checkForUpdateActionSlot(silent=True)
                self._settings["last_check_for_update"] = current_epoch
                self.setSettings(self._settings)

    def saveProjectAs(self):
        """
        Saves a project to another location/name.

        :returns: GNS3 project file (.gns3)
        """

        # first check if any node that can be started is running
        topology = Topology.instance()
        running_nodes = []
        for node in topology.nodes():
            if hasattr(node, "start") and node.status() == Node.started:
                running_nodes.append(node.name())

        if running_nodes:
            nodes = "\n".join(running_nodes)
            MessageBox(self, "Save project", "Please stop the following nodes before saving the topology to a new location", nodes)
            return

        if self._temporary_project:
            default_project_name = "untitled"
        else:
            default_project_name = os.path.basename(self._project_settings["project_path"])
            if default_project_name.endswith(".gns3"):
                default_project_name = default_project_name[:-5]

        try:
            projects_dir_path = self.projectsDirPath()
            os.makedirs(projects_dir_path)
        except FileExistsError:
            pass
        except OSError as e:
            QtGui.QMessageBox.critical(self, "Save project", "Could not create the projects directory {}: {}".format(projects_dir_path, str(e)))
            return

        file_dialog = QtGui.QFileDialog(self)
        file_dialog.setWindowTitle("Save project")
        file_dialog.setNameFilters(["Directories"])
        file_dialog.setDirectory(projects_dir_path)
        file_dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        file_dialog.setLabelText(QtGui.QFileDialog.FileName, "Project name:")
        file_dialog.selectFile(default_project_name)
        file_dialog.setOptions(QtGui.QFileDialog.ShowDirsOnly)
        file_dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        if file_dialog.exec_() == QtGui.QFileDialog.Rejected:
            return

        project_dir = file_dialog.selectedFiles()[0]
        project_name = os.path.basename(project_dir)
        topology_file_path = os.path.join(project_dir, project_name + ".gns3")
        new_project_files_dir = os.path.join(project_dir, project_name + "-files")

        # create the destination directory for project files
        try:
            os.makedirs(new_project_files_dir)
        except FileExistsError:
            pass
        except OSError as e:
            QtGui.QMessageBox.critical(self, "Save project", "Could not create project directory {}: {}".format(new_project_files_dir), str(e))
            return

        # create the sub-directories to avoid race conditions when setting the new working
        # directory to modules (modules could create directories with different ownership)
        for curpath, dirs, _ in os.walk(self._project_settings["project_files_dir"]):
            base_dir = curpath.replace(self._project_settings["project_files_dir"], new_project_files_dir)
            for directory in dirs:
                try:
                    destination_dir = os.path.join(base_dir, directory)
                    os.makedirs(destination_dir)
                except FileExistsError:
                    pass
                except OSError as e:
                    QtGui.QMessageBox.critical(self, "Save project", "Could not create project sub-directory {}: {}".format(destination_dir, str(e)))
                    return

        # let all modules know about the new project files directory
        self.uiGraphicsView.updateProjectFilesDir(new_project_files_dir)

        if self._temporary_project:
            # move files if saving from a temporary project
            log.info("moving project files from {} to {}".format(self._project_settings["project_files_dir"], new_project_files_dir))
            self._thread = ProcessFilesThread(self._project_settings["project_files_dir"], new_project_files_dir, move=True)
            progress_dialog = ProgressDialog(self._thread, "Project", "Moving project files...", "Cancel", parent=self)
        else:
            # else, just copy the files
            log.info("copying project files from {} to {}".format(self._project_settings["project_files_dir"], new_project_files_dir))
            self._thread = ProcessFilesThread(self._project_settings["project_files_dir"], new_project_files_dir)
            progress_dialog = ProgressDialog(self._thread, "Project", "Copying project files...", "Cancel", parent=self)
        progress_dialog.show()
        progress_dialog.exec_()

        errors = progress_dialog.errors()
        if errors:
            errors = "\n".join(errors)
            MessageBox(self, "Save project", "Errors detected while saving the project", errors, icon=QtGui.QMessageBox.Warning)

        self._deleteTemporaryProject()
        self._project_settings["project_files_dir"] = new_project_files_dir
        self._project_settings["project_name"] = project_name
        return self.saveProject(topology_file_path)

    def saveProject(self, path):
        """
        Saves a project.

        :param path: path to project file
        """

        topology = Topology.instance()
        try:
            with open(path, "w") as f:
                log.info("saving project: {}".format(path))
                json.dump(topology.dump(), f, sort_keys=True, indent=4)
        except OSError as e:
            QtGui.QMessageBox.critical(self, "Save", "Could not save project to {}: {}".format(path, e))
            return False

        self.uiStatusBar.showMessage("Project saved to {}".format(path), 2000)
        self._project_settings["project_path"] = path
        self._setCurrentFile(path)
        return True

    def _convertOldProject(self, path):
        """
        Converts old ini-style GNS3 topologies (<=0.8.7) to the newer version 1+ JSON format.

        :param path: path to the project file.
        """

        try:
            from gns3converter.main import do_conversion, get_snapshots, ConvertError
        except ImportError:
            QtGui.QMessageBox.critical(self, "GNS3 converter", "Please install gns3-converter in order to open old ini-style GNS3 projects")
            return

        try:
            project_name = os.path.basename(os.path.dirname(path))
            project_dir = os.path.join(self._settings["projects_path"], project_name)

            while os.path.isdir(project_dir):
                text, ok = QtGui.QInputDialog.getText(self,
                                                      "GNS3 converter",
                                                      "Project '{}' already exists. Please choose an alternative project name:".format(project_name),
                                                      text=project_name + "2")
                if ok:
                    project_name = text
                    project_dir = os.path.join(self._settings["projects_path"], project_name)
                else:
                    return

            for snapshot_def in get_snapshots(path):
                do_conversion(snapshot_def, project_name, project_dir, quiet=True)

            topology_def = {'file': path, 'snapshot': False}
            do_conversion(topology_def, project_name, project_dir, quiet=True)
        except ConvertError as e:
            QtGui.QMessageBox.critical(self, "GNS3 converter", "Could not convert {}: {}".format(path, e))
            return
        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_tb)
            tb = "".join(lines)
            MessageBox(self, "GNS3 converter", "Unexpected exception while converting {}".format(path), details=tb)
            return

        QtGui.QMessageBox.information(self, "GNS3 converter", "Your project has been converted to a new format and can be found in: {}".format(project_dir))
        project_path = os.path.join(project_dir, project_name + ".gns3")
        self.loadProject(project_path)

    def loadProject(self, path):
        """
        Loads a project into GNS3.

        :param path: path to project file
        """

        self.uiGraphicsView.reset()
        topology = Topology.instance()
        try:

            extension = os.path.splitext(path)[1]
            if extension == ".net":
                self._convertOldProject(path)
                return

            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            with open(path, "r") as f:
                need_to_save = False
                log.info("loading project: {}".format(path))
                json_topology = json.load(f)

                project_files_dir = path
                if path.endswith(".gns3"):
                    project_files_dir = path[:-5]
                elif path.endswith(".net"):
                    project_files_dir = path[:-4]
                self._project_settings["project_files_dir"] = project_files_dir + "-files"

                try:
                    os.makedirs(self._project_settings["project_files_dir"])
                except FileExistsError:
                    pass
                except OSError as e:
                    QtGui.QMessageBox.critical(self, "Load project", "Could not create project sub-directory {}: {}".format(self._project_settings["project_files_dir"], e))
                    return

                self.uiGraphicsView.updateProjectFilesDir(self._project_settings["project_files_dir"])

                # if we're opening a cloud project, fire up instances
                if json_topology["resources_type"] == "cloud":
                    self._project_settings["project_type"] = "cloud"
                    # new_instances = []
                    # for instance in json_topology["topology"]["instances"]:
                    #     name = instance["name"]
                    #     flavor = instance["size_id"]
                    #     image = instance["image_id"]
                    #     i, k = self._create_instance(name, flavor, image)
                    #     new_instances.append({
                    #         "name": i.name,
                    #         "id": i.id,
                    #         "size_id": flavor,
                    #         "image_id": image,
                    #         "private_key": k.private_key,
                    #         "public_key": k.public_key
                    #     })
                    # # update topology with new image data
                    # json_topology["topology"]["instances"] = new_instances
                    # # we need to save the updates
                    # need_to_save = True
                else:
                    self._project_settings["project_type"] = "local"

                topology.load(json_topology)

                if need_to_save:
                    self.saveProject(path)
        except OSError as e:
            QtGui.QMessageBox.critical(self, "Load", "Could not load project {}: {}".format(os.path.basename(path), e))
            #log.error("exception {type}".format(type=type(e)), exc_info=1)
            return False
        except ValueError as e:
            QtGui.QMessageBox.critical(self, "Load", "Invalid file: {}".format(e))
            return False
        finally:
            QtGui.QApplication.restoreOverrideCursor()

        self.uiStatusBar.showMessage("Project loaded {}".format(path), 2000)
        self._project_settings["project_path"] = path
        self._setCurrentFile(path)
        self._labInstructionsActionSlot(silent=True)

        return True

    def _deleteTemporaryProject(self):
        """
        Deletes a temporary project.
        """

        if self._temporary_project and self._project_settings["project_path"]:
            # delete the temporary project files
            log.info("deleting temporary project files directory: {}".format(self._project_settings["project_files_dir"]))
            shutil.rmtree(self._project_settings["project_files_dir"], ignore_errors=True)
            try:
                log.info("deleting temporary topology file: {}".format(self._project_settings["project_path"]))
                os.remove(self._project_settings["project_path"])
            except OSError as e:
                log.warning("could not delete temporary topology file: {}: {}".format(self._project_settings["project_path"], e))

    def _createTemporaryProject(self):
        """
        Creates a temporary project.
        """

        self.uiGraphicsView.reset()
        try:
            with tempfile.NamedTemporaryFile(prefix="gns3-", delete=False) as f:
                log.info("creating temporary topology file: {}".format(f.name))
                project_files_dir = f.name + "-files"
                if not os.path.isdir(project_files_dir):
                    log.info("creating temporary project files directory: {}".format(project_files_dir))
                    os.mkdir(project_files_dir)

                self._project_settings["project_files_dir"] = project_files_dir
                self._project_settings["project_path"] = f.name

        except OSError as e:
            QtGui.QMessageBox.critical(self, "Save", "Could not create project: {}".format(e))

        self.uiGraphicsView.updateProjectFilesDir(self._project_settings["project_files_dir"])
        self._setCurrentFile()

    def isTemporaryProject(self):
        """
        Returns either this is a temporary project or not.

        :returns: boolean
        """

        return self._temporary_project

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
            self._updateRecentFileSettings(path)
            self._updateRecentFileActions()

        self.setWindowModified(False)

    def _updateRecentFileSettings(self, path):
        """
        Updates the recent file settings.

        :param path: path to the new file
        """

        recent_files = []
        settings = QtCore.QSettings()

        # read the recent file list
        settings.beginGroup("RecentFiles")
        size = settings.beginReadArray("file")
        for index in range(0, size):
            settings.setArrayIndex(index)
            file_path = settings.value("path", "")
            if file_path:
                recent_files.append(file_path)
        settings.endArray()

        # update the recent file list
        if path in recent_files:
            recent_files.remove(path)
        recent_files.insert(0, path)
        if len(recent_files) > self._max_recent_files:
            recent_files.pop()

        # write the recent file list
        settings.beginWriteArray("file", len(recent_files))
        index = 0
        for file_path in recent_files:
            settings.setArrayIndex(index)
            settings.setValue("path", file_path)
            index += 1
        settings.endArray()
        settings.endGroup()

    def _updateRecentFileActions(self):
        """
        Updates recent file actions.
        """

        settings = QtCore.QSettings()
        settings.beginGroup("RecentFiles")
        size = settings.beginReadArray("file")
        for index in range(0, size):
            settings.setArrayIndex(index)
            file_path = settings.value("path", "")
            if file_path:
                action = self._recent_file_actions[index]
                action.setText(" {}. {}".format(index + 1, os.path.basename(file_path)))
                action.setData(file_path)
                action.setVisible(True)
                index += 1
        settings.endArray()

        for index in range(size + 1, self._max_recent_files):
            self._recent_file_actions[index].setVisible(False)

        if size:
            self._recent_file_actions_separator.setVisible(True)

    def projectsDirPath(self):
        """
        Returns the projects directory path.

        :returns: path to the default projects directory
        """

        return self._settings["projects_path"]

    def imagesDirPath(self):
        """
        Returns the images directory path.

        :returns: path to the default images directory
        """

        return self._settings["images_path"]

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of MainWindow.

        :returns: instance of MainWindow
        """

        if not hasattr(MainWindow, "_instance"):
            MainWindow._instance = MainWindow()
        return MainWindow._instance

    def shutdown_cloud_instances(self, project):
        """
        This slot is invoked before a project is closed, when:
         * a new project is created
         * a project from the recent menu is opened
         * a project is opened from file
         * program exits

        :param project: path to gns3 project file
        """

        if self._temporary_project:
            # do nothing if previous project was temporary
            return

        CloudInstances.instance().save()

    def project_created(self, project):
        """
        This slot is invoked when a project is created or opened

        :param project: path to gns3 project file currently opened
        """
        if self._temporary_project:
            # do nothing if project is temporary
            return

        with open(project) as f:
            json_topology = json.load(f)

            self.CloudInspectorView.clear()

            if json_topology["resources_type"] != 'cloud':
                # do nothing in case of local projects
                return

            project_instances = json_topology["topology"]["instances"]
            self.CloudInspectorView.load(self, [i["id"] for i in project_instances])

    def add_instance_to_project(self, instance, keypair):
        """
        Add an instance to the current project

        :param instance: libcloud Node object
        """
        if instance is None:
            log.error("Failed creating a new instance for current project")
            return

        default_image_id = self.cloudSettings()['default_image']

        topology = Topology.instance()
        topology.addInstance(instance.name, instance.id, instance.extra['flavorId'],
                             default_image_id, keypair.private_key, keypair.public_key)
        self.CloudInspectorView.addInstance(instance)

        # persist infos saving current project
        self.saveProject(self._project_settings["project_path"])

    def remove_instance_from_project(self, instance):
        """
        Remove an instance from the current project

        :param instance: libcloud Node object
        """
        topology = Topology.instance()
        topology.removeInstance(instance.id)
        # persist infos saving current project
        self.saveProject(self._project_settings["project_path"])

    def _create_instance(self, name, flavor, image_id):
        """
        Wrapper method to handle SSH keypairs creation before actually creating
        an instance
        """
        # add -gns3 suffix to image names to minimize clashes on Rackspace accounts
        if not name.endswith("-gns3"):
            name += "-gns3"

        log.debug("Creating cloud keypair with name {}".format(name))
        try:
            keypair = self.cloudProvider.create_key_pair(name)
        except KeyPairExists:
            log.debug("Cloud keypair with name {} exists.  Recreating.".format(name))
            # delete keypairs if they already exist
            self.cloudProvider.delete_key_pair_by_name(name)
            keypair = self.cloudProvider.create_key_pair(name)

        log.debug("Creating cloud server with name {}".format(name))
        instance = self.cloudProvider.create_instance(name, flavor, image_id, keypair)
        log.debug("Cloud server {} created".format(name))
        return instance, keypair

    def _exportProjectActionSlot(self):
        if self._temporary_project:
            # do nothing if project is temporary
            QtGui.QMessageBox.critical(
                self,
                "Backup project",
                "Cannot backup temporary projects, please save current project first."
            )
            return
        if self.checkForUnsavedChanges():
            self.saveProject(self._project_settings["project_path"])

        upload_thread = UploadProjectThread(
            self,
            self._cloud_settings,
            self._project_settings['project_path'],
            self._settings['images_path']
        )
        progress_dialog = ProgressDialog(upload_thread, "Backing Up Project", "Uploading project files...", "Cancel",
                                         parent=self)
        progress_dialog.show()
        progress_dialog.exec_()

    def _importProjectActionSlot(self):
        dialog = ImportCloudProjectDialog(
            self,
            self._settings['projects_path'],
            self._settings['images_path'],
            self._cloud_settings
        )

        dialog.show()
        dialog.exec_()

    def _moveLocalProjectToCloudActionSlot(self):
        if self._temporary_project:
            # do nothing if project is temporary
            QtGui.QMessageBox.critical(
                self,
                "Move project to Cloud",
                "Cannot move temporary projects, please save current project first.")
            return
        if self._project_settings["project_type"] == "cloud":
            # do nothing if project is already a cloud project
            QtGui.QMessageBox.critical(
                self,
                "Move project to Cloud",
                "This project is already a Cloud Project")
            return
        if not self.checkForUnsavedChanges():
            # do nothing if project is already a cloud project
            QtGui.QMessageBox.critical(
                self,
                "Unsaved changes",
                "There are unsaved changes. Please save the project first.")
            return

        # Upload images to cloud storage
        topology = Topology.instance()
        images = set([
            (
                node.settings()['image'],
                'images/' + os.path.relpath(node.settings()['image'], self._settings["images_path"])
            )
            for node in topology.nodes() if 'image' in node.settings()
        ])
        log.debug('uploading images ' + str(images) + ' to cloud')
        upload_thread = UploadFilesThread(self, self._cloud_settings, images)
        upload_images_progress_dialog = ProgressDialog(upload_thread, "Uploading images", "Uploading image files...",
                                                       "Cancel", parent=self)
        upload_images_progress_dialog.show()
        upload_images_progress_dialog.exec_()

        progress_dialog = QtGui.QProgressDialog("Moving project to cloud", "Cancel", 0, 100, self)
        progress_dialog.show()

        def buildComplete(server_id):
            progress_dialog.setValue(80)
            log.debug("websocket connected, server_id=" + str(server_id))

            instance = topology.getInstance(server_id)
            # copy nvram, config, and disk files to server
            with ssh_client(instance.host, instance.private_key) as client:
                log.debug('copying device files to cloud instance')
                sftp = client.open_sftp()

                project_files_dir = os.path.join(
                    os.path.dirname(self._project_settings['project_path']),
                    os.path.basename(os.path.dirname(self._project_settings['project_path'])) + '-files'
                )
                dest_project_path = posixpath.join(
                    '/root/GNS3/projects',
                    os.path.basename(os.path.dirname(self._project_settings['project_path']))
                )

                for root, dirs, files in os.walk(project_files_dir):
                    directory = posixpath.normpath(posixpath.join(
                        dest_project_path,
                        os.path.relpath(root, project_files_dir).replace('\\', '/')
                    ))
                    sftp.mkdir(directory)
                    sftp.chdir(directory)

                    for file in files:
                        local_filepath = os.path.join(root, file)
                        if os.path.isfile(local_filepath) and not self._should_exclude_copying_file(file):
                            log.debug('copying file ' + local_filepath)
                            sftp.put(local_filepath, file)
                            log.debug('copied file successfully')

                sftp.close()

            self._project_settings["project_type"] = "cloud"

            # switch server on all nodes to cloud instance
            server = Servers.instance().anyCloudServer()

            for node in topology.nodes():
                node._server = server

            # reload project
            self.saveProject(self._project_settings["project_path"])
            topology.reset()
            self.loadProject(self._project_settings["project_path"])
            progress_dialog.accept()

        instances = CloudInstances.instance().instances
        for instance in instances:
            topology.addInstance2(instance)
        self.CloudInspectorView.load(self, [i.id for i in topology.instances()])

        # Create a new instance.  At some point we could reuse an existing instance.
        builder = self.CloudInspectorView.createInstance(
            self._project_settings["project_name"],
            self.cloudSettings()['default_flavor'],
            self.cloudSettings()['default_image']
        )
        builder.buildComplete.connect(buildComplete)

    def _moveCloudProjectToLocalActionSlot(self):
        if self._temporary_project:
            # do nothing if project is temporary
            QtGui.QMessageBox.critical(
                self,
                "Move project to local machine",
                "Cannot move temporary projects, please save current project first.")
            return
        if self._project_settings["project_type"] == "local":
            # do nothing if project is already a cloud project
            QtGui.QMessageBox.critical(
                self,
                "Move project to ",
                "This project is already a local project")
            return
        if not self.checkForUnsavedChanges():
            # do nothing if project is already a cloud project
            QtGui.QMessageBox.critical(
                self,
                "Unsaved changes",
                "There are unsaved changes. Please save the project first.")
            return

        topology = Topology.instance()

        # download images from cloud storage
        images = set(
            [posixpath.basename(node.settings()["image"]) for node in topology.nodes() if 'image' in node.settings()]
        )

        log.debug('downloading images ' + str(images))
        download_images_thread = DownloadImagesThread(self._cloud_settings, self._settings['images_path'], images)
        download_images_progress_dialog = ProgressDialog(download_images_thread, "Downloading Images",
                                                         "Downloading images files...", "Cancel", parent=self)
        download_images_progress_dialog.show()
        download_images_progress_dialog.exec_()

        # copy device files from cloud instances
        src_project_path = posixpath.join(
            '/root/GNS3/projects',
            os.path.basename(os.path.dirname(self._project_settings['project_path']))
        )
        project_files_dir = os.path.join(
            os.path.dirname(self._project_settings['project_path']),
            os.path.basename(os.path.dirname(self._project_settings['project_path'])) + '-files'
        )

        for topology_instance in topology.instances():
            log.debug('copying device files from instance ' + str(topology_instance.host))
            with ssh_client(topology_instance.host, topology_instance.private_key) as client:
                if client is not None:
                    sftp = client.open_sftp()

                    def copy_files(src_dir, dest_dir):
                        if not os.path.exists(dest_dir):
                            os.makedirs(dest_dir)

                        files = [f.filename for f in sftp.listdir_attr(src_dir) if stat.S_ISREG(f.st_mode)]
                        for file in files:
                            if not self._should_exclude_copying_file(file):
                                src_filename = posixpath.join(src_dir, file)
                                dest_filename = os.path.join(dest_dir, file)
                                sftp.get(src_filename, dest_filename)

                        dirs = [d.filename for d in sftp.listdir_attr(src_dir) if stat.S_ISDIR(d.st_mode)]
                        for d in dirs:
                            copy_files(posixpath.join(src_dir, d), os.path.join(dest_dir, d))

                    copy_files(src_project_path, project_files_dir)

                    sftp.close()
                else:
                    log.debug('could not connect to instance ' + str(topology_instance.host))

        # switch server on all nodes to local server
        server = Servers.instance().localServer()

        for node in topology.nodes():
            node._server = server
            if "image" in node.settings():
                node.settings()["image"] = os.path.basename(node.settings()["image"])

        # reload project
        self._project_settings["project_type"] = "local"
        self.saveProject(self._project_settings["project_path"])
        topology.reset()
        self.loadProject(self._project_settings["project_path"])

    @staticmethod
    def _should_exclude_copying_file(filename):
        """
        Returns whether or not a file should be excluded from copying when converting projects
        from cloud to local or vice versa
        :param filename:
        :return: True if file should be excluded, False otherwise
        """
        return filename.endswith('.ghost')

    def _cloud_instance_selected(self, instance_id):
        """
        Clear selection, then select all the nodes on the graphics view
        running on the instance_id instance
        """
        self.uiGraphicsView.scene().clearSelection()
        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem):
                if item.node()._server.instance_id == instance_id:
                    item.setSelected(True)

    def _setStyle(self, style):

        if style == "Charcoal (default)":
            self._setCharcoalStyle()
            return True
        elif style == "Classic":
            self._setClassicStyle()
            return True

        return False

    def _getStyleIcon(self, normal_file, active_file):

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(normal_file), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(active_file), QtGui.QIcon.Active, QtGui.QIcon.Off)
        return icon

    def _setLegacyStyle(self):
        """
        Sets the legacy GUI style.
        """

        self.setStyleSheet("")
        self.uiNewProjectAction.setIcon(QtGui.QIcon(":/icons/new-project.svg"))
        self.uiOpenProjectAction.setIcon(QtGui.QIcon(":/icons/open.svg"))
        self.uiSaveProjectAction.setIcon(QtGui.QIcon(":/icons/save.svg"))
        self.uiSaveProjectAsAction.setIcon(QtGui.QIcon(":/icons/save-as.svg"))
        self.uiImportExportConfigsAction.setIcon(QtGui.QIcon(":/icons/import_export_configs.svg"))
        self.uiScreenshotAction.setIcon(QtGui.QIcon(":/icons/camera-photo.svg"))
        self.uiSnapshotAction.setIcon(QtGui.QIcon(":/icons/snapshot.svg"))
        self.uiQuitAction.setIcon(QtGui.QIcon(":/icons/quit.svg"))
        self.uiPreferencesAction.setIcon(QtGui.QIcon(":/icons/applications.svg"))
        self.uiZoomInAction.setIcon(QtGui.QIcon(":/icons/zoom-in.png"))
        self.uiZoomOutAction.setIcon(QtGui.QIcon(":/icons/zoom-out.png"))
        self.uiShowPortNamesAction.setIcon(QtGui.QIcon(":/icons/show-interface-names.svg"))
        self.uiStartAllAction.setIcon(self._getStyleIcon(":/icons/start.svg", ":/icons/start-hover.svg"))
        self.uiSuspendAllAction.setIcon(self._getStyleIcon(":/icons/pause.svg", ":/icons/pause-hover.svg"))
        self.uiStopAllAction.setIcon(self._getStyleIcon(":/icons/stop.svg", ":/icons/stop-hover.svg"))
        self.uiReloadAllAction.setIcon(QtGui.QIcon(":/icons/reload.svg"))
        self.uiAuxConsoleAllAction.setIcon(QtGui.QIcon(":/icons/aux-console.svg"))
        self.uiConsoleAllAction.setIcon(QtGui.QIcon(":/icons/console.svg"))
        self.uiAddNoteAction.setIcon(QtGui.QIcon(":/icons/add-note.svg"))
        self.uiInsertImageAction.setIcon(QtGui.QIcon(":/icons/image.svg"))
        self.uiDrawRectangleAction.setIcon(self._getStyleIcon(":/icons/rectangle.svg", ":/icons/rectangle-hover.svg"))
        self.uiDrawEllipseAction.setIcon(self._getStyleIcon(":/icons/ellipse.svg", ":/icons/ellipse-hover.svg"))
        self.uiOnlineHelpAction.setIcon(QtGui.QIcon(":/icons/help.svg"))
        self.uiBrowseRoutersAction.setIcon(self._getStyleIcon(":/icons/router.png", ":/icons/router-hover.png"))
        self.uiBrowseSwitchesAction.setIcon(self._getStyleIcon(":/icons/switch.png", ":/icons/switch-hover.png"))
        self.uiBrowseEndDevicesAction.setIcon(self._getStyleIcon(":/icons/PC.png", ":/icons/PC-hover.png"))
        self.uiBrowseSecurityDevicesAction.setIcon(self._getStyleIcon(":/icons/firewall.png", ":/icons/firewall-hover.png"))
        self.uiBrowseAllDevicesAction.setIcon(self._getStyleIcon(":/icons/browse-all-icons.png", ":/icons/browse-all-icons-hover.png"))
        self.uiAddLinkAction.setIcon(self._getStyleIcon(":/icons/connection-new.svg", ":/charcoal_icons/connection-new-hover.svg"))

    def _setClassicStyle(self):
        """
        Sets the classic GUI style.
        """

        self.setStyleSheet("")
        self.uiNewProjectAction.setIcon(self._getStyleIcon(":/classic_icons/new-project.svg", ":/classic_icons/new-project-hover.svg"))
        self.uiOpenProjectAction.setIcon(self._getStyleIcon(":/classic_icons/open.svg", ":/classic_icons/open-hover.svg"))
        self.uiSaveProjectAction.setIcon(self._getStyleIcon(":/classic_icons/save-project.svg", ":/classic_icons/save-project-hover.svg"))
        self.uiSaveProjectAsAction.setIcon(self._getStyleIcon(":/classic_icons/save-as-project.svg", ":/classic_icons/save-as-project-hover.svg"))
        self.uiImportExportConfigsAction.setIcon(self._getStyleIcon(":/classic_icons/import_export_configs.svg", ":/classic_icons/import_export_configs-hover.svg"))
        self.uiScreenshotAction.setIcon(self._getStyleIcon(":/classic_icons/camera-photo.svg", ":/classic_icons/camera-photo-hover.svg"))
        self.uiSnapshotAction.setIcon(self._getStyleIcon(":/classic_icons/snapshot.svg", ":/classic_icons/snapshot-hover.svg"))
        self.uiQuitAction.setIcon(self._getStyleIcon(":/classic_icons/quit.svg", ":/classic_icons/quit-hover.svg"))
        self.uiPreferencesAction.setIcon(self._getStyleIcon(":/classic_icons/preferences.svg", ":/classic_icons/preferences-hover.svg"))
        self.uiZoomInAction.setIcon(self._getStyleIcon(":/classic_icons/zoom-in.svg", ":/classic_icons/zoom-in-hover.svg"))
        self.uiZoomOutAction.setIcon(self._getStyleIcon(":/classic_icons/zoom-out.svg", ":/classic_icons/zoom-out-hover.svg"))
        self.uiShowPortNamesAction.setIcon(self._getStyleIcon(":/classic_icons/show-interface-names.svg", ":/classic_icons/show-interface-names-hover.svg"))
        self.uiStartAllAction.setIcon(self._getStyleIcon(":/classic_icons/start.svg", ":/classic_icons/start-hover.svg"))
        self.uiSuspendAllAction.setIcon(self._getStyleIcon(":/classic_icons/pause.svg", ":/classic_icons/pause-hover.svg"))
        self.uiStopAllAction.setIcon(self._getStyleIcon(":/classic_icons/stop.svg", ":/classic_icons/stop-hover.svg"))
        self.uiReloadAllAction.setIcon(self._getStyleIcon(":/classic_icons/reload.svg", ":/classic_icons/reload-hover.svg"))
        self.uiAuxConsoleAllAction.setIcon(self._getStyleIcon(":/classic_icons/aux-console.svg", ":/classic_icons/aux-console-hover.svg"))
        self.uiConsoleAllAction.setIcon(self._getStyleIcon(":/classic_icons/console.svg", ":/classic_icons/console-hover.svg"))
        self.uiAddNoteAction.setIcon(self._getStyleIcon(":/classic_icons/add-note.svg", ":/classic_icons/add-note-hover.svg"))
        self.uiInsertImageAction.setIcon(self._getStyleIcon(":/classic_icons/image.svg", ":/classic_icons/image-hover.svg"))
        self.uiDrawRectangleAction.setIcon(self._getStyleIcon(":/classic_icons/rectangle.svg", ":/classic_icons/rectangle-hover.svg"))
        self.uiDrawEllipseAction.setIcon(self._getStyleIcon(":/classic_icons/ellipse.svg", ":/classic_icons/ellipse-hover.svg"))
        self.uiOnlineHelpAction.setIcon(self._getStyleIcon(":/classic_icons/help.svg", ":/classic_icons/help-hover.svg"))
        self.uiBrowseRoutersAction.setIcon(self._getStyleIcon(":/classic_icons/router.svg", ":/classic_icons/router-hover.svg"))
        self.uiBrowseSwitchesAction.setIcon(self._getStyleIcon(":/classic_icons/switch.svg", ":/classic_icons/switch-hover.svg"))
        self.uiBrowseEndDevicesAction.setIcon(self._getStyleIcon(":/classic_icons/pc.svg", ":/classic_icons/pc-hover.svg"))
        self.uiBrowseSecurityDevicesAction.setIcon(self._getStyleIcon(":/classic_icons/firewall.svg", ":/classic_icons/firewall-hover.svg"))
        self.uiBrowseAllDevicesAction.setIcon(self._getStyleIcon(":/classic_icons/browse-all-icons.svg", ":/classic_icons/browse-all-icons-hover.svg"))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/classic_icons/add-link.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/classic_icons/add-link-hover.svg"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/classic_icons/add-link-cancel.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.uiAddLinkAction.setIcon(icon)

    def _setCharcoalStyle(self):
        """
        Sets the charcoal GUI style.
        """

        style = """QWidget {background-color: #535353}
QToolBar {border:0px}
QGraphicsView, QTextEdit, QPlainTextEdit, QTreeWidget, QLineEdit, QSpinBox, QComboBox {background-color: #dedede}
QDockWidget, QMenuBar, QPushButton, QToolButton, QTabWidget {color: #dedede; font: bold 11px}
QLabel, QMenu, QStatusBar, QRadioButton, QCheckBox {color: #dedede}
QMenuBar::item {background-color: #535353}
QMenu::item:selected {color: white; background-color: #5f5f5f}
QToolButton:hover {background-color: #5f5f5f}
QGroupBox {color: #dedede; font: bold 12px; padding: 15px; border-style: none}
QAbstractScrollArea::corner { background: #535353}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {background: none}
QComboBox {selection-color: black; selection-background-color: #dedede}
"""

        if sys.platform.startswith("darwin"):
            style += "QDockWidget::title {text-align: center; background-color: #535353}"

        self.setStyleSheet(style)
        self.uiNewProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/new-project.svg", ":/charcoal_icons/new-project-hover.svg"))
        self.uiOpenProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/open.svg", ":/charcoal_icons/open-hover.svg"))
        self.uiSaveProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/save-project.svg", ":/charcoal_icons/save-project-hover.svg"))
        self.uiSaveProjectAsAction.setIcon(self._getStyleIcon(":/charcoal_icons/save-as-project.svg", ":/charcoal_icons/save-as-project-hover.svg"))
        self.uiImportExportConfigsAction.setIcon(self._getStyleIcon(":/charcoal_icons/import_export_configs.svg", ":/charcoal_icons/import_export_configs-hover.svg"))
        self.uiScreenshotAction.setIcon(self._getStyleIcon(":/charcoal_icons/camera-photo.svg", ":/charcoal_icons/camera-photo-hover.svg"))
        self.uiSnapshotAction.setIcon(self._getStyleIcon(":/charcoal_icons/snapshot.svg", ":/charcoal_icons/snapshot-hover.svg"))
        self.uiQuitAction.setIcon(self._getStyleIcon(":/charcoal_icons/quit.svg", ":/charcoal_icons/quit-hover.svg"))
        self.uiPreferencesAction.setIcon(self._getStyleIcon(":/charcoal_icons/preferences.svg", ":/charcoal_icons/preferences-hover.svg"))
        self.uiZoomInAction.setIcon(self._getStyleIcon(":/charcoal_icons/zoom-in.svg", ":/charcoal_icons/zoom-in-hover.svg"))
        self.uiZoomOutAction.setIcon(self._getStyleIcon(":/charcoal_icons/zoom-out.svg", ":/charcoal_icons/zoom-out-hover.svg"))
        self.uiShowPortNamesAction.setIcon(self._getStyleIcon(":/charcoal_icons/show-interface-names.svg", ":/charcoal_icons/show-interface-names-hover.svg"))
        self.uiStartAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/start.svg", ":/charcoal_icons/start-hover.svg"))
        self.uiSuspendAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/pause.svg", ":/charcoal_icons/pause-hover.svg"))
        self.uiStopAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/stop.svg", ":/charcoal_icons/stop-hover.svg"))
        self.uiReloadAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/reload.svg", ":/charcoal_icons/reload-hover.svg"))
        self.uiAuxConsoleAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/aux-console.svg", ":/charcoal_icons/aux-console-hover.svg"))
        self.uiConsoleAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/console.svg", ":/charcoal_icons/console-hover.svg"))
        self.uiAddNoteAction.setIcon(self._getStyleIcon(":/charcoal_icons/add-note.svg", ":/charcoal_icons/add-note-hover.svg"))
        self.uiInsertImageAction.setIcon(self._getStyleIcon(":/charcoal_icons/image.svg", ":/charcoal_icons/image-hover.svg"))
        self.uiDrawRectangleAction.setIcon(self._getStyleIcon(":/charcoal_icons/rectangle.svg", ":/charcoal_icons/rectangle-hover.svg"))
        self.uiDrawEllipseAction.setIcon(self._getStyleIcon(":/charcoal_icons/ellipse.svg", ":/charcoal_icons/ellipse-hover.svg"))
        self.uiOnlineHelpAction.setIcon(self._getStyleIcon(":/charcoal_icons/help.svg", ":/charcoal_icons/help-hover.svg"))
        self.uiBrowseRoutersAction.setIcon(self._getStyleIcon(":/charcoal_icons/router.svg", ":/charcoal_icons/router-hover.svg"))
        self.uiBrowseSwitchesAction.setIcon(self._getStyleIcon(":/charcoal_icons/switch.svg", ":/charcoal_icons/switch-hover.svg"))
        self.uiBrowseEndDevicesAction.setIcon(self._getStyleIcon(":/charcoal_icons/pc.svg", ":/charcoal_icons/pc-hover.svg"))
        self.uiBrowseSecurityDevicesAction.setIcon(self._getStyleIcon(":/charcoal_icons/firewall.svg", ":/charcoal_icons/firewall-hover.svg"))
        self.uiBrowseAllDevicesAction.setIcon(self._getStyleIcon(":/charcoal_icons/browse-all-icons.svg", ":/charcoal_icons/browse-all-icons-hover.svg"))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/charcoal_icons/add-link-1.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/charcoal_icons/add-link-1-hover.svg"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/charcoal_icons/add-link-1-cancel.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.uiAddLinkAction.setIcon(icon)
