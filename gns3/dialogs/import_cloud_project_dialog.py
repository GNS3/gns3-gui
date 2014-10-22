"""
Dialog for importing cloud projects
"""

from ..ui.import_cloud_project_dialog_ui import Ui_ImportCloudProjectDialog
from ..qt import QtGui
from ..cloud.utils import get_cloud_projects, DownloadProjectThread
from ..utils.progress_dialog import ProgressDialog


class ImportCloudProjectDialog(QtGui.QDialog, Ui_ImportCloudProjectDialog):
    """
    Import cloud project dialog implementation.
    """

    def __init__(self, parent, project_dest_path, images_dest_path, cloud_settings):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.project_dest_path = project_dest_path
        self.images_dest_path = images_dest_path
        self.cloud_settings = cloud_settings

        self.uiImportProjectAction.clicked.connect(self._importProject)
        self._listCloudProjects()

    def _importProject(self):
        project_file_name = self.projects[self.listWidget.currentItem().text()]

        download_thread = DownloadProjectThread(
            project_file_name,
            self.project_dest_path,
            self.images_dest_path,
            self.cloud_settings
        )
        progress_dialog = ProgressDialog(download_thread, "Importing project", "Downloading project files...", "Cancel",
                                         parent=self.parent())

        progress_dialog.show()
        progress_dialog.exec_()

        self.close()

    def _listCloudProjects(self):
        self.projects = get_cloud_projects(self.cloud_settings)
        self.listWidget.addItems(list(self.projects.keys()))
