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
import glob
import logging

from .modules import MODULES
from .qt import QtGui, QtCore
from .servers import Servers
from .node import Node
from .ui.main_window_ui import Ui_MainWindow
from .dialogs.about_dialog import AboutDialog
from .dialogs.new_project_dialog import NewProjectDialog
from .dialogs.preferences_dialog import PreferencesDialog
from .settings import GENERAL_SETTINGS, GENERAL_SETTING_TYPES, CLOUD_SETTINGS, CLOUD_SETTINGS_TYPES
from .utils.progress_dialog import ProgressDialog
from .utils.process_files_thread import ProcessFilesThread
from .utils.wait_for_connection_thread import WaitForConnectionThread
from .utils.message_box import MessageBox
from .ports.port import Port
from .items.node_item import NodeItem
from .items.link_item import LinkItem
from .topology import Topology, TopologyInstance
from .cloud.utils import get_provider
from .cloud.exceptions import KeyPairExists

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

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self._settings = {}
        self._cloud_settings = {}
        self._loadSettings()
        self._connections()
        self._ignore_unsaved_state = False
        self._temporary_project = True
        self._max_recent_files = 5
        self._recent_file_actions = []

        self._project_settings = {
            "project_name": "unsaved",
            "project_path": None,
            "project_files_dir": None,
            "project_type": "local",
        }

        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # do not show the nodes dock widget my default
        self.uiNodesDockWidget.setVisible(False)

        # populate the view -> docks menu
        self.uiDocksMenu.addAction(self.uiTopologySummaryDockWidget.toggleViewAction())
        self.uiDocksMenu.addAction(self.uiConsoleDockWidget.toggleViewAction())
        self.uiDocksMenu.addAction(self.uiNodesDockWidget.toggleViewAction())
        self.uiDocksMenu.addAction(self.uiCloudInspectorDockWidget.toggleViewAction())

        # set the images directory
        self.uiGraphicsView.updateImageFilesDir(self.imagesDirPath())

        # add recent file actions to the File menu
        for i in range(0, self._max_recent_files):
            action = QtGui.QAction(self.uiFileMenu)
            action.setVisible(False)
            action.triggered.connect(self._openRecentFileSlot)
            self._recent_file_actions.append(action)
        self.uiFileMenu.insertActions(self.uiQuitAction, self._recent_file_actions)
        self._recent_file_actions_separator = self.uiFileMenu.insertSeparator(self.uiQuitAction)
        self._recent_file_actions_separator.setVisible(False)
        self._updateRecentFileActions()

        self._cloud_provider = None

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

        # restore the geometry and state of the main window.
        settings = QtCore.QSettings()
        self.restoreGeometry(settings.value("GUI/geometry", QtCore.QByteArray()))
        self.restoreState(settings.value("GUI/state", QtCore.QByteArray()))

        # restore the general settings
        settings.beginGroup(self.__class__.__name__)
        for name, value in GENERAL_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=GENERAL_SETTING_TYPES[name])
        settings.endGroup()

        # restore cloud settings
        settings.beginGroup(CLOUD_SETTINGS_GROUP)
        for name, value in CLOUD_SETTINGS.items():
            self._cloud_settings[name] = settings.value(name, value, type=CLOUD_SETTINGS_TYPES[name])
        settings.endGroup()

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
        self.uiOpenProjectAction.triggered.connect(self._openProjectActionSlot)
        self.uiSaveProjectAction.triggered.connect(self._saveProjectActionSlot)
        self.uiSaveProjectAsAction.triggered.connect(self._saveProjectAsActionSlot)
        self.uiImportExportConfigsAction.triggered.connect(self._importExportConfigsActionSlot)
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
        self.uiShowPortNamesAction.triggered.connect(self._showPortNamesActionSlot)

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

        # project
        self.project_about_to_close_signal.connect(self.shutdown_cloud_instances)
        self.project_new_signal.connect(self.project_created)

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
            project_dialog = NewProjectDialog(self)
            project_dialog.show()
            create_new_project = project_dialog.exec_()

            self.project_about_to_close_signal.emit(self._project_settings["project_path"])

            if create_new_project:
                self.uiGraphicsView.reset()
                new_project_settings = project_dialog.getNewProjectSettings()

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

                if new_project_settings["project_type"] == "cloud":
                    provider = self.cloudProvider
                    if provider is None:
                        log.error("Unable to get a cloud provider")
                        return

                    # create an instance for this project
                    default_flavor = self.cloudSettings()['default_flavor']
                    default_image_id = self.cloudSettings()['default_image']
                    instance, keypair = self._create_instance(new_project_settings["project_name"],
                                                              default_flavor,
                                                              default_image_id)

                    topology = Topology.instance()
                    topology.addInstance(new_project_settings["project_name"], instance.id,
                                         default_flavor, default_image_id,
                                         keypair.private_key, keypair.public_key)

                self._project_settings.update(new_project_settings)
                self._saveProject(new_project_settings["project_path"])

            else:
                self._createTemporaryProject()

            self.project_new_signal.emit(self._project_settings["project_path"])

    def _openProjectActionSlot(self):
        """
        Slot called to open a project.
        """

        path, _ = QtGui.QFileDialog.getOpenFileNameAndFilter(self,
                                                             "Open project",
                                                             self.projectsDirPath(),
                                                             "All files (*.*);;GNS3 project files (*.gns3)",
                                                             "GNS3 project files (*.gns3)")
        if path and self.checkForUnsavedChanges():
            self.project_about_to_close_signal.emit(self._project_settings["project_path"])
            if self.loadProject(path):
                self.project_new_signal.emit(path)

    def _openRecentFileSlot(self):
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
            return self._saveProjectAs()
        else:
            return self._saveProject(self._project_settings["project_path"])

    def _saveProjectAsActionSlot(self):
        """
        Slot called to save a project to another location/name.
        """

        self._saveProjectAs()

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

    def _showPortNamesActionSlot(self):
        """
        Slot called to show the port names on the scene.
        """

        LinkItem.showPortLabels(self.uiShowPortNamesAction.isChecked())
        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, LinkItem):
                item.adjust()

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

        from .telnet_console import telnetConsole
        for item in self.uiGraphicsView.scene().items():
            if isinstance(item, NodeItem) and hasattr(item.node(), "console") and item.node().initialized():
                node = item.node()
                if node.status() != Node.started:
                    continue
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

        try:
            # QtWebKit which is used by NewsDialog is not installed
            # by default on FreeBSD, Solaris and possibly other systems.
            from .dialogs.news_dialog import NewsDialog
        except ImportError:
            return

        dialog = NewsDialog(self)
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
            self.uiNodesView.populateNodesView(category)

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
            self.project_about_to_close_signal.emit(self._project_settings["project_path"])

            # save the geometry and state of the main window.
            settings = QtCore.QSettings()
            settings.setValue("GUI/geometry", self.saveGeometry())
            settings.setValue("GUI/state", self.saveState())
            event.accept()

            servers = Servers.instance()
            servers.stopLocalServer(wait=True)
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
                    return self._saveProjectAs()
                return self._saveProject(self._project_settings["project_path"])
            elif reply == QtGui.QMessageBox.Cancel:
                return False
        self._deleteTemporaryProject()
        return True

    def startupLoading(self):
        """
        Called by QTimer.singleShot to load everything needed at startup.
        """

        self._createTemporaryProject()
        self._newsActionSlot()

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
                        if progress_dialog.exec_() == False:
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

    def _saveProjectAs(self):
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
        return self._saveProject(topology_file_path)

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
        except OSError as e:
            QtGui.QMessageBox.critical(self, "Save", "Could not save project to {}: {}".format(path, e))
            return False

        self.uiStatusBar.showMessage("Project saved to {}".format(path), 2000)
        self._project_settings["project_path"] = path
        self._setCurrentFile(path)
        return True

    def loadProject(self, path):
        """
        Loads a project into GNS3.

        :param path: path to project file
        """

        self.uiGraphicsView.reset()

        project_files_dir = path
        if path.endswith(".gns3"):
            project_files_dir = path[:-5]
        elif path.endswith(".net"):
            project_files_dir = path[:-4]
        self._project_settings["project_files_dir"] = project_files_dir + "-files"

        topology = Topology.instance()
        try:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            with open(path, "r") as f:
                need_to_save = False
                log.info("loading project: {}".format(path))
                json_topology = json.load(f)
                if not os.path.isdir(self._project_settings["project_files_dir"]):
                    os.makedirs(self._project_settings["project_files_dir"])
                self.uiGraphicsView.updateProjectFilesDir(self._project_settings["project_files_dir"])

                # if we're opening a cloud project, fire up instances
                if json_topology["resources_type"] == "cloud":
                    self._project_settings["project_type"] = "cloud"
                    provider = self.cloudProvider
                    new_instances = []
                    for instance in json_topology["topology"]["instances"]:
                        name = instance["name"]
                        flavor = instance["size_id"]
                        image = instance["image_id"]
                        i, k = self._create_instance(name, flavor, image)
                        new_instances.append({
                            "name": i.name,
                            "id": i.id,
                            "size_id": flavor,
                            "image_id": image,
                            "private_key": k.private_key,
                            "public_key": k.public_key
                        })
                    # update topology with new image data
                    json_topology["topology"]["instances"] = new_instances
                    # we need to save the updates
                    need_to_save = True
                else:
                    self._project_settings["project_type"] = "local"

                topology.load(json_topology)

                if need_to_save:
                    self._saveProject(path)
        except OSError as e:
            QtGui.QMessageBox.critical(self, "Load", "Could not load project from {}: {}".format(path, e))
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

        with open(project) as f:
            old_json_topology = json.load(f)

            if old_json_topology["resources_type"] != 'cloud':
                # do nothing in case of local projects
                return

            provider = self.cloudProvider
            if provider is None:
                log.error("Unable to get a cloud provider")
                return

            for instance in old_json_topology["topology"]["instances"]:
                # shutdown the instance, we can pass to libcloud our namedtuple instead of a Node
                # object because only instance.id is actually accessed
                ti = TopologyInstance(**instance)
                self.cloudProvider.delete_instance(ti)
                # delete keypairs
                self.cloudProvider.delete_key_pair_by_name(instance["name"])

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
            self.CloudInspectorView.load(self, project_instances)

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
        self._saveProject(self._project_settings["project_path"])

    def remove_instance_from_project(self, instance):
        """
        Remove an instance from the current project

        :param instance: libcloud Node object
        """
        topology = Topology.instance()
        topology.removeInstance(instance.id)
        # persist infos saving current project
        self._saveProject(self._project_settings["project_path"])

    def _create_instance(self, name, flavor, image_id):
        """
        Wrapper method to handle SSH keypairs creation before actually creating
        an instance
        """
        try:
            keypair = self.cloudProvider.create_key_pair(name)
        except KeyPairExists:
            # delete keypairs if already exist
            self.cloudProvider.delete_key_pair_by_name(name)
            keypair = self.cloudProvider.create_key_pair(name)

        instance = self.cloudProvider.create_instance(name, flavor, image_id, keypair)
        return instance, keypair
