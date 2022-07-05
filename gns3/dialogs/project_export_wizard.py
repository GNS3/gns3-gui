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

from gns3.qt import QtCore, QtWidgets, QtGui
from gns3.utils import parse_version
from gns3.http_client_error import HttpClientError, HttpClientCancelledRequestError
from gns3.local_server import LocalServer
from gns3.ui.export_project_wizard_ui import Ui_ExportProjectWizard

import logging
log = logging.getLogger(__name__)


class ExportProjectWizard(QtWidgets.QWizard, Ui_ExportProjectWizard):
    """
    Export project wizard.
    """

    readme_signal = QtCore.pyqtSignal()

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
        self.uiCompressionComboBox.addItem("Zstandard compression", "zstd")
        self.uiCompressionComboBox.currentIndexChanged.connect(self._compressionChangedSlot)

        # set zstd compression by default
        self.uiCompressionComboBox.setCurrentIndex(4)
        self.helpRequested.connect(self._showHelpSlot)
        self.uiPathBrowserToolButton.clicked.connect(self._pathBrowserSlot)

        # QTextDocument before Qt version 5.14 doesn't support Markdown
        if parse_version(QtCore.QT_VERSION_STR) < parse_version("5.14.0") or parse_version(QtCore.PYQT_VERSION_STR) < parse_version("5.14.0"):
            self._use_markdown = False
        else:
            self._use_markdown = True

        self._readme_filename = "README.txt"
        self.uiTabWidget.currentChanged.connect(self._previewMarkdownSlot)
        self._loadReadme()

    def _loadReadme(self):

        self._project.get("/files/{}".format(self._readme_filename), self._loadedReadme, raw=True)

    def _loadedReadme(self, result, error=False, context={}, **kwargs):

        if not error:
            content = result.decode("utf-8", errors="replace")
            self.uiReadmeTextEdit.setPlainText(content)
        else:
            if self._use_markdown:
                readme_markdown = "# Project {}\n\nCreated on: {}\n\nAuthor: John Doe <john.doe@example.com>\n\n## Description\n\nNo project description was given".format(self._project.name(), datetime.date.today())
                self.uiReadmeTextEdit.setPlainText(readme_markdown)
            else:
                readme_text = "Project: '{}' created on {}\nAuthor: John Doe <john.doe@example.com>\n\nNo project description was given".format(self._project.name(), datetime.date.today())
                self.uiReadmeTextEdit.setPlainText(readme_text)

    def _pathBrowserSlot(self):

        directory = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        if len(directory) == 0:
            directory = LocalServer.instance().localServerSettings()["projects_path"]

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export project", directory,
                                                        "GNS3 Project (*.gns3project *.gns3p)",
                                                        "GNS3 Project (*.gns3project *.gns3p)")
        if path is None or len(path) == 0:
            return

        self.uiPathLineEdit.setText(path)

    def _previewMarkdownSlot(self, index):

        # index 1 is preview tab
        if index == 1:

            if self._use_markdown is False:
                QtWidgets.QMessageBox.critical(self, "Markdown preview", "Markdown preview is only support with Qt version 5.14.0 or above")
                return

            # show Markdown preview
            document = QtGui.QTextDocument()
            self.uiReadmePreviewEdit.setDocument(document)
            document.setMarkdown(self.uiReadmeTextEdit.toPlainText())

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
        return True

    def _saveReadmeCallback(self, result, error=False, **kwargs):
        if error:
            QtWidgets.QMessageBox.critical(self, "Export project", "Could not created readme file")
        self.readme_signal.emit()

    def waitForReadme(self, signal, timeout=10000):

        # inspired from https://www.jdreaver.com/posts/2014-07-03-waiting-for-signals-pyside-pyqt.html
        loop = QtCore.QEventLoop()
        signal.connect(loop.quit)
        if timeout is not None:
            QtCore.QTimer.singleShot(timeout, loop.quit)
        loop.exec_()

    def _compressionChangedSlot(self, index):
        """
        Set the default compression level.
        """

        compression = self.uiCompressionComboBox.itemData(index)
        self.uiCompressionLevelSpinBox.setEnabled(True)
        if compression == "zip":
            self.uiCompressionLevelSpinBox.setValue(6)  # ZIP default compression level is 6
        elif compression == "bzip2":
            self.uiCompressionLevelSpinBox.setValue(9)  # BZIP2 default compression level is 9
        elif compression == "zstd":
            self.uiCompressionLevelSpinBox.setValue(3)  # ZSTD default compression level is 3
        else:
            # compression level is not supported
            self.uiCompressionLevelSpinBox.setValue(0)
            self.uiCompressionLevelSpinBox.setEnabled(False)

    def done(self, result):
        """
        This dialog is closed.
        """

        if result:

            content = self.uiReadmeTextEdit.toPlainText()
            if content:
                self._project.post("/files/{}".format(self._readme_filename), self._saveReadmeCallback, body=content)

            if self.uiIncludeImagesCheckBox.isChecked():
                include_images = "yes"
            else:
                include_images = "no"
            if self.uiIncludeSnapshotsCheckBox.isChecked():
                include_snapshots = "yes"
            else:
                include_snapshots = "no"
            if self.uiResetMacAddressesCheckBox.isChecked():
                reset_mac_addresses = "yes"
            else:
                reset_mac_addresses = "no"
            compression = self.uiCompressionComboBox.currentData()
            self.waitForReadme(self.readme_signal)

            params = {
                "include_images": include_images,
                "include_snapshots": include_snapshots,
                "reset_mac_addresses": reset_mac_addresses,
                "compression": compression
            }

            try:
                self._project.get(
                    "/export",
                    callback=None,
                    download_progress_callback=self._downloadFileProgress,
                    progress_text="Exporting project files...",
                    params=params,
                    timeout=None,
                    wait=True,
                    raw=True
                )
            except HttpClientCancelledRequestError:
                pass
            except HttpClientError as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Project export",
                    f"Could not export project: {e}"
                )

        super().done(result)

    def _downloadFileProgress(self, content, **kwargs):
        """
        Called for each part of the file
        """

        try:
            with open(self._path, 'ab') as f:
                f.write(content)
        except OSError as e:
            log.error(f"Could not write project file: {e}")
            return
