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
import time
import shutil
import json
import glob
import logging
import subprocess

from .local_config import LocalConfig
from .modules import MODULES
from .modules.module_error import ModuleError
from .modules.vpcs import VPCS
from .qt import QtGui, QtCore, QtWidgets, QtSvg
from .servers import Servers
from .gns3_vm import GNS3VM
from .node import Node
from .ui.main_window_ui import Ui_MainWindow
from .dialogs.about_dialog import AboutDialog
from .dialogs.new_project_dialog import NewProjectDialog
from .dialogs.preferences_dialog import PreferencesDialog
from .dialogs.snapshots_dialog import SnapshotsDialog
from .dialogs.export_debug_dialog import ExportDebugDialog
from .dialogs.doctor_dialog import DoctorDialog
from .dialogs.setup_wizard import SetupWizard
from .settings import GENERAL_SETTINGS
from .utils.progress_dialog import ProgressDialog
from .utils.process_files_worker import ProcessFilesWorker
from .utils.wait_for_connection_worker import WaitForConnectionWorker
from .utils.wait_for_vm_worker import WaitForVMWorker
from .utils.export_project_worker import ExportProjectWorker
from .utils.import_project_worker import ImportProjectWorker
from .utils.message_box import MessageBox
from .ports.port import Port
from .items.node_item import NodeItem
from .items.link_item import LinkItem
from .items.shape_item import ShapeItem
from .items.image_item import ImageItem
from .items.note_item import NoteItem
from .topology import Topology
from .project import Project
from .http_client import HTTPClient
from .progress import Progress
from .update_manager import UpdateManager
from .utils.analytics import AnalyticsClient
from .dialogs.appliance_wizard import ApplianceWizard
from .dialogs.new_appliance_dialog import NewApplianceDialog
from .registry.appliance import ApplianceError

log = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    """
    Main window implementation.

    :param parent: parent widget
    """

    # signal to tell the view if the user is adding a link or not
    adding_link_signal = QtCore.pyqtSignal(bool)

    # signal to tell a new project was created
    project_new_signal = QtCore.pyqtSignal(str)

    # signal to tell the windows is ready to load his first project
    ready_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setupUi(self)

        MainWindow._instance = self
        self._settings = {}
        HTTPClient.setProgressCallback(Progress.instance(self))

        self._project = None
        self._createTemporaryProject()
        self._first_file_load = True
        self._loadSettings()
        self._connections()
        self._ignore_unsaved_state = False
        self._max_recent_files = 5
        self._soft_exit = True
        self._project_dialog = None
        self._recent_file_actions = []
        self._start_time = time.time()
        local_config = LocalConfig.instance()
        local_config.config_changed_signal.connect(self._localConfigChangedSlot)
        self._local_config_timer = QtCore.QTimer(self)
        self._local_config_timer.timeout.connect(local_config.checkConfigChanged)
        self._local_config_timer.start(1000)  # milliseconds
        self._analytics_client = AnalyticsClient()

        # restore the geometry and state of the main window.
        self.restoreGeometry(QtCore.QByteArray().fromBase64(self._settings["geometry"].encode()))
        self.restoreState(QtCore.QByteArray().fromBase64(self._settings["state"].encode()))

        # populate the view -> docks menu
        self.uiDocksMenu.addAction(self.uiTopologySummaryDockWidget.toggleViewAction())
        self.uiDocksMenu.addAction(self.uiServerSummaryDockWidget.toggleViewAction())
        self.uiDocksMenu.addAction(self.uiConsoleDockWidget.toggleViewAction())
        self.uiDocksMenu.addAction(self.uiNodesDockWidget.toggleViewAction())
        # Make sure the dock widget is not open
        self.uiNodesDockWidget.setVisible(False)

        # default directories for QFileDialog
        self._import_configs_from_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        self._export_configs_to_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        self._screenshots_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.PicturesLocation)
        self._pictures_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.PicturesLocation)

        # add recent file actions to the File menu
        for i in range(0, self._max_recent_files):
            action = QtWidgets.QAction(self.uiFileMenu)
            action.setVisible(False)
            action.triggered.connect(self.openRecentFileSlot)
            self._recent_file_actions.append(action)
        self.uiFileMenu.insertActions(self.uiQuitAction, self._recent_file_actions)
        self._recent_file_actions_separator = self.uiFileMenu.insertSeparator(self.uiQuitAction)
        self._recent_file_actions_separator.setVisible(False)
        self._updateRecentFileActions()

        # set the window icon
        self.setWindowIcon(QtGui.QIcon(":/images/gns3.ico"))

        # restore the style
        self._setStyle(self._settings.get("style"))


        self.setWindowTitle("[*] GNS3")

        # load initial stuff once the event loop isn't busy
        self.run_later(0, self.startupLoading)

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, GENERAL_SETTINGS)

        # restore packet capture settings
        Port.loadPacketCaptureSettings()

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

        # change the GUI style
        style = new_settings.get("style")
        if style and new_settings["style"] != self._settings["style"]:
            if not self._setStyle(style):
                self._setLegacyStyle()

        self._settings.update(new_settings)
        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

    def setSoftExit(self, softExit):
        """If True warn user before exiting app if unsaved data"""
        self._soft_exit = softExit

    def _connections(self):
        """
        Connect widgets to slots
        """

        # file menu connections
        self.uiNewProjectAction.triggered.connect(self._newProjectActionSlot)
        self.uiOpenProjectAction.triggered.connect(self.openProjectActionSlot)
        self.uiOpenApplianceAction.triggered.connect(self.openApplianceActionSlot)
        self.uiSaveProjectAction.triggered.connect(self._saveProjectActionSlot)
        self.uiSaveProjectAsAction.triggered.connect(self._saveProjectAsActionSlot)
        self.uiExportProjectAction.triggered.connect(self._exportProjectActionSlot)
        self.uiImportProjectAction.triggered.connect(self._importProjectActionSlot)
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

        # tools menu connections
        self.uiVPCSAction.triggered.connect(self._vpcsActionSlot)

        # annotate menu connections
        self.uiAddNoteAction.triggered.connect(self._addNoteActionSlot)
        self.uiInsertImageAction.triggered.connect(self._insertImageActionSlot)
        self.uiDrawRectangleAction.triggered.connect(self._drawRectangleActionSlot)
        self.uiDrawEllipseAction.triggered.connect(self._drawEllipseActionSlot)
        self.uiEditReadmeAction.triggered.connect(self._editReadmeActionSlot)

        # help menu connections
        self.uiOnlineHelpAction.triggered.connect(self._onlineHelpActionSlot)
        self.uiCheckForUpdateAction.triggered.connect(self._checkForUpdateActionSlot)
        self.uiSetupWizard.triggered.connect(self._setupWizardActionSlot)
        self.uiLabInstructionsAction.triggered.connect(self._labInstructionsActionSlot)
        self.uiAboutQtAction.triggered.connect(self._aboutQtActionSlot)
        self.uiAboutAction.triggered.connect(self._aboutActionSlot)
        self.uiExportDebugInformationAction.triggered.connect(self._exportDebugInformationSlot)
        self.uiDoctorAction.triggered.connect(self._doctorSlot)
        self.uiAcademyAction.triggered.connect(self._academyActionSlot)
        self.uiIOUVMConverterAction.triggered.connect(self._IOUVMConverterActionSlot)
        # New appliance button
        self.uiNewAppliancePushButton.clicked.connect(self._newApplianceActionSlot)

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
        self.project_new_signal.connect(self.project_created)

        self.ready_signal.connect(self._readySlot)


    def project(self):
        """
        Return current project
        """

        return self._project

    def setProject(self, project):
        """
        Set current project

        :param project: Project instance
        """

        self._project = project
        self._setCurrentFile(project.topologyFile())

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

        self._project.close()
        self._project = Project()
        self.uiGraphicsView.reset()
        # create the destination directory for project files
        try:
            os.makedirs(new_project_settings["project_files_dir"], exist_ok=True)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "New project", "Could not create project files directory {}: {}".format(new_project_settings["project_files_dir"], e))
            self._createTemporaryProject()

        # let all modules know about the new project files directory
        # self.uiGraphicsView.updateProjectFilesDir(new_project_settings["project_files_dir"])

        topology = Topology.instance()
        topology.project = self._project

        self._project.setName(new_project_settings["project_name"])
        self._project.setTopologyFile(new_project_settings["project_path"])
        self.saveProject(new_project_settings["project_path"])
        self.project_new_signal.emit(self._project.topologyFile())

    def _newProjectActionSlot(self):
        """
        Slot called to create a new project.
        """

        if self.checkForUnsavedChanges():
            self._project_dialog = NewProjectDialog(self)
            self._project_dialog.show()
            create_new_project = self._project_dialog.exec_()
            # Close the device dock so it repopulates.  Done in case switching
            # between cloud and local.
            self.uiNodesDockWidget.setVisible(False)
            self.uiNodesDockWidget.setWindowTitle("")

            if create_new_project:
                new_project_settings = self._project_dialog.getNewProjectSettings()
                self._createNewProject(new_project_settings)
            else:
                self._createTemporaryProject()
            self._project_dialog = None

    def _newApplianceActionSlot(self):
        """
        Called when user want to create a new appliance
        """
        dialog = NewApplianceDialog(self)
        dialog.show()

    def _IOUVMConverterActionSlot(self):
        command = shutil.which("gns3-iouvm-converter")
        if command is None:
            QtWidgets.QMessageBox.critical(self, "GNS3 IOU VM Converter", "gns3-iouvm-converter not found")
            return
        try:
            subprocess.Popen([command])
        except (OSError, subprocess.SubprocessError) as e:
            QtWidgets.QMessageBox.critical(self, "GNS3 IOU VM Converter", "Error when running gns3-iouvm-converter {}".format(e))

    def openApplianceActionSlot(self):
        """
        Slot called to open an appliance.
        """

        directory = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)
        if len(directory) == 0:
            directory = self.projectsDirPath()
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        "Open appliance",
                                                        directory,
                                                        "All files (*.*);;GNS3 Appliance (*.gns3appliance *.gns3a)",
                                                        "GNS3 Appliance (*.gns3appliance *.gns3a)")
        if path:
            self.loadPath(path)

    def openProjectActionSlot(self):
        """
        Slot called to open a project.
        """

        path, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        "Open project",
                                                        self.projectsDirPath(),
                                                        "All files (*.*);;GNS3 Project (*.gns3);;GNS3 Portable Project (*.gns3project *.gns3p);;NET files (*.net)",
                                                        "GNS3 Project (*.gns3)")
        if path:
            self.loadPath(path)

    def openRecentFileSlot(self):
        """
        Slot called to open recent file from the File menu.
        """

        action = self.sender()
        if action:
            path = action.data()
            if not os.path.isfile(path):
                QtWidgets.QMessageBox.critical(self, "Recent file", "{}: no such file".format(path))
                return
            self.loadPath(path)

    def loadSnapshot(self, path):
        """Loads a snapshot"""

        self._open_project_path = path
        self._project.project_closed_signal.connect(self._projectClosedContinueLoadPath)
        self._project.close()

    def loadPath(self, path):
        """Open a file and close the previous project"""

        if path:
            if self._first_file_load is True:
                self._first_file_load = False
                time.sleep(0.5)  # give some time to the server to initialize

            if self._project_dialog:
                self._project_dialog.reject()
                self._project_dialog = None

            if path.endswith(".gns3project") or path.endswith(".gns3p"):
                project_name = os.path.basename(path).split('.')[0]
                self._project_dialog = NewProjectDialog(self, default_project_name=project_name)
                self._project_dialog.show()
                if self._project_dialog.exec_():
                    new_project_settings = self._project_dialog.getNewProjectSettings()
                    import_worker = ImportProjectWorker(path, new_project_settings)
                    import_worker.imported.connect(self.loadPath)
                    progress_dialog = ProgressDialog(import_worker, "Importing project", "Importing portable project files...", "Cancel", parent=self)
                    progress_dialog.show()
                    progress_dialog.exec_()

                self._project_dialog = None

            elif path.endswith(".gns3appliance") or path.endswith(".gns3a"):
                try:
                    self._appliance_wizard = ApplianceWizard(self, path)
                except ApplianceError as e:
                    QtWidgets.QMessageBox.critical(self, "Appliance", "Error while importing appliance {}: {}".format(path, str(e)))
                    return
                self._appliance_wizard.show()
                self._appliance_wizard.exec_()
            elif self.checkForUnsavedChanges():
                self._open_project_path = path
                if self._project.closed():
                    self._projectClosedContinueLoadPath()
                else:
                    self._project.project_closed_signal.connect(self._projectClosedContinueLoadPath)
                    self._project.close()

    def _projectClosedContinueLoadPath(self):

        path = self._open_project_path
        if self._loadProject(path):
            self.project_new_signal.emit(path)

    def _saveProjectActionSlot(self):
        """
        Slot called to save a project.
        """

        if self._project.temporary():
            return self.saveProjectAs()
        else:
            if not self._project.filesDir():
                QtWidgets.QMessageBox.critical(self, "Project", "Sorry, no project has been created or initialized")
                return
            return self.saveProject(self._project.topologyFile())

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
        selection, ok = QtWidgets.QInputDialog.getItem(self, "Import/Export configs", "Please choose an option:", options, 0, False)
        if ok:
            if selection == options[0]:
                self._exportConfigs()
            else:
                self._importConfigs()

    def _exportConfigs(self):
        """
        Exports all configs to a directory.
        """

        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Export directory", self._export_configs_to_dir, QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            self._export_configs_to_dir = os.path.dirname(path)
            for module in MODULES:
                instance = module.instance()
                if hasattr(instance, "exportConfigs"):
                    instance.exportConfigs(path)

    def _importConfigs(self):
        """
        Imports all configs from a directory.
        """

        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Import directory", self._import_configs_from_dir, QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            self._import_configs_from_dir = os.path.dirname(path)
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
        source = scene.itemsBoundingRect().adjusted(-20.0, -20.0, 20.0, 20.0)
        image = QtGui.QImage(source.size().toSize(), QtGui.QImage.Format_RGB32)
        image.fill(QtCore.Qt.white)
        painter = QtGui.QPainter(image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        scene.render(painter, source=source)
        painter.end()
        # TODO: quality option
        return image.save(path)

    def _screenshotActionSlot(self):
        """
        Slot called to take a screenshot of the scene.
        """

        # supported image file formats
        file_formats = "PNG File (*.png);;JPG File (*.jpeg *.jpg);;BMP File (*.bmp);;XPM File (*.xpm *.xbm);;PPM File (*.ppm);;TIFF File (*.tiff)"
        path, selected_filter = QtWidgets.QFileDialog.getSaveFileName(self, "Screenshot", self._screenshots_dir, file_formats)
        if not path:
            return
        self._screenshots_dir = os.path.dirname(path)

        # add the extension if missing
        file_format = "." + selected_filter[:4].lower().strip()
        if not path.endswith(file_format):
            path += file_format

        if not self._createScreenshot(path):
            QtWidgets.QMessageBox.critical(self, "Screenshot", "Could not create screenshot file {}".format(path))

    def _snapshotActionSlot(self):
        """
        Slot called to open the snapshot dialog.
        """

        if self._project.temporary():
            QtWidgets.QMessageBox.critical(self, "Snapshots", "Sorry, snapshots are not supported with temporary projects")
            return

        # first check if any node doesn't run locally
        topology = Topology.instance()
        for node in topology.nodes():
            if node.server() != Servers.instance().localServer():
                QtWidgets.QMessageBox.critical(self, "Snapshots", "Sorry, snapshots can only be created if all the nodes run locally")
                return

        if self._nodeRunning():
            QtWidgets.QMessageBox.warning(self, "Snapshots", "Sorry, snapshots can only be created when all nodes are stopped")
            return

        dialog = SnapshotsDialog(self,
                                 self._project.topologyFile(),
                                 self._project.filesDir())
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

        self.uiGraphicsView.resetTransform()

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

        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, LinkItem):
                item.resetPortLabels()
                item.adjust()

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

        self.uiGraphicsView.auxConsoleFromItems(self.uiGraphicsView.scene().items())

    def _consoleAllActionSlot(self):
        """
        Slot called when connecting to all the nodes using the console.
        """

        self.uiGraphicsView.consoleFromItems(self.uiGraphicsView.scene().items())

    def _vpcsActionSlot(self):
        """
        Slot called when VPCS multi-host is clicked in the Tools menu.
        """

        vpcs_module = VPCS.instance()

        if self._project.filesDir() is None:
            QtWidgets.QMessageBox.critical(self, "VPCS", "Sorry, the project hasn't been initialized yet")
            return

        try:
            working_dir = os.path.join(self._project.filesDir(), "project-files", "vpcs", "multi-host")
            os.makedirs(working_dir, exist_ok=True)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "VPCS", "Could not create the VPCS working directory: {}".format(e))
            return

        try:
            vpcs_port = vpcs_module.startMultiHostVPCS(working_dir)
        except ModuleError as e:
            QtWidgets.QMessageBox.critical(self, "VPCS", "{}".format(e))
            return

        try:
            from .telnet_console import telnetConsole
            telnetConsole("VPCS multi-host", "127.0.0.1", vpcs_port)
        except (OSError, ValueError) as e:
            QtWidgets.QMessageBox.critical(self, "Console", "Cannot start console application: {}".format(e))

    def _addNoteActionSlot(self):
        """
        Slot called when adding a new note on the scene.
        """

        self.uiGraphicsView.addNote(self.uiAddNoteAction.isChecked())

    def _insertImageActionSlot(self):
        """
        Slot called when inserting an image on the scene.
        """

        files_dir = self._project.filesDir()
        if files_dir is None:
            QtWidgets.QMessageBox.critical(self, "Image", "Please create a node first")
            return

        # supported image file formats
        file_formats = "Image files (*.svg *.bmp *.jpeg *.jpg *.gif *.pbm *.pgm *.png *.ppm *.xbm *.xpm);;All files (*.*)"

        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Image", self._pictures_dir, file_formats)
        if not path:
            return
        self._pictures_dir = os.path.dirname(path)

        image = QtGui.QPixmap(path)
        if image.isNull():
            QtWidgets.QMessageBox.critical(self, "Image", "Image file format not supported")
            return

        destination_dir = os.path.join(files_dir, "project-files", "images")
        try:
            os.makedirs(destination_dir, exist_ok=True)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Image", "Could not create the image directory: {}".format(e))
            return

        image_filename = os.path.basename(path)
        destination_image_path = os.path.join(destination_dir, image_filename)
        if not os.path.isfile(destination_image_path):
            # copy the image to the project files directory
            try:
                shutil.copyfile(path, destination_image_path)
            except OSError as e:
                QtWidgets.QMessageBox.critical(self, "Image", "Could not copy the image to the project image directory: {}".format(e))
                return

        renderer = QtSvg.QSvgRenderer(path)
        if renderer.isValid():
            # use a SVG image item if this is a valid SVG file
            image = renderer

        # path to the image is relative to the project-files dir
        self.uiGraphicsView.addImage(image, os.path.join("images", image_filename))

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

        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://gns3.com/support/docs"))

    def _checkForUpdateActionSlot(self, silent=False):
        """
        Slot to check if a newer version is available.

        :param silent: do not display any message
        """

        self._update_manager = UpdateManager()
        self._update_manager.checkForUpdate(self, silent)

    def _setupWizardActionSlot(self):
        """
        Slot to open the setup wizard.
        """

        with Progress.instance().context(min_duration=0):
            setup_wizard = SetupWizard(self)
            setup_wizard.show()
            setup_wizard.exec_()

    def _labInstructionsActionSlot(self, silent=False):
        """
        Slot to open lab instructions.
        """

        if self._project.temporary():
            QtWidgets.QMessageBox.critical(self, "Lab instructions", "Sorry, lab instructions are not supported with temporary projects")
            return

        project_dir = glob.escape(os.path.dirname(self._project.topologyFile()))
        instructions_files = glob.glob(project_dir + os.sep + "instructions.*")
        instructions_files += glob.glob(os.path.join(project_dir, "instructions") + os.sep + "instructions*")
        if len(instructions_files):
            path = instructions_files[0]
            if QtGui.QDesktopServices.openUrl(QtCore.QUrl('file:///' + path, QtCore.QUrl.TolerantMode)) is False and silent is False:
                QtWidgets.QMessageBox.critical(self, "Lab instructions", "Could not open {}".format(path))
        elif silent is False:
            QtWidgets.QMessageBox.critical(self, "Lab instructions", "No instructions found")

    def _aboutQtActionSlot(self):
        """
        Slot to display the Qt About dialog.
        """

        QtWidgets.QMessageBox.aboutQt(self)

    def _aboutActionSlot(self):
        """
        Slot to display the GNS3 About dialog.
        """

        dialog = AboutDialog(self)
        dialog.show()
        dialog.exec_()

    def _exportDebugInformationSlot(self):
        """
        Slot to display a window for exporting debug information
        """

        dialog = ExportDebugDialog(self, self._project)
        dialog.show()
        dialog.exec_()

    def _doctorSlot(self):
        """
        Slot to display a window for exporting debug information
        """

        dialog = DoctorDialog(self)
        dialog.show()
        dialog.exec_()

    def _academyActionSlot(self):
        """
        Slot to launch a browser pointing to the courses page.
        """

        QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://academy.gns3.com/"))

    def _showNodesDockWidget(self, title, category):
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
            self.uiNodesView.populateNodesView(category)

    def _localConfigChangedSlot(self):
        """
        Called when the local config change
        """

        self.uiNodesView.refresh()

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

        self._showNodesDockWidget("All devices", None)

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

        with Progress.instance().context(min_duration=0):
            dialog = PreferencesDialog(self)
            dialog.restoreGeometry(QtCore.QByteArray().fromBase64(self._settings["preferences_dialog_geometry"].encode()))
            dialog.show()
            dialog.exec_()
            self._settings["preferences_dialog_geometry"] = bytes(dialog.saveGeometry().toBase64()).decode()
            self.setSettings(self._settings)

    def _editReadmeActionSlot(self):
        """
        Slot to edit the README file
        """

        if self._project.temporary():
            QtWidgets.QMessageBox.critical(self, "README", "Sorry, README file is not supported with temporary projects")
            return

        log.debug("Opened %s", self._project.readmePathFile())
        if not os.path.exists(self._project.readmePathFile()):
            try:
                with open(self._project.readmePathFile(), "w+") as f:
                    f.write("Title: My lab\nAuthor: Grass Hopper <grass@hopper.com>\n\nThis lab is about...")
            except OSError as e:
                QtWidgets.QMessageBox.critical(self, "README", "Could not create {}".format(self._project.readmePathFile()))
                return
        if QtGui.QDesktopServices.openUrl(QtCore.QUrl('file:///' + self._project.readmePathFile(), QtCore.QUrl.TolerantMode)) is False:
            QtWidgets.QMessageBox.critical(self, "README", "Could not open {}".format(self._project.readmePathFile()))

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
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """
        Handles the event when the main window is closed.

        :param event: QCloseEvent
        """

        progress = Progress.instance()
        progress.setAllowCancelQuery(True)
        progress.setCancelButtonText("Force quit")

        log.debug("Close the main Windows")

        self._analytics_client.sendScreenView("Main Window", session_start=False)

        servers = Servers.instance()
        if self._project.closed():
            log.debug("Project is closed killing server and closing main windows")
            self._finish_application_closing(close_windows=False)
            event.accept()
            self.uiConsoleTextEdit.closeIO()
        elif not self._soft_exit or self.checkForUnsavedChanges():
            log.debug("Project is not closed asking for project closing")
            self._project.project_closed_signal.connect(self._finish_application_closing)
            self._project.close(local_server_shutdown=True)
            event.ignore()
        else:
            event.ignore()

    def _finish_application_closing(self, close_windows=True):
        """
        Handles the event when the main window is closed.
        And project closed.

        :params closing: True the windows is currently closing do not try to reclose it
        """

        log.debug("_finish_application_closing")
        VPCS.instance().stopMultiHostVPCS()

        GNS3VM.instance().shutdown()
        self._settings["geometry"] = bytes(self.saveGeometry().toBase64()).decode()
        self._settings["state"] = bytes(self.saveState().toBase64()).decode()
        self.setSettings(self._settings)

        servers = Servers.instance()
        servers.stopLocalServer(wait=True)

        time_spent = "{:.0f}".format(time.time() - self._start_time)
        log.debug("Time spend in the software is {}".format(time_spent))

        if close_windows:
            self.close()

    def _nodeRunning(self):
        """
        Display a warning to user

        :returns: False is a device is still running
        """
        # check if any node is running
        topology = Topology.instance()
        topology.project = self._project
        running_node = False
        for node in topology.nodes():
            if hasattr(node, "start") and node.status() == Node.started:
                return True
        return False

    def checkForUnsavedChanges(self):
        """
        Checks if there are any unsaved changes.

        :returns: boolean
        """

        if self._nodeRunning():
            QtWidgets.QMessageBox.warning(self, "Closing project", "A device is still running, please stop it before closing your project")
            return False

        if self.testAttribute(QtCore.Qt.WA_WindowModified):
            if self._project.temporary():
                destination_file = "untitled.gns3"
            else:
                destination_file = os.path.basename(self._project.topologyFile())
            reply = QtWidgets.QMessageBox.warning(self, "Unsaved changes", 'Save changes to project "{}" before closing?'.format(destination_file),
                                                  QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Save:
                if self._project.temporary():
                    return self.saveProjectAs()
                return self.saveProject(self._project.topologyFile())
            elif reply == QtWidgets.QMessageBox.Cancel:
                return False
        return True

    def startupLoading(self):
        """
        Called by QTimer.singleShot to load everything needed at startup.
        """

        if not LocalConfig.instance().isMainGui():
            reply = QtWidgets.QMessageBox.warning(self, "GNS3", "Another GNS3 GUI is already running. Continue?",
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                self.close()
                return

        if not sys.platform.startswith("win") and os.geteuid() == 0:
            QtWidgets.QMessageBox.warning(self, "Root", "Running GNS3 as root is not recommended and could be dangerous")

        # restore debug level
        if self._settings["debug_level"]:
            root = logging.getLogger()
            root.addHandler(logging.StreamHandler(sys.stdout))

        # restore the style
        self._setStyle(self._settings.get("style"))

        servers = Servers.instance()
        # start the GNS3 VM
        gns3_vm = GNS3VM.instance()
        if not gns3_vm.isRunning():
            servers.initVMServer()
            if gns3_vm.isRemote():
                gns3_vm.setRunning(True)
            elif gns3_vm.autoStart():
                worker = WaitForVMWorker()
                progress_dialog = ProgressDialog(worker, "GNS3 VM", "Starting the GNS3 VM...", "Cancel", busy=True, parent=self, delay=5)
                progress_dialog.show()
                if progress_dialog.exec_():
                    gns3_vm.adjustLocalServerIP()

        # start and connect to the local server
        server = servers.localServer()
        if servers.shouldLocalServerAutoStart():
                if not servers.localServerAutoStart():
                    QtWidgets.QMessageBox.critical(self, "Local server", "Could not start the local server process: {}".format(servers.localServerPath()))
                    return

                worker = WaitForConnectionWorker(server.host(), server.port())
                progress_dialog = ProgressDialog(worker,
                                                 "Local server",
                                                 "Connecting to server {} on port {}...".format(server.host(), server.port()),
                                                 "Cancel", busy=True, parent=self)
                progress_dialog.show()
                if not progress_dialog.exec_():
                    return

        # show the setup wizard
        if not self._settings["hide_setup_wizard"] and not gns3_vm.isRunning():
            with Progress.instance().context(min_duration=0):
                setup_wizard = SetupWizard(self)
                setup_wizard.show()
                setup_wizard.exec_()

        self._analytics_client.sendScreenView("Main Window")
        self._createTemporaryProject()
        self.ready_signal.emit()

        if self._settings["check_for_update"]:
            # automatic check for update every week (604800 seconds)
            current_epoch = int(time.mktime(time.localtime()))
            if current_epoch - self._settings["last_check_for_update"] >= 604800:
                # let's check for an update
                self._checkForUpdateActionSlot(silent=True)
                self._settings["last_check_for_update"] = current_epoch
                self.setSettings(self._settings)

    def _readySlot(self):
        """
        Called when the application is ready to load a project
        """
        if self._settings["auto_launch_project_dialog"] and self._first_file_load:
            self._project_dialog = NewProjectDialog(self, showed_from_startup=True)
            self._project_dialog.accepted.connect(self._newProjectDialodAcceptedSlot)
            self._project_dialog.show()

    def _newProjectDialodAcceptedSlot(self):
        """
        Called when user accept the new project dialog
        """
        if self._project_dialog:
            new_project_settings = self._project_dialog.getNewProjectSettings()
            self._createNewProject(new_project_settings)
            self._project_dialog = None

    def _running_nodes(self):
        """
        :returns: Return the list of running nodes
        """
        topology = Topology.instance()
        running_nodes = []
        for node in topology.nodes():
            if hasattr(node, "start") and node.status() == Node.started:
                running_nodes.append(node.name())
        return running_nodes

    def _isTopologyOnRemoteServer(self):
        """
        :returns: Boolean True if topology run on a remote server
        """
        topology = Topology.instance()
        running_nodes = []
        for node in topology.nodes():
            if not node.server().isLocal():
                return True
        return False

    def saveProjectAs(self):
        """
        Saves a project to another location/name.

        :returns: GNS3 project file (.gns3)
        """

        if self._nodeRunning():
            QtWidgets.QMessageBox.warning(self, "Save As", "All devices must be stopped before saving to another location")
            return False

        if self._isTopologyOnRemoteServer() and not self._project.temporary():
            MessageBox(self, "Save project", "You can not use the save as function on a remote project for the moment.")
            return

        if self._project.temporary():
            default_project_name = "untitled"
        else:
            default_project_name = self._project.name()

        projects_dir_path = os.path.normpath(os.path.expanduser(self.projectsDirPath()))
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setWindowTitle("Save project")
        file_dialog.setNameFilters(["Directories"])
        file_dialog.setDirectory(projects_dir_path)
        file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        file_dialog.setLabelText(QtWidgets.QFileDialog.FileName, "Project name:")
        file_dialog.selectFile(default_project_name)
        file_dialog.setOptions(QtWidgets.QFileDialog.ShowDirsOnly)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        if file_dialog.exec_() == QtWidgets.QFileDialog.Rejected:
            return

        project_dir = file_dialog.selectedFiles()[0]
        project_name = os.path.basename(project_dir)
        topology_file_path = os.path.join(project_dir, project_name + ".gns3")
        old_topology_file_path = os.path.join(project_dir, default_project_name + ".gns3")

        # create the destination directory for project files
        try:
            os.makedirs(project_dir, exist_ok=True)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Save project", "Could not create project directory {}: {}".format(project_dir, e))
            return

        if self._project.temporary():
            # move files if saving from a temporary project
            log.info("Moving project files from {} to {}".format(self._project.filesDir(), project_dir))
            worker = ProcessFilesWorker(self._project.filesDir(), project_dir, move=True, skip_files=[".gns3_temporary"])
            progress_dialog = ProgressDialog(worker, "Project", "Moving project files...", "Cancel", parent=self)
        else:
            # else, just copy the files
            log.info("Copying project files from {} to {}".format(self._project.filesDir(), project_dir))
            worker = ProcessFilesWorker(self._project.filesDir(), project_dir)
            progress_dialog = ProgressDialog(worker, "Project", "Copying project files...", "Cancel", parent=self)
        progress_dialog.show()
        progress_dialog.exec_()

        errors = progress_dialog.errors()
        if errors:
            errors = "\n".join(errors)
            MessageBox(self, "Save project", "Errors detected while saving the project", errors, icon=QtWidgets.QMessageBox.Warning)

        self._project.setName(project_name)
        if self._project.temporary():
            self._project.moveFromTemporaryToPath(project_dir)
            return self.saveProject(topology_file_path)
        else:
            # We save the topology and use the standard restore process to reinitialize everything
            self._project.setTopologyFile(topology_file_path)
            self.saveProject(topology_file_path, random_id=True)

            if os.path.exists(old_topology_file_path):
                try:
                    os.remove(old_topology_file_path)
                except OSError as e:
                    MessageBox(self, "Save project", "Errors detected while saving the project", str(e), icon=QtWidgets.QMessageBox.Warning)
            return self.loadPath(topology_file_path)

    def saveProject(self, path, random_id=False):
        """
        Saves a project.

        :param path: path to project file
        :param random_id: Randomize project and vm id (use for save as)
        """

        topology = Topology.instance()
        topology.project = self._project
        try:
            self._project.commit()
            topo = topology.dump(random_id=random_id)
            log.info("Saving project: {}".format(path))
            content = json.dumps(topo, sort_keys=True, indent=4)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Save", "Could not save project to {}: {}".format(path, e))
            return False

        if self._settings["auto_screenshot"]:
            self._createScreenshot(os.path.join(os.path.dirname(path), "screenshot.png"))
        self.uiStatusBar.showMessage("Project saved to {}".format(path), 2000)
        self._project.setTopologyFile(path)
        self._setCurrentFile(path)

        self._analytics_client.sendScreenView("Main Window")

        return True

    def _convertOldProject(self, path):
        """
        Converts old ini-style GNS3 topologies (<=0.8.7) to the newer version 1+ JSON format.

        :param path: path to the project file.
        """

        try:
            from gns3converter.main import do_conversion, get_snapshots, ConvertError
        except ImportError as e:
            log.error("GNS3 converter is missing: {}".format(str(e)))
            QtWidgets.QMessageBox.critical(self, "GNS3 converter", "Please install gns3-converter in order to open old ini-style GNS3 projects")
            self._createTemporaryProject()
            return

        try:
            project_name = os.path.basename(os.path.dirname(path))
            project_dir = os.path.join(self.projectsDirPath(), project_name)

            while os.path.isdir(project_dir):
                text, ok = QtWidgets.QInputDialog.getText(self,
                                                          "GNS3 converter",
                                                          "Project '{}' already exists. Please choose an alternative project name:".format(project_name),
                                                          text=project_name + "2")
                if ok:
                    project_name = text
                    project_dir = os.path.join(self.projectsDirPath(), project_name)
                else:
                    self._createTemporaryProject()
                    return

            for snapshot_def in get_snapshots(path):
                do_conversion(snapshot_def, project_name, project_dir, quiet=True)

            topology_def = {'file': path, 'snapshot': False}
            do_conversion(topology_def, project_name, project_dir, quiet=True)
        except ConvertError as e:
            QtWidgets.QMessageBox.critical(self, "GNS3 converter", "Could not convert {}: {}".format(path, e))
            self._createTemporaryProject()
            return
        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_tb)
            tb = "".join(lines)
            MessageBox(self, "GNS3 converter", "Unexpected exception while converting {}".format(path), details=tb)
            self._createTemporaryProject()
            return

        QtWidgets.QMessageBox.information(self, "GNS3 converter", "Your project has been converted to a new format and can be found in: {}".format(project_dir))
        project_path = os.path.join(project_dir, project_name + ".gns3")
        self._loadProject(project_path)

    def _loadProject(self, path):
        """
        Loads a project into GNS3.

        :param path: path to project file
        """

        self._project = Project()
        self.uiGraphicsView.reset()
        topology = Topology.instance()
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

            extension = os.path.splitext(path)[1]
            if extension == ".net":
                self._convertOldProject(path)
                return
            topology.loadFile(path, self._project)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Load", "Could not load project {}: {}".format(os.path.basename(path), e))
            # log.error("exception {type}".format(type=type(e)), exc_info=1)
            self._createTemporaryProject()
            return False
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, "Load", "Invalid or corrupted file: {}".format(e))
            self._createTemporaryProject()
            return False
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        self.uiStatusBar.showMessage("Project loaded {}".format(path), 2000)
        self._setCurrentFile(path)
        self._labInstructionsActionSlot(silent=True)

        return True

    def _createTemporaryProject(self):
        """
        Creates a temporary project.
        """

        if self._project:
            self._project.close()
        self._project = Project()
        self._project.setTemporary(True)
        self._project.setName("unsaved")
        self.uiGraphicsView.reset()
        self._setCurrentFile()

    def isTemporaryProject(self):
        """
        Returns either this is a temporary project or not.

        :returns: boolean
        """

        return self._project.temporary()

    def _setCurrentFile(self, path=None):
        """
        Sets the current project file path.

        :param path: path to project file
        """

        if not path:
            self.setWindowFilePath("Unsaved project")
            self.setWindowTitle("Unsaved project[*] - GNS3")
        else:
            path = os.path.normpath(path)
            self.setWindowFilePath(path)
            self.setWindowTitle("{path}[*] - GNS3".format(path=os.path.basename(path)))
            self._updateRecentFileSettings(path)
            self._updateRecentFileActions()

        self.setWindowModified(False)

    def _updateRecentFileSettings(self, path):
        """
        Updates the recent file settings.

        :param path: path to the new file
        """

        recent_files = []
        for file_path in self._settings["recent_files"]:
            if file_path:
                file_path = os.path.normpath(file_path)
                if file_path not in recent_files and os.path.exists(file_path):
                    recent_files.append(file_path)

        # update the recent file list
        if path in recent_files:
            recent_files.remove(path)
        recent_files.insert(0, path)
        if len(recent_files) > self._max_recent_files:
            recent_files.pop()

        # write the recent file list
        self._settings["recent_files"] = recent_files
        self.setSettings(self._settings)

    def _updateRecentFileActions(self):
        """
        Updates recent file actions.
        """

        index = 0
        size = len(self._settings["recent_files"])
        for file_path in self._settings["recent_files"]:
            try:
                if file_path and os.path.exists(file_path):
                    action = self._recent_file_actions[index]
                    action.setText(" {}. {}".format(index + 1, os.path.basename(file_path)))
                    action.setData(file_path)
                    action.setVisible(True)
                    index += 1
            # We can have this error if user save a file with unicode char
            # and change his system locale.
            except UnicodeEncodeError:
                pass

        for index in range(size + 1, self._max_recent_files):
            self._recent_file_actions[index].setVisible(False)

        if size:
            self._recent_file_actions_separator.setVisible(True)

    @staticmethod
    def projectsDirPath():
        """
        Returns the projects directory path.

        :returns: path to the default projects directory
        """

        return Servers.instance().localServerSettings()["projects_path"]

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of MainWindow.

        :returns: instance of MainWindow
        """

        if not hasattr(MainWindow, "_instance"):
            MainWindow._instance = MainWindow()
        return MainWindow._instance

    def project_created(self, project):
        """
        This slot is invoked when a project is created or opened

        :param project: path to gns3 project file currently opened
        """

        if self._project.temporary():
            # do nothing if project is temporary
            return

        try:
            with open(project, encoding="utf-8") as f:
                json_topology = json.load(f)
                if not isinstance(json_topology, dict):
                    raise ValueError("Not a GNS3 project")
        except (OSError, ValueError) as e:
            QtWidgets.QMessageBox.critical(self, "Project", "Could not read project: {}".format(e))

    def run_later(self, counter, callback):
        """
        Run a function after X milliseconds

        :params counter: Time to wait before fire the callback (in milliseconds)
        :params callback: Function to run
        """

        QtCore.QTimer.singleShot(counter, callback)

    def _exportProjectActionSlot(self):
        """
        Slot called to export a portable project
        """

        running_nodes = self._running_nodes()
        if running_nodes:
            nodes = "\n".join(running_nodes)
            MessageBox(self, "Export project", "Please stop the following nodes before exporting the project", nodes)
            return

        if self.testAttribute(QtCore.Qt.WA_WindowModified):
            QtWidgets.QMessageBox.critical(self, "Export project", "Please save the project before exporting it")
            return

        if self._project.temporary():
            QtWidgets.QMessageBox.critical(self, "Export project", "A temporary project cannot be exported")
            return

        topology = Topology.instance()
        for node in topology.nodes():
            if node.__class__.__name__ in ["VirtualBoxVM", "VMwareVM"]:
                QtWidgets.QMessageBox.critical(self, "Export portable project" "A project containing VMware or VirtualBox VMs cannot be exported because the VMs are managed by these software.")
                return

        include_image_question = """Would you like to include any base image?

The project will not require additional images to run on another host, however the resulting file will be much bigger.

It is your responsability to check if you have the right to distribute the image(s) as part of the project.
        """

        reply = QtWidgets.QMessageBox.question(self, "Export project", include_image_question,
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        include_images = int(reply == QtWidgets.QMessageBox.Yes)

        if not os.path.exists(self._project.readmePathFile()):
            text, ok = QtWidgets.QInputDialog.getMultiLineText(self, "Export project",
                                                               "Please provide a description for the project, especially if you want to share it. \nThe description will be saved in README.txt inside the project file",
                                                               "Project title\n\nAuthor: Grace Hopper <grace@hopper.com>\n\nThis project is about...")
            if not ok:
                return
            try:
                with open(self._project.readmePathFile(), 'w+') as f:
                    f.write(text)
            except OSError as e:
                QtWidgets.QMessageBox.critical(self, "Export project", "Could not create {}: {}".format(self._project.readmePathFile(), e))
                return

        for server in self._project.servers():
            if not server.isLocal() and not server.isGNS3VM():
                QtWidgets.QMessageBox.critical(self, "Export project", "Projects running on a remote server cannot be exported. Only projects running locally or in the GNS3 VM are supported.")
                return

        directory = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        if len(directory) == 0:
            directory = self.projectsDirPath()

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export portable project", directory,
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)",
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)")
        if path is None or len(path) == 0:
            return

        if not path.endswith(".gns3project") or not path.endswith(".gns3p"):
            path += ".gns3project"

        try:
            open(path, 'wb+').close()
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Export project", "Could not write {}: {}".format(path, e))
            return

        export_worker = ExportProjectWorker(self._project, path, include_images)
        progress_dialog = ProgressDialog(export_worker, "Exporting project", "Exporting portable project files...", "Cancel", parent=self)
        progress_dialog.show()
        progress_dialog.exec_()

    def _importProjectActionSlot(self):
        """
        Slot called to import a portable project
        """

        directory = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)
        if len(directory) == 0:
            directory = self.projectsDirPath()
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        "Import project",
                                                        directory,
                                                        "All files (*.*);;GNS3 Portable Project (*.gns3project *.gns3p)",
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)")
        if not path:
            return
        self.loadPath(path)

    def _setStyle(self, style):

        if style.startswith("Charcoal"):
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
        self.uiOpenApplianceAction.setIcon(QtGui.QIcon(":/icons/open.svg"))
        self.uiSaveProjectAction.setIcon(QtGui.QIcon(":/icons/save.svg"))
        self.uiSaveProjectAsAction.setIcon(QtGui.QIcon(":/icons/save-as.svg"))
        self.uiImportExportConfigsAction.setIcon(QtGui.QIcon(":/icons/import_export_configs.svg"))
        self.uiImportProjectAction.setIcon(QtGui.QIcon(":/icons/import_config.svg"))
        self.uiExportProjectAction.setIcon(QtGui.QIcon(":/icons/export_config.svg"))
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
        self.uiEditReadmeAction.setIcon(QtGui.QIcon(":/icons/edit.svg"))
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
        self.uiOpenApplianceAction.setIcon(self._getStyleIcon(":/classic_icons/open.svg", ":/classic_icons/open-hover.svg"))
        self.uiSaveProjectAction.setIcon(self._getStyleIcon(":/classic_icons/save-project.svg", ":/classic_icons/save-project-hover.svg"))
        self.uiSaveProjectAsAction.setIcon(self._getStyleIcon(":/classic_icons/save-as-project.svg", ":/classic_icons/save-as-project-hover.svg"))
        self.uiImportExportConfigsAction.setIcon(self._getStyleIcon(":/classic_icons/import_export_configs.svg", ":/classic_icons/import_export_configs-hover.svg"))
        self.uiImportProjectAction.setIcon(self._getStyleIcon(":/classic_icons/import.svg", ":/classic_icons/import-hover.svg"))
        self.uiExportProjectAction.setIcon(self._getStyleIcon(":/classic_icons/export.svg", ":/classic_icons/export-hover.svg"))
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
        self.uiEditReadmeAction.setIcon(self._getStyleIcon(":/classic_icons/edit.svg", ":/classic_icons/edit.svg"))
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

        stylefile = QtCore.QFile(":/styles/charcoal.css")
        stylefile.open(QtCore.QFile.ReadOnly)
        style = QtCore.QTextStream(stylefile).readAll()
        if sys.platform.startswith("darwin"):
            style += "QDockWidget::title {text-align: center; background-color: #535353}"

        self.setStyleSheet(style)
        self.uiNewProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/new-project.svg", ":/charcoal_icons/new-project-hover.svg"))
        self.uiOpenProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/open.svg", ":/charcoal_icons/open-hover.svg"))
        self.uiOpenApplianceAction.setIcon(self._getStyleIcon(":/charcoal_icons/open.svg", ":/charcoal_icons/open-hover.svg"))
        self.uiSaveProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/save-project.svg", ":/charcoal_icons/save-project-hover.svg"))
        self.uiSaveProjectAsAction.setIcon(self._getStyleIcon(":/charcoal_icons/save-as-project.svg", ":/charcoal_icons/save-as-project-hover.svg"))
        self.uiImportExportConfigsAction.setIcon(self._getStyleIcon(":/charcoal_icons/import_export_configs.svg", ":/charcoal_icons/import_export_configs-hover.svg"))
        self.uiImportProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/import.svg", ":/charcoal_icons/import-hover.svg"))
        self.uiExportProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/export.svg", ":/charcoal_icons/export-hover.svg"))
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
        self.uiEditReadmeAction.setIcon(self._getStyleIcon(":/charcoal_icons/edit.svg", ":/charcoal_icons/edit.svg"))
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
