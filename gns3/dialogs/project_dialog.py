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

import os
from ..qt import QtCore, QtGui, QtWidgets, qslot, sip_is_deleted
from ..ui.project_dialog_ui import Ui_ProjectDialog
from ..controller import Controller
from ..topology import Topology


import logging
log = logging.getLogger(__name__)


class ProjectDialog(QtWidgets.QDialog, Ui_ProjectDialog):

    """
    New project dialog.
    """

    def __init__(self, parent, default_project_name="untitled", show_open_options=True):
        """
        :param parent: parent widget.
        :param default_project_name: Project name by default
        :param show_open_options: If true allow to open a project from the dialog
        otherwise it's just for create a project
        """
        super().__init__(parent)
        self.setupUi(self)

        self._main_window = parent
        self._project_settings = {}
        self.uiNameLineEdit.setText(default_project_name)
        self.uiLocationLineEdit.setText(os.path.join(Topology.instance().projectsDirPath(), default_project_name))

        self.uiNameLineEdit.textEdited.connect(self._projectNameSlot)
        self.uiLocationBrowserToolButton.clicked.connect(self._projectPathSlot)
        self.uiSettingsPushButton.clicked.connect(self._settingsClickedSlot)

        if show_open_options:
            self.uiOpenProjectPushButton.clicked.connect(self._openProjectActionSlot)
            self._addRecentFilesMenu()
        else:
            self.uiOpenProjectGroupBox.hide()
            self.uiProjectTabWidget.removeTab(1)

        # If the controller is remote we hide option for local file system
        if Controller.instance().isRemote():
            self.uiLocationLabel.setVisible(False)
            self.uiLocationLineEdit.setVisible(False)
            self.uiLocationBrowserToolButton.setVisible(False)
            self.uiOpenProjectPushButton.setVisible(False)

        self.uiProjectsTreeWidget.itemDoubleClicked.connect(self._projectsTreeWidgetDoubleClickedSlot)
        self.uiDeleteProjectButton.clicked.connect(self._deleteProjectSlot)
        self.uiDuplicateProjectPushButton.clicked.connect(self._duplicateProjectSlot)
        self.uiRefreshProjectsPushButton.clicked.connect(Controller.instance().refreshProjectList)
        Controller.instance().project_list_updated_signal.connect(self._updateProjectListSlot)
        self._updateProjectListSlot()
        Controller.instance().refreshProjectList()

    def _settingsClickedSlot(self):
        """
        When the user click on the settings button
        """
        self.reject()
        self._main_window.preferencesActionSlot()

    def _projectsTreeWidgetDoubleClickedSlot(self, item, column):
        self.done(True)

    @qslot
    def _deleteProjectSlot(self, *args):
        if len(self.uiProjectsTreeWidget.selectedItems()) == 0:
            QtWidgets.QMessageBox.critical(self, "Delete project", "No project selected")
            return

        projects_to_delete = set()
        for project in self.uiProjectsTreeWidget.selectedItems():
            if sip_is_deleted(project):
                continue
            project_id = project.data(0, QtCore.Qt.UserRole)
            project_name = project.data(1, QtCore.Qt.UserRole)

            reply = QtWidgets.QMessageBox.warning(self,
                                                  "Delete project",
                                                  'Delete project "{}"?\nThis cannot be reverted.'.format(project_name),
                                                  QtWidgets.QMessageBox.Yes,
                                                  QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                projects_to_delete.add(project_id)

        for project_id in projects_to_delete:
            Controller.instance().deleteProject(project_id)

    def _duplicateProjectSlot(self):

        if len(self.uiProjectsTreeWidget.selectedItems()) == 0:
            QtWidgets.QMessageBox.critical(self, "Duplicate project", "No project selected")
            return

        if len(self.uiProjectsTreeWidget.selectedItems()) > 1:
            QtWidgets.QMessageBox.critical(self, "Duplicate project", "Please select only one project to duplicate")
            return

        for project in self.uiProjectsTreeWidget.selectedItems():
            project_id = project.data(0, QtCore.Qt.UserRole)
            project_name = project.data(1, QtCore.Qt.UserRole)

            new_project_name = project_name + "-1"
            existing_project_name = [p["name"] for p in Controller.instance().projects()]
            i = 1
            while new_project_name in existing_project_name:
                new_project_name = "{}-{}".format(project_name, i)
                i += 1

            name, reply = QtWidgets.QInputDialog.getText(self,
                                                         "Duplicate project",
                                                         'Duplicate project "{}"?.'.format(project_name),
                                                         QtWidgets.QLineEdit.Normal,
                                                         new_project_name)
            name = name.strip()
            if reply and len(name) > 0:

                reset_mac_addresses = self.uiResetMacAddressesCheckBox.isChecked()

                if Controller.instance().isRemote():
                    Controller.instance().post("/projects/{project_id}/duplicate".format(project_id=project_id),
                                               self._duplicateCallback,
                                               body={"name": name, "reset_mac_addresses": reset_mac_addresses},
                                               progressText="Duplicating project '{}'...".format(name),
                                               timeout=None)
                else:
                    project_location = os.path.join(Topology.instance().projectsDirPath(), name)
                    Controller.instance().post("/projects/{project_id}/duplicate".format(project_id=project_id),
                                               self._duplicateCallback,
                                               body={"name": name, "path": project_location, "reset_mac_addresses": reset_mac_addresses},
                                               progressText="Duplicating project '{}'...".format(name),
                                               timeout=None)

    def _duplicateCallback(self, result, error=False, **kwargs):
        if error:
            log.error("Error while duplicating project: {}".format(result["message"]))
            return
        Controller.instance().refreshProjectList()

    @qslot
    def _updateProjectListSlot(self, *args):
        self.uiProjectsTreeWidget.clear()
        self.uiDeleteProjectButton.setEnabled(False)
        self.uiProjectsTreeWidget.setUpdatesEnabled(False)
        items = []
        for project in Controller.instance().projects():
            path = os.path.join(project["path"], project["filename"])
            item = QtWidgets.QTreeWidgetItem([project["name"], project["status"], path])
            item.setData(0, QtCore.Qt.UserRole, project["project_id"])
            item.setData(1, QtCore.Qt.UserRole, project["name"])
            item.setData(2, QtCore.Qt.UserRole, path)
            items.append(item)
        self.uiProjectsTreeWidget.addTopLevelItems(items)

        if len(Controller.instance().projects()):
            self.uiDeleteProjectButton.setEnabled(True)

        self.uiProjectsTreeWidget.header().setResizeContentsPrecision(100)  # How many row is checked for the resize for performance reason
        self.uiProjectsTreeWidget.resizeColumnToContents(0)
        self.uiProjectsTreeWidget.resizeColumnToContents(1)
        self.uiProjectsTreeWidget.resizeColumnToContents(2)
        self.uiProjectsTreeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        self.uiProjectsTreeWidget.setUpdatesEnabled(True)

    def keyPressEvent(self, e):
        """
        Event handler in order to properly handle escape.
        """

        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def _projectNameSlot(self, text):

        project_dir = Topology.instance().projectsDirPath()
        if os.path.dirname(self.uiLocationLineEdit.text()) == project_dir:
            self.uiLocationLineEdit.setText(os.path.join(project_dir, text))

    def _projectPathSlot(self):
        """
        Slot to select the a new project location.
        """

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Project location", os.path.join(Topology.instance().projectsDirPath(),
                                                                                               self.uiNameLineEdit.text()))

        if path:
            self.uiNameLineEdit.setText(os.path.basename(path))
            self.uiLocationLineEdit.setText(path)

    def getProjectSettings(self):

        return self._project_settings

    def _menuTriggeredSlot(self, action):
        """
        Closes this dialog when a recent project
        has been opened.

        :param action: ignored.
        """

        self.reject()

    def _openProjectActionSlot(self):
        """
        Opens a project and closes this dialog.
        """

        self._main_window.openProjectActionSlot()
        self.reject()

    def _addRecentFilesMenu(self):
        """
        Add recent projects in a menu.
        """

        menu = QtWidgets.QMenu(parent=self)
        if Controller.instance().isRemote():
            for action in self._main_window.recent_project_actions:
                menu.addAction(action)
        else:
            for action in self._main_window.recent_file_actions:
                menu.addAction(action)
        menu.triggered.connect(self._menuTriggeredSlot)
        self.uiRecentProjectsPushButton.setMenu(menu)

    def _overwriteProjectCallback(self, result, error=False, **kwargs):
        if error:
            # A 404 could arrive if someone else as deleted the project
            if "status" not in result or result["status"] != 404:
                return
            elif "message" in result:
                QtWidgets.QMessageBox.critical(self,
                                               "New Project",
                                               "Error while overwrite project: {}".format(result["message"]))
        Controller.instance().refreshProjectList()
        self.done(True)

    def _newProject(self):
        self._project_settings["project_name"] = self.uiNameLineEdit.text().strip()
        if Controller.instance().isRemote():
            self._project_settings.pop("project_path", None)
            self._project_settings.pop("project_files_dir", None)
        else:
            project_location = self.uiLocationLineEdit.text().strip()
            if not project_location:
                QtWidgets.QMessageBox.critical(self, "New project", "Project location is empty")
                return False

            self._project_settings["project_path"] = os.path.join(project_location, self._project_settings["project_name"] + ".gns3")
            self._project_settings["project_files_dir"] = project_location

        if len(self._project_settings["project_name"]) == 0:
            QtWidgets.QMessageBox.critical(self, "New project", "Project name is empty")
            return False

        for existing_project in Controller.instance().projects():
            if self._project_settings["project_name"] == existing_project["name"] \
               and ("project_files_dir" in self._project_settings and self._project_settings["project_files_dir"] == existing_project["path"]):

                if existing_project["status"] == "opened":
                    QtWidgets.QMessageBox.critical(self,
                                                   "New project",
                                                   'Project "{}" is opened, it cannot be overwritten'.format(self._project_settings["project_name"]))
                    return False

                reply = QtWidgets.QMessageBox.warning(self,
                                                      "New project",
                                                      'Project "{}" already exists in location "{}", overwrite it?'.format(existing_project["name"], existing_project["path"]),
                                                      QtWidgets.QMessageBox.Yes,
                                                      QtWidgets.QMessageBox.No)

                if reply == QtWidgets.QMessageBox.Yes:
                    Controller.instance().deleteProject(existing_project["project_id"], self._overwriteProjectCallback)

                # In all cases we cancel the new project and if project success to delete
                # we will call done again
                return False

        return True

    def done(self, result):

        if result:
            if self.uiProjectTabWidget.currentIndex() == 0:
                if not self._newProject():
                    return
            else:
                current = self.uiProjectsTreeWidget.currentItem()
                if current is None:
                    QtWidgets.QMessageBox.critical(self, "Open project", "No project selected")
                    return

                self._project_settings["project_id"] = current.data(0, QtCore.Qt.UserRole)
                self._project_settings["project_name"] = current.data(1, QtCore.Qt.UserRole)
        super().done(result)
