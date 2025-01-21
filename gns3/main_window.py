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

import sys
import os
import time
import logging

from .local_config import LocalConfig
from .local_server import LocalServer
from .modules import MODULES
from .qt import QtGui, QtCore, QtWidgets, qslot
from .controller import Controller
from .node import Node
from .ui.main_window_ui import Ui_MainWindow
from .style import Style
from .dialogs.about_dialog import AboutDialog
from .dialogs.project_dialog import ProjectDialog
from .dialogs.preferences_dialog import PreferencesDialog
from .dialogs.snapshots_dialog import SnapshotsDialog
from .dialogs.export_debug_dialog import ExportDebugDialog
from .dialogs.doctor_dialog import DoctorDialog
from .dialogs.edit_project_dialog import EditProjectDialog
from .dialogs.setup_wizard import SetupWizard
from .settings import GENERAL_SETTINGS
from .items.node_item import NodeItem
from .items.link_item import LinkItem, SvgIconItem
from .items.shape_item import ShapeItem
from .items.label_item import LabelItem
from .topology import Topology
from .http_client import HTTPClient
from .progress import Progress
from .update_manager import UpdateManager
from .dialogs.appliance_wizard import ApplianceWizard
from .dialogs.new_template_wizard import NewTemplateWizard
from .dialogs.notif_dialog import NotifDialog, NotifDialogHandler
from .status_bar import StatusBarHandler
from .registry.appliance import ApplianceError
from .template_manager import TemplateManager
from .appliance_manager import ApplianceManager

log = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    """
    Main window implementation.

    :param parent: parent widget
    """

    # signal to tell the view if the user is adding a link or not
    adding_link_signal = QtCore.pyqtSignal(bool)

    # Signal of settings updates
    settings_updated_signal = QtCore.Signal()

    def __init__(self, parent=None, open_file=None):
        """
        :param open_file: Open this file instead of asking for a new project
        """

        super().__init__(parent)
        self._settings = {}

        self.setupUi(self)
        self.setUnifiedTitleAndToolBarOnMac(True)

        # These widgets will be disabled when no project is loaded
        self.disableWhenNoProjectWidgets = [
            self.uiGraphicsView,
            self.uiAnnotateMenu,
            self.uiAnnotationToolBar,
            self.uiControlToolBar,
            self.uiControlMenu,
            self.uiSaveProjectAsAction,
            self.uiExportProjectAction,
            self.uiScreenshotAction,
            self.uiSnapshotAction,
            self.uiEditProjectAction,
            self.uiDeleteProjectAction,
            self.uiImportExportConfigsAction,
            self.uiLockAllAction
        ]

        self._notif_dialog = NotifDialog(self)
        # Setup logger
        logging.getLogger().addHandler(NotifDialogHandler(self._notif_dialog))
        logging.getLogger().addHandler(StatusBarHandler(self.uiStatusBar))

        self._open_file_at_startup = open_file

        MainWindow._instance = self
        topology = Topology.instance()
        topology.setMainWindow(self)
        topology.project_changed_signal.connect(self._projectChangedSlot)
        Controller.instance().setParent(self)
        LocalServer.instance().setParent(self)

        HTTPClient.setProgressCallback(Progress.instance(self))

        self._first_file_load = True
        self._open_project_path = None
        self._loadSettings()
        self._connections()
        self._maxrecent_files = 5
        self._project_dialog = None
        self.recent_file_actions = []
        self.recent_project_actions = []
        self._start_time = time.time()
        local_config = LocalConfig.instance()
        #local_config.config_changed_signal.connect(self._localConfigChangedSlot)
        self._local_config_timer = QtCore.QTimer(self)
        self._local_config_timer.timeout.connect(local_config.checkConfigChanged)
        self._local_config_timer.start(1000)  # milliseconds
        self._template_manager = TemplateManager().instance()
        self._appliance_manager = ApplianceManager().instance()

        # restore the geometry and state of the main window.
        self._save_gui_state_geometry = True
        self.restoreGeometry(QtCore.QByteArray().fromBase64(self._settings["geometry"].encode()))
        self.restoreState(QtCore.QByteArray().fromBase64(self._settings["state"].encode()))

        # populate the view -> docks menu
        self.uiDocksMenu.addAction(self.uiTopologySummaryDockWidget.toggleViewAction())
        self.uiDocksMenu.addAction(self.uiComputeSummaryDockWidget.toggleViewAction())
        self.uiDocksMenu.addAction(self.uiConsoleDockWidget.toggleViewAction())
        action = self.uiNodesDockWidget.toggleViewAction()
        action.setIconText("All devices")
        self.uiDocksMenu.addAction(action)

        # Sometimes the parent seem invalid https://github.com/GNS3/gns3-gui/issues/2182
        self.uiNodesDockWidget.setParent(self)
        # make sure the dock widget is not open
        self.uiNodesDockWidget.setVisible(False)

        # default directories for QFileDialog
        self._import_configs_from_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        self._export_configs_to_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        self._screenshots_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.PicturesLocation)
        self._pictures_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.PicturesLocation)
        self._appliance_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)
        self._portable_project_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)
        self._project_dir = None

        # add recent file actions to the File menu
        for i in range(0, self._maxrecent_files):
            action = QtWidgets.QAction(self.uiFileMenu)
            action.setVisible(False)
            action.triggered.connect(self.openRecentFileSlot)
            self.recent_file_actions.append(action)
        self.uiFileMenu.insertActions(self.uiQuitAction, self.recent_file_actions)
        self.recent_file_actions_separator = self.uiFileMenu.insertSeparator(self.uiQuitAction)
        self.recent_file_actions_separator.setVisible(False)
        self.updateRecentFileActions()

        # add recent projects to the File menu
        for i in range(0, self._maxrecent_files):
            action = QtWidgets.QAction(self.uiFileMenu)
            action.setVisible(False)
            action.triggered.connect(self.openRecentProjectSlot)
            self.recent_project_actions.append(action)
        self.recent_project_actions_separator = self.uiFileMenu.addSeparator()
        self.recent_project_actions_separator.setVisible(False)
        self.uiFileMenu.addActions(self.recent_project_actions)

        # set the window icon
        self.setWindowIcon(QtGui.QIcon(":/images/gns3.ico"))

        # restore the style
        self._setStyle(self._settings.get("style"))

        if self._settings.get("hide_new_template_button"):
            self.uiNewTemplatePushButton.hide()

        self.setWindowTitle("[*] GNS3")

        # load initial stuff once the event loop isn't busy
        self.run_later(0, self.startupLoading)

    def _connections(self):
        """
        Connect widgets to slots
        """

        # file menu connections
        self.uiNewProjectAction.triggered.connect(self._newProjectActionSlot)
        self.uiOpenProjectAction.triggered.connect(self.openProjectActionSlot)
        self.uiOpenApplianceAction.triggered.connect(self.openApplianceActionSlot)
        self.uiNewTemplateAction.triggered.connect(self._newTemplateActionSlot)
        self.uiSaveProjectAsAction.triggered.connect(self._saveProjectAsActionSlot)
        self.uiExportProjectAction.triggered.connect(self._exportProjectActionSlot)
        self.uiImportProjectAction.triggered.connect(self._importProjectActionSlot)
        self.uiImportExportConfigsAction.triggered.connect(self._importExportConfigsActionSlot)
        self.uiScreenshotAction.triggered.connect(self._screenshotActionSlot)
        self.uiSnapshotAction.triggered.connect(self._snapshotActionSlot)
        self.uiEditProjectAction.triggered.connect(self._editProjectActionSlot)
        self.uiDeleteProjectAction.triggered.connect(self._deleteProjectActionSlot)

        # edit menu connections
        self.uiSelectAllAction.triggered.connect(self._selectAllActionSlot)
        self.uiSelectNoneAction.triggered.connect(self._selectNoneActionSlot)
        self.uiPreferencesAction.triggered.connect(self.preferencesActionSlot)

        # view menu connections
        self.uiActionFullscreen.triggered.connect(self._fullScreenActionSlot)
        self.uiZoomInAction.triggered.connect(self._zoomInActionSlot)
        self.uiZoomOutAction.triggered.connect(self._zoomOutActionSlot)
        self.uiZoomResetAction.triggered.connect(self._zoomResetActionSlot)
        self.uiFitInViewAction.triggered.connect(self._fitInViewActionSlot)
        self.uiShowLayersAction.triggered.connect(self._showLayersActionSlot)
        self.uiResetPortLabelsAction.triggered.connect(self._resetPortLabelsActionSlot)
        self.uiShowPortNamesAction.triggered.connect(self._showPortNamesActionSlot)
        self.uiShowGridAction.triggered.connect(self._showGridActionSlot)
        self.uiSnapToGridAction.triggered.connect(self._snapToGridActionSlot)
        self.uiLockAllAction.triggered.connect(self._lockActionSlot)
        self.uiResetGUIStateAction.triggered.connect(self._resetGUIState)
        self.uiResetDocksAction.triggered.connect(self._resetDocksSlot)

        # tool menu connections
        self.uiWebUIAction.triggered.connect(self._openWebInterfaceActionSlot)

        # control menu connections
        self.uiStartAllAction.triggered.connect(self._startAllActionSlot)
        self.uiSuspendAllAction.triggered.connect(self._suspendAllActionSlot)
        self.uiStopAllAction.triggered.connect(self._stopAllActionSlot)
        self.uiReloadAllAction.triggered.connect(self._reloadAllActionSlot)
        self.uiAuxConsoleAllAction.triggered.connect(self._auxConsoleAllActionSlot)
        self.uiConsoleAllAction.triggered.connect(self._consoleAllActionSlot)
        self.uiResetConsoleAllAction.triggered.connect(self._consoleResetAllActionSlot)

        # device menu is contextual and is build on-the-fly
        self.uiDeviceMenu.aboutToShow.connect(self._deviceMenuActionSlot)

        # annotate menu connections
        self.uiAddNoteAction.triggered.connect(self._addNoteActionSlot)
        self.uiInsertImageAction.triggered.connect(self._insertImageActionSlot)
        self.uiDrawRectangleAction.triggered.connect(self._drawRectangleActionSlot)
        self.uiDrawEllipseAction.triggered.connect(self._drawEllipseActionSlot)
        self.uiDrawLineAction.triggered.connect(self._drawLineActionSlot)
        self.uiEditReadmeAction.triggered.connect(self._editReadmeActionSlot)

        # help menu connections
        self.uiOnlineHelpAction.triggered.connect(self._onlineHelpActionSlot)
        self.uiCheckForUpdateAction.triggered.connect(self._checkForUpdateActionSlot)
        self.uiSetupWizard.triggered.connect(self._setupWizardActionSlot)
        self.uiAboutQtAction.triggered.connect(self._aboutQtActionSlot)
        self.uiAboutAction.triggered.connect(self._aboutActionSlot)
        self.uiExportDebugInformationAction.triggered.connect(self._exportDebugInformationSlot)
        self.uiDoctorAction.triggered.connect(self._doctorSlot)
        self.uiAcademyAction.triggered.connect(self._academyActionSlot)
        self.uiShortcutsAction.triggered.connect(self._shortcutsActionSlot)

        # browsers tool bar connections
        self.uiBrowseRoutersAction.triggered.connect(self._browseRoutersActionSlot)
        self.uiBrowseSwitchesAction.triggered.connect(self._browseSwitchesActionSlot)
        self.uiBrowseEndDevicesAction.triggered.connect(self._browseEndDevicesActionSlot)
        self.uiBrowseSecurityDevicesAction.triggered.connect(self._browseSecurityDevicesActionSlot)
        self.uiBrowseAllDevicesAction.triggered.connect(self._browseAllDevicesActionSlot)
        self.uiAddLinkAction.triggered.connect(self._addLinkActionSlot)

        # new template button
        self.uiNewTemplatePushButton.clicked.connect(self._newTemplateActionSlot)

        # connect the signal to the view
        self.adding_link_signal.connect(self.uiGraphicsView.addingLinkSlot)

        # connect to the signal when settings change
        self.settings_updated_signal.connect(self.settingsChangedSlot)

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, GENERAL_SETTINGS)

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
            self._setStyle(style)

        self._settings.update(new_settings)
        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)
        self.settings_updated_signal.emit()

    def _openWebInterfaceActionSlot(self):
        if Controller.instance().connected():
            base_url = Controller.instance().httpClient().fullUrl()
            webui_url = "{}/static/web-ui/bundled".format(base_url)
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(webui_url))

    def _showGridActionSlot(self):
        """
        Called when we ask to display the grid
        """
        self.showGrid(self.uiShowGridAction.isChecked())

        # save settings
        project = Topology.instance().project()
        if project is not None:
            project.setShowGrid(self.uiShowGridAction.isChecked())
            project.update()

    def _snapToGridActionSlot(self):
        """
        Called when user click on the snap to grid menu item
        :return: None
        """
        self.snapToGrid(self.uiSnapToGridAction.isChecked())

        # save settings
        project = Topology.instance().project()
        if project is not None:
            project.setSnapToGrid(self.uiSnapToGridAction.isChecked())
            project.update()

    def _lockActionSlot(self):
        """
        Called when user click on the lock menu item
        :return: None
        """

        if self.uiGraphicsView.isEnabled():
            for item in self.uiGraphicsView.items():
                if not isinstance(item, LinkItem) and not isinstance(item, LabelItem) and not isinstance(item, SvgIconItem):
                    if self.uiLockAllAction.isChecked() and not item.locked():
                        item.setLocked(True)
                    elif not self.uiLockAllAction.isChecked() and item.locked():
                        item.setLocked(False)
                    if item.parentItem() is None:
                        item.updateNode()
                    item.update()

    def _resetGUIState(self):
        """
        Reset the GUI state.
        """

        self._save_gui_state_geometry = False
        self.close()
        if hasattr(sys, "frozen"):
            QtCore.QProcess.startDetached(os.path.abspath(sys.executable), sys.argv)
        else:
            QtWidgets.QMessageBox.information(self, "GUI state","The GUI state has been reset, please restart the application")

    def _resetDocksSlot(self):
        """
        Reset the dock widgets.
        """

        self.uiTopologySummaryDockWidget.setFloating(False)
        self.uiComputeSummaryDockWidget.setFloating(False)
        self.uiConsoleDockWidget.setFloating(False)
        self.uiNodesDockWidget.setFloating(False)

    def _newProjectActionSlot(self):
        """
        Slot called to create a new project.
        """

        # prevents race condition
        if self._project_dialog is not None:
            return

        self._project_dialog = ProjectDialog(self)
        self._project_dialog.show()
        create_new_project = self._project_dialog.exec_()

        if create_new_project:
            Topology.instance().createLoadProject(self._project_dialog.getProjectSettings())

        self._project_dialog = None

    def _newTemplateActionSlot(self):
        """
        Called when user want to create a new template.
        """

        dialog = NewTemplateWizard(self)
        dialog.show()
        dialog.exec_()

    @qslot
    def openApplianceActionSlot(self, *args):
        """
        Slot called to open an appliance.
        """

        directory = self._appliance_dir
        if not os.path.exists(self._appliance_dir):
            directory = Topology.instance().projectsDirPath()
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import appliance", directory,
                                                        "All files (*);;GNS3 Appliance (*.gns3appliance *.gns3a)",
                                                        "GNS3 Appliance (*.gns3appliance *.gns3a)")
        if path:
            self.loadPath(path)
            self._appliance_dir = os.path.dirname(path)

    def openProjectActionSlot(self):
        """
        Slot called to open a project.
        """

        if Controller.instance().isRemote():
            # If the server is remote we use the new project windows with the project library
            self._newProjectActionSlot()
        else:
            directory = self._project_dir
            if self._project_dir is None or not os.path.exists(self._project_dir):
                directory = Topology.instance().projectsDirPath()
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open project", directory,
                                                            "All files (*);;GNS3 Project (*.gns3);;GNS3 Portable Project (*.gns3project *.gns3p);;NET files (*.net)",
                                                            "GNS3 Project (*.gns3)")
            if path:
                self.loadPath(path)
                self._project_dir = os.path.dirname(path)

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

    def openRecentProjectSlot(self):
        """
        Slot called to open recent project from the project menu.
        """

        action = self.sender()
        if action and action.data():
            if len(action.data()) == 2:
                project_id, project_path = action.data()
                Topology.instance().createLoadProject({
                    "project_path": project_path,
                    "project_id": project_id})
            else:
                (project_id, ) = action.data()
                Topology.instance().createLoadProject({"project_id": project_id})

    def loadPath(self, path):
        """Open a file and close the previous project"""

        if not path:
            return

        if self._first_file_load is True:
            self._first_file_load = False
            time.sleep(0.5)  # give some time to the server to initialize

        if self._project_dialog:
            self._project_dialog.reject()
            self._project_dialog = None

        if path.endswith(".gns3project") or path.endswith(".gns3p"):
            # Portable GNS3 project
            Topology.instance().importProject(path)
        elif path.endswith(".net"):
            QtWidgets.QMessageBox.critical(self, "Open project", "Importing legacy project is not supported in 2.0.\nYou must open it using GNS3 1.x in order to convert it or manually run the gns3 converter.")
            return

        elif path.endswith(".gns3appliance") or path.endswith(".gns3a"):
            # GNS3 appliance
            try:
                self._appliance_wizard = ApplianceWizard(self, path)
            except ApplianceError as e:
                QtWidgets.QMessageBox.critical(self, "Appliance", "Error while importing appliance {}: {}".format(path, str(e)))
                return
            self._appliance_wizard.show()
            self._appliance_wizard.exec_()
        elif path.endswith(".gns3"):
            if Controller.instance().isRemote():
                QtWidgets.QMessageBox.critical(self, "Open project", "Cannot open a .gns3 file on a remote server, please use a portable project (.gns3p) instead")
                return
            else:
                Topology.instance().loadProject(path)
        else:
            try:
                extension = path.split('.')[1]
                QtWidgets.QMessageBox.critical(self, "File open", "Unsupported file extension {} for {}".format(extension, path))
            except IndexError:
                QtWidgets.QMessageBox.critical(self, "File open", "Missing file extension for {}".format(path))

    @qslot
    def _projectChangedSlot(self, *args):
        """
        Called when a project finish to load
        """
        project = Topology.instance().project()
        if project is not None and self._project_dialog:
            self._project_dialog.reject()
            self._project_dialog = None
        self._refreshVisibleWidgets()

    @qslot
    def settingsChangedSlot(self, *args):
        """
        Called when settings are updated
        """
        # It covers case when project is not set
        # and we need to refresh template manager
        # and appliance manager
        project = Topology.instance().project()
        if project is None:
            self._template_manager.instance().refresh()
            self._appliance_manager.instance().refresh()

    def _refreshVisibleWidgets(self):
        """
        Refresh widgets that should be visible or not
        """

        # No projects
        if Topology.instance().project() is None:
            for widget in self.disableWhenNoProjectWidgets:
                widget.setEnabled(False)
        else:
            for widget in self.disableWhenNoProjectWidgets:
                widget.setEnabled(True)

    def _saveProjectAsActionSlot(self):
        """
        Slot called to save a project to another location/name.
        """

        Topology.instance().saveProjectAs()

    def _importExportConfigsActionSlot(self):
        """
        Slot called when importing and exporting configs
        for the entire project.
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

    def createScreenshot(self, path):
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

    def showLayers(self, show_layers):
        """
        Shows layers in GUI
        :param show_layers: boolean
        :return: None
        """
        NodeItem.show_layer = show_layers
        ShapeItem.show_layer = show_layers
        for item in self.uiGraphicsView.items():
            item.update()

    def showGrid(self, show_grid):
        """
        Shows grid in GUI
        :param show_grid: boolean
        :return: None
        """
        self.uiGraphicsView.viewport().update()

    def snapToGrid(self, snap_to_grid):
        """
        Snap to grid in GUI
        :param snap_to_grid: boolean
        :return: None
        """
        self.uiGraphicsView.viewport().update()

    def showInterfaceLabels(self, show_interface_labels):
        """
        Show interface labels in GUI
        :param show_interface_labels: boolean
        :return: None
        """
        LinkItem.showPortLabels(show_interface_labels)
        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, LinkItem):
                item.adjust()
        
    def _updateZoomSettings(self, zoom=None):
        """
        Updates zoom settings
        :param zoom integer optional, when not provided then calculated from current view
        :return: None
        """

        if zoom is None:
            zoom = round(self.uiGraphicsView.transform().m11() * 100)

        # save settings
        project = Topology.instance().project()
        if project is not None:
            project.setZoom(zoom)
            project.update()

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

        # add the extension if missing (Mac OS automatically adds an extension already)
        if not sys.platform.startswith("darwin"):
            file_format = "." + selected_filter[:4].lower().strip()
            if not path.endswith(file_format):
                path += file_format

        if not self.createScreenshot(path):
            QtWidgets.QMessageBox.critical(self, "Screenshot", "Could not create screenshot file {}".format(path))

    def _snapshotActionSlot(self):
        """
        Slot called to open the snapshot dialog.
        """

        project = Topology.instance().project()

        dialog = SnapshotsDialog(self, project)
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

        factor_in = pow(2.0, 60 / 240.0)
        self.uiGraphicsView.scaleView(factor_in)
        self._updateZoomSettings()

    def _zoomOutActionSlot(self):
        """
        Slot called to scale out the view.
        """

        factor_out = pow(2.0, -60 / 240.0)
        self.uiGraphicsView.scaleView(factor_out)
        self._updateZoomSettings()

    def _zoomResetActionSlot(self):
        """
        Slot called to reset the zoom.
        """

        self.uiGraphicsView.resetTransform()
        self._updateZoomSettings()

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
        self.showLayers(self.uiShowLayersAction.isChecked())

        # save settings
        project = Topology.instance().project()
        if project is not None:
            project.setShowLayers(self.uiShowLayersAction.isChecked())
            project.update()

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

        self.showInterfaceLabels(self.uiShowPortNamesAction.isChecked())

        # save settings
        project = Topology.instance().project()
        if project is not None:
            project.setShowInterfaceLabels(self.uiShowPortNamesAction.isChecked())
            project.update()

    def _startAllActionSlot(self):
        """
        Slot called when starting all the nodes.
        """

        reply = QtWidgets.QMessageBox.question(self, "Confirm Start All", "Are you sure you want to start all devices?",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                                                   
        if reply == QtWidgets.QMessageBox.No:
            return

        project = Topology.instance().project()
        if project is not None:
            project.start_all_nodes()

    def _suspendAllActionSlot(self):
        """
        Slot called when suspending all the nodes.
        """

        reply = QtWidgets.QMessageBox.question(self, "Confirm Suspend All", "Are you sure you want to suspend all devices?",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.No:
            return

        project = Topology.instance().project()
        if project is not None:
            project.suspend_all_nodes()

    def _stopAllActionSlot(self):
        """
        Slot called when stopping all the nodes.
        """

        reply = QtWidgets.QMessageBox.question(self, "Confirm Stop All", "Are you sure you want to stop all devices?",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.No:
            return

        project = Topology.instance().project()
        if project is not None:
            project.stop_all_nodes()

    def _reloadAllActionSlot(self):
        """
        Slot called when reloading all the nodes.
        """

        reply = QtWidgets.QMessageBox.question(self, "Confirm Reload All", "Are you sure you want to reload all devices?",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.No:
            return

        project = Topology.instance().project()
        if project is not None:
            project.reload_all_nodes()

    def _consoleResetAllActionSlot(self):
        """
        Slot called when reset all console connections.
        """

        project = Topology.instance().project()
        if project is not None:
            project.reset_console_all_nodes()

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

        self.uiGraphicsView.consoleFromAllItems()

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
        file_formats = "Image files (*.svg *.bmp *.jpeg *.jpg *.gif *.pbm *.pgm *.png *.ppm *.xbm *.xpm);;All files (*)"

        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Image", self._pictures_dir, file_formats)
        if not path:
            return
        self._pictures_dir = os.path.dirname(path)

        QtGui.QPixmap(path)
        self.uiGraphicsView.addImage(path)

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

    def _drawLineActionSlot(self):
        """
        Slot called when adding a line on the scene.
        """

        self.uiGraphicsView.addLine(self.uiDrawLineAction.isChecked())

    def _onlineHelpActionSlot(self):
        """
        Slot to launch a browser pointing to the documentation page.
        """

        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://docs.gns3.com/"))

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
            res = setup_wizard.exec_()
            # start and connect to the local server if needed
            LocalServer.instance().localServerAutoStartIfRequired()

    def _shortcutsActionSlot(self):

        shortcuts_text = ""
        for action in self.findChildren(QtWidgets.QAction):
            shortcut = action.shortcut().toString()
            if shortcut:
                shortcuts_text += f"{action.toolTip()}: {shortcut}\n"
        QtWidgets.QMessageBox.information(self, "Shortcuts", shortcuts_text)

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

        dialog = ExportDebugDialog(self, Topology.instance().project())
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
            self.uiNodesDockWidget.populateNodesView(category)

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

    def preferencesActionSlot(self):
        """
        Slot to show the preferences dialog.
        """

        with Progress.instance().context(min_duration=0):
            dialog = PreferencesDialog(self)
            #dialog.restoreGeometry(QtCore.QByteArray().fromBase64(self._settings["preferences_dialog_geometry"].encode()))
            dialog.show()
            dialog.exec_()
            #self._settings["preferences_dialog_geometry"] = bytes(dialog.saveGeometry().toBase64()).decode()
            #self.setSettings(self._settings)

    def _editReadmeActionSlot(self):
        """
        Slot to edit the README file
        """
        Topology.instance().editReadme()

    def resizeEvent(self, event):
        self._notif_dialog.resize()
        super().resizeEvent(event)

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
        elif key == QtCore.Qt.Key_C and event.modifiers() & QtCore.Qt.ControlModifier:
            status_bar_message = self.uiStatusBar.currentMessage()
            if status_bar_message:
                QtWidgets.QApplication.clipboard().setText(status_bar_message)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """
        Handles the event when the main window is closed.

        :param event: QCloseEvent
        """

        if Topology.instance().project():
            reply = QtWidgets.QMessageBox.question(self, "Confirm Exit", "Are you sure you want to exit GNS3?",
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                event.ignore()
                return

        progress = Progress.instance()
        progress.setAllowCancelQuery(True)
        progress.setCancelButtonText("Force quit")

        log.debug("Close the Main Window")
        self._finish_application_closing(close_windows=False)
        event.accept()
        self.uiConsoleTextEdit.closeIO()

    def _finish_application_closing(self, close_windows=True):
        """
        Handles the event when the main window is closed.
        And project closed.

        :params closing: True the windows is currently closing do not try to reclose it
        """

        log.debug("_finish_application_closing")

        if self._save_gui_state_geometry:
            self._settings["geometry"] = bytes(self.saveGeometry().toBase64()).decode()
            self._settings["state"] = bytes(self.saveState().toBase64()).decode()
        else:
            self._settings["geometry"] = ""
            self._settings["state"] = ""
        self.setSettings(self._settings)

        Controller.instance().stopListenNotifications()
        server = LocalServer.instance()
        server.stopLocalServer(wait=True)

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
        topology.project = Topology.instance().project()
        for node in topology.nodes():
            if not node.isAlwaysOn() and node.status() == Node.started:
                return True
        return False

    def startupLoading(self):
        """
        Called by QTimer.singleShot to load everything needed at startup.
        """

        if not LocalConfig.instance().isMainGui():
            reply = QtWidgets.QMessageBox.warning(self, "GNS3", "Another GNS3 GUI is already running. Continue?",
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                sys.exit(1)
                return

        run_as_root_path = LocalConfig.instance().runAsRootPath()

        if not sys.platform.startswith("win") and os.geteuid() == 0:
            # touches file to know that user has run GNS3 as root and to prevent
            # from running as user
            if not os.path.exists(run_as_root_path):
                try:
                    open(run_as_root_path, 'a').close()
                except OSError as e:
                    log.warning("Cannot write `run_as_root` file due to: {}".format(str(e)))

            QtWidgets.QMessageBox.warning(self, "Root", "Running GNS3 as root is not recommended and could be dangerous")

        if not sys.platform.startswith("win") and os.geteuid() != 0 and os.path.exists(run_as_root_path):
            QtWidgets.QMessageBox.critical(
                self, "Run as user",
                "GNS3 has been previously run as root. It is not possible "
                "to change to another user and GNS3 will be shutdown. Please delete the '{}' file "
                "and start the program again.".format(run_as_root_path))

            sys.exit(1)

        # restore debug level
        if self._settings["debug_level"]:
            print("Activating debugging (use command 'debug 0' to deactivate)")
            root = logging.getLogger()
            root.setLevel(logging.DEBUG)

        # restore the style
        self._setStyle(self._settings.get("style"))

        Controller.instance().connected_signal.connect(self._controllerConnectedSlot)
        Controller.instance().project_list_updated_signal.connect(self.updateRecentProjectActions)

        self.uiGraphicsView.setEnabled(False)

        # show the setup wizard
        if not self._settings["hide_setup_wizard"]:
            self._setupWizardActionSlot()
        else:
            # start and connect to the local server if needed
            LocalServer.instance().localServerAutoStartIfRequired()
            if self._open_file_at_startup:
                self.loadPath(self._open_file_at_startup)
                self._open_file_at_startup = None
            elif Topology.instance().project() is None:
                self._newProjectActionSlot()

        if self._settings["check_for_update"]:
            # automatic check for update every week (604800 seconds)
            current_epoch = int(time.mktime(time.localtime()))
            if current_epoch - self._settings["last_check_for_update"] >= 604800:
                # let's check for an update
                self._checkForUpdateActionSlot(silent=True)
                self._settings["last_check_for_update"] = current_epoch
                self.setSettings(self._settings)

    def updateRecentProjectsSettings(self, project_id, project_name, project_path):
        """
        Updates the recent project settings.

        :param project_id: The ID of the project
        :param project_name: The name of the project
        :param project_path: The project path
        """

        # Projects are stored as a list of project_id:project_name
        key = "{}:{}:{}".format(project_id, project_name, project_path)

        recent_projects = []
        for project in self._settings["recent_projects"]:
            recent_projects.append(project)

        # Because the name can change we compare only the project id and path
        for project_key in list(recent_projects):
            if project_key.split(":")[0] == project_id:
                recent_projects.remove(project_key)
        for project_key in list(recent_projects):
            try:
                if project_key.split(":")[2] == project_path:
                    recent_projects.remove(project_key)
            # 2.0.0 alpha1 compatible
            except IndexError:
                pass

        recent_projects.insert(0, key)
        if len(recent_projects) > self._maxrecent_files:
            recent_projects.pop()

        # write the recent file list
        self._settings["recent_projects"] = recent_projects
        self.setSettings(self._settings)

    def updateRecentProjectActions(self):
        """
        Updates recent project actions.
        """

        index = 0
        size = len(self._settings["recent_projects"])
        for project in self._settings["recent_projects"]:
            # Projects are stored as a list of project_id:project_name
            try:
                project_id, project_name, project_path = project.split(":", maxsplit=2)
            except ValueError:  # Compatible with 2.0.0a1
                project_path = None
                project_id, project_name = project.split(":", maxsplit=1)

            if project_id not in [p["project_id"] for p in Controller.instance().projects()]:
                size -= 1
                continue

            action = self.recent_project_actions[index]
            if project_path and os.path.exists(project_path):
                action.setText(" {}. {} [{}]".format(index + 1, project_name, project_path))
                action.setData((project_id, project_path, ))
            else:
                action.setText(" {}. {}".format(index + 1, project_name))
                action.setData((project_id, ))
            index += 1

        if Controller.instance().isRemote():
            for index in range(0, size):
                self.recent_project_actions[index].setVisible(True)
            for index in range(size + 1, self._maxrecent_files):
                self.recent_project_actions[index].setVisible(False)

            if size:
                self.recent_project_actions_separator.setVisible(True)
        else:
            for action in self.recent_project_actions:
                action.setVisible(False)
            self.recent_project_actions_separator.setVisible(False)

    def updateRecentFileSettings(self, path):
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
        if len(recent_files) > self._maxrecent_files:
            recent_files.pop()

        # write the recent file list
        self._settings["recent_files"] = recent_files
        self.setSettings(self._settings)

    def updateRecentFileActions(self):
        """
        Updates recent file actions.
        """

        index = 0
        size = len(self._settings["recent_files"])
        for file_path in self._settings["recent_files"]:
            try:
                if file_path and os.path.exists(file_path):
                    action = self.recent_file_actions[index]
                    duplicate = False
                    for file_path_2 in self._settings["recent_files"]:
                        if file_path != file_path_2 and os.path.basename(file_path) == os.path.basename(file_path_2):
                            duplicate = True
                            break
                    if duplicate:
                        action.setText(" {}. {} [{}]".format(index + 1, os.path.basename(file_path), file_path))
                    else:
                        action.setText(" {}. {}".format(index + 1, os.path.basename(file_path)))
                    action.setData(file_path)
                    action.setVisible(True)
                    index += 1
            # We can have this error if user save a file with unicode char
            # and change his system locale.
            except UnicodeEncodeError:
                pass

        if not Controller.instance().isRemote():
            for index in range(size + 1, self._maxrecent_files):
                self.recent_file_actions[index].setVisible(False)

            if size:
                self.recent_file_actions_separator.setVisible(True)
        else:
            for index in range(0, self._maxrecent_files):
                self.recent_file_actions[index].setVisible(False)
            self.recent_file_actions_separator.setVisible(False)

    def _controllerConnectedSlot(self):
        self.updateRecentFileActions()
        self._refreshVisibleWidgets()

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

        Topology.instance().exportProject()

    def _importProjectActionSlot(self):
        """
        Slot called to import a portable project
        """

        directory = self._portable_project_dir
        if not os.path.exists(directory):
            directory = Topology.instance().projectsDirPath()
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open portable project", directory,
                                                        "All files (*);;GNS3 Portable Project (*.gns3project *.gns3p)",
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)")
        if path:
            Topology.instance().importProject(path)
            self._portable_project_dir = os.path.dirname(path)

    def _editProjectActionSlot(self):
        if Topology.instance().project() is None:
            return
        dialog = EditProjectDialog(self)
        dialog.show()
        dialog.exec_()

    def _deleteProjectActionSlot(self):
        if Topology.instance().project() is None:
            return
        reply = QtWidgets.QMessageBox.warning(
            self,
            "GNS3",
            "The project will be deleted from disk. All files will be removed including the project subdirectories. Continue?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            Topology.instance().deleteProject()

    def _setStyle(self, style_name):
        """
        Applies a style.

        :param style_name: Style name
        """

        style = Style(self)
        if style_name.startswith("Charcoal"):
            style.setCharcoalStyle()
        elif style_name == "Classic":
            style.setClassicStyle()
        else:
            style.setLegacyStyle()

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of MainWindow.

        :returns: instance of MainWindow
        """

        if not hasattr(MainWindow, "_instance"):
            MainWindow._instance = MainWindow()
        return MainWindow._instance
