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
import datetime

from gns3.qt import QtCore, QtWidgets
from ..local_server import LocalServer
from ..utils.progress_dialog import ProgressDialog
from ..utils.export_project_worker import ExportProjectWorker
from ..ui.export_project_wizard_ui import Ui_ExportProjectWizard

import logging
log = logging.getLogger(__name__)


class ExportProjectWizard(QtWidgets.QWizard, Ui_ExportProjectWizard):
    """
    Export project wizard.
    """

    def __init__(self, project, parent):

        super().__init__(parent)
        self.setupUi(self)

        self._project = project
        self._path = None
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtWidgets.QWizard.NoDefaultButton)

        self.uiCompressionComboBox.addItem("None", "none")
        self.uiCompressionComboBox.addItem("Zip compression (deflate)", "zip")
        self.uiCompressionComboBox.addItem("Bzip2 compression", "bzip2")
        self.uiCompressionComboBox.addItem("Lzma compression", "lzma")

        # set zip compression by default
        self.uiCompressionComboBox.setCurrentIndex(1)
        self.helpRequested.connect(self._showHelpSlot)
        self.uiPathBrowserToolButton.clicked.connect(self._pathBrowserSlot)

        readme_text = "Project: '{}' created on {}\nAuthor: John Doe <john.doe@example.com>\n\nNo project description was given".format(self._project.name(), datetime.date.today())
        self.uiReadmeTextEdit.setPlainText(readme_text)

    def _pathBrowserSlot(self):

        directory = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        if len(directory) == 0:
            directory = LocalServer.instance().localServerSettings()["projects_path"]

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export portable project", directory,
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)",
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)")
        if path is None or len(path) == 0:
            return

        self.uiPathLineEdit.setText(path)

    def _showHelpSlot(self):

        include_image_help = """Including base images means additional images will not be requested to
        import the project on another computer, however the resulting file will be much bigger.
        Also, you are responsible to check if you have the right to distribute the image(s) as part of the project.
        """
        QtWidgets.QMessageBox.information(self, "Help about export a project", include_image_help)

    def validateCurrentPage(self):
        """
        Validates if the project can be exported.
        """

        if self.currentPage() == self.uiExportOptionsWizardPage:
            path = self.uiPathLineEdit.text().strip()
            if not path:
                QtWidgets.QMessageBox.critical(self, "Export project", "Please select a path where to export the project")
                return False

            if not path.endswith(".gns3project") and not path.endswith(".gns3p"):
                path += ".gns3project"
            try:
                open(path, 'wb+').close()
            except OSError as e:
                QtWidgets.QMessageBox.critical(self, "Export project", "Cannot export project to '{}': {}".format(path, e))
                return False
            self._path = path
        elif self.currentPage() == self.uiProjectReadmeWizardPage:
            text = self.uiReadmeTextEdit.toPlainText().strip()
            if text:
                self._project.post("/files/README.txt", self._saveReadmeCallback, body=text)
        return True

    def _saveReadmeCallback(self, result, error=False, **kwargs):
        if error:
            QtWidgets.QMessageBox.critical(self, "Export project", "Could not created readme file")

    def done(self, result):
        """
        This dialog is closed.
        """

        if result:
            if self.uiIncludeImagesCheckBox.isChecked():
                include_images = "yes"
            else:
                include_images = "no"
            compression = self.uiCompressionComboBox.currentData()
            export_worker = ExportProjectWorker(self._project, self._path, include_images, compression)
            progress_dialog = ProgressDialog(export_worker, "Exporting project", "Exporting portable project files...", "Cancel", parent=self, create_thread=False)
            progress_dialog.show()
            progress_dialog.exec_()
        super().done(result)
