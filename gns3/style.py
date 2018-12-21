# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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
Sets window styles
"""

import sys
from gns3.qt import QtCore, QtGui


class Style:

    """
    Apply styles

    :param main_window: MainWindow instance.
    """

    def __init__(self, main_window):

        self._mw = main_window

    def _getStyleIcon(self, normal_file, active_file):

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(normal_file), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(active_file), QtGui.QIcon.Active, QtGui.QIcon.Off)
        return icon

    def setLegacyStyle(self):
        """
        Sets the legacy GUI style.
        """

        self._mw.setStyleSheet("")
        self._mw.uiNewProjectAction.setIcon(QtGui.QIcon(":/icons/new-project.svg"))
        self._mw.uiOpenProjectAction.setIcon(QtGui.QIcon(":/icons/open.svg"))
        self._mw.uiOpenApplianceAction.setIcon(QtGui.QIcon(":/icons/open.svg"))
        self._mw.uiNewTemplateAction.setIcon(QtGui.QIcon(":/icons/plus.svg"))
        self._mw.uiSaveProjectAsAction.setIcon(QtGui.QIcon(":/icons/save-as.svg"))
        self._mw.uiEditProjectAction.setIcon(QtGui.QIcon(":/icons/edit.svg"))
        self._mw.uiImportExportConfigsAction.setIcon(QtGui.QIcon(":/icons/import_export_configs.svg"))
        self._mw.uiImportProjectAction.setIcon(QtGui.QIcon(":/icons/import.svg"))
        self._mw.uiExportProjectAction.setIcon(QtGui.QIcon(":/icons/export.svg"))
        self._mw.uiDeleteProjectAction.setIcon(QtGui.QIcon(":/icons/delete.svg"))
        self._mw.uiScreenshotAction.setIcon(QtGui.QIcon(":/icons/camera-photo.svg"))
        self._mw.uiSnapshotAction.setIcon(QtGui.QIcon(":/icons/snapshot.svg"))
        self._mw.uiQuitAction.setIcon(QtGui.QIcon(":/icons/quit.svg"))
        self._mw.uiPreferencesAction.setIcon(QtGui.QIcon(":/icons/applications.svg"))
        self._mw.uiZoomInAction.setIcon(QtGui.QIcon(":/icons/zoom-in.png"))
        self._mw.uiZoomOutAction.setIcon(QtGui.QIcon(":/icons/zoom-out.png"))
        self._mw.uiShowPortNamesAction.setIcon(QtGui.QIcon(":/icons/show-interface-names.svg"))
        self._mw.uiStartAllAction.setIcon(self._getStyleIcon(":/icons/start.svg", ":/icons/start-hover.svg"))
        self._mw.uiSuspendAllAction.setIcon(self._getStyleIcon(":/icons/pause.svg", ":/icons/pause-hover.svg"))
        self._mw.uiStopAllAction.setIcon(self._getStyleIcon(":/icons/stop.svg", ":/icons/stop-hover.svg"))
        self._mw.uiReloadAllAction.setIcon(QtGui.QIcon(":/icons/reload.svg"))
        self._mw.uiAuxConsoleAllAction.setIcon(QtGui.QIcon(":/icons/aux-console.svg"))
        self._mw.uiConsoleAllAction.setIcon(QtGui.QIcon(":/icons/console.svg"))
        self._mw.uiAddNoteAction.setIcon(QtGui.QIcon(":/icons/add-note.svg"))
        self._mw.uiInsertImageAction.setIcon(QtGui.QIcon(":/icons/image.svg"))
        self._mw.uiDrawRectangleAction.setIcon(self._getStyleIcon(":/icons/rectangle.svg", ":/icons/rectangle-hover.svg"))
        self._mw.uiDrawEllipseAction.setIcon(self._getStyleIcon(":/icons/ellipse.svg", ":/icons/ellipse-hover.svg"))
        self._mw.uiDrawLineAction.setIcon(QtGui.QIcon(":/icons/vertically.svg"))
        self._mw.uiEditReadmeAction.setIcon(QtGui.QIcon(":/icons/edit.svg"))
        self._mw.uiOnlineHelpAction.setIcon(QtGui.QIcon(":/icons/help.svg"))
        self._mw.uiBrowseRoutersAction.setIcon(self._getStyleIcon(":/icons/router.png", ":/icons/router-hover.png"))
        self._mw.uiBrowseSwitchesAction.setIcon(self._getStyleIcon(":/icons/switch.png", ":/icons/switch-hover.png"))
        self._mw.uiBrowseEndDevicesAction.setIcon(self._getStyleIcon(":/icons/PC.png", ":/icons/PC-hover.png"))
        self._mw.uiBrowseSecurityDevicesAction.setIcon(self._getStyleIcon(":/icons/firewall.png", ":/icons/firewall-hover.png"))
        self._mw.uiBrowseAllDevicesAction.setIcon(self._getStyleIcon(":/icons/browse-all-icons.png", ":/icons/browse-all-icons-hover.png"))
        self._mw.uiAddLinkAction.setIcon(self._getStyleIcon(":/icons/connection-new.svg", ":/charcoal_icons/connection-new-hover.svg"))

        # Lock action has 4 different icons
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/lock.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap(":/icons/lock.svg"), QtGui.QIcon.Active, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap(":/icons/unlock.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/icons/unlock.svg"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        self._mw.uiLockAllAction.setIcon(icon)


    def setClassicStyle(self):
        """
        Sets the classic GUI style.
        """

        self._mw.setStyleSheet("")
        self._mw.uiNewProjectAction.setIcon(self._getStyleIcon(":/classic_icons/new-project.svg", ":/classic_icons/new-project-hover.svg"))
        self._mw.uiOpenProjectAction.setIcon(self._getStyleIcon(":/classic_icons/open.svg", ":/classic_icons/open-hover.svg"))
        self._mw.uiOpenApplianceAction.setIcon(self._getStyleIcon(":/classic_icons/open.svg", ":/classic_icons/open-hover.svg"))
        self._mw.uiNewTemplateAction.setIcon(self._getStyleIcon(":/classic_icons/plus.svg", ":/classic_icons/plus-hover.svg"))
        self._mw.uiSaveProjectAsAction.setIcon(self._getStyleIcon(":/classic_icons/save-as-project.svg", ":/classic_icons/save-as-project-hover.svg"))
        self._mw.uiEditProjectAction.setIcon(self._getStyleIcon(":/classic_icons/edit.svg", ":/classic_icons/edit-hover.svg"))
        self._mw.uiImportExportConfigsAction.setIcon(self._getStyleIcon(":/classic_icons/import_export_configs.svg", ":/classic_icons/import_export_configs-hover.svg"))
        self._mw.uiImportProjectAction.setIcon(self._getStyleIcon(":/classic_icons/import.svg", ":/classic_icons/import-hover.svg"))
        self._mw.uiExportProjectAction.setIcon(self._getStyleIcon(":/classic_icons/export.svg", ":/classic_icons/export-hover.svg"))
        self._mw.uiDeleteProjectAction.setIcon(self._getStyleIcon(":/classic_icons/delete.svg", ":/classic_icons/delete-hover.svg"))
        self._mw.uiScreenshotAction.setIcon(self._getStyleIcon(":/classic_icons/camera-photo.svg", ":/classic_icons/camera-photo-hover.svg"))
        self._mw.uiSnapshotAction.setIcon(self._getStyleIcon(":/classic_icons/snapshot.svg", ":/classic_icons/snapshot-hover.svg"))
        self._mw.uiQuitAction.setIcon(self._getStyleIcon(":/classic_icons/quit.svg", ":/classic_icons/quit-hover.svg"))
        self._mw.uiPreferencesAction.setIcon(self._getStyleIcon(":/classic_icons/preferences.svg", ":/classic_icons/preferences-hover.svg"))
        self._mw.uiZoomInAction.setIcon(self._getStyleIcon(":/classic_icons/zoom-in.svg", ":/classic_icons/zoom-in-hover.svg"))
        self._mw.uiZoomOutAction.setIcon(self._getStyleIcon(":/classic_icons/zoom-out.svg", ":/classic_icons/zoom-out-hover.svg"))
        self._mw.uiShowPortNamesAction.setIcon(self._getStyleIcon(":/classic_icons/show-interface-names.svg", ":/classic_icons/show-interface-names-hover.svg"))
        self._mw.uiStartAllAction.setIcon(self._getStyleIcon(":/classic_icons/start.svg", ":/classic_icons/start-hover.svg"))
        self._mw.uiSuspendAllAction.setIcon(self._getStyleIcon(":/classic_icons/pause.svg", ":/classic_icons/pause-hover.svg"))
        self._mw.uiStopAllAction.setIcon(self._getStyleIcon(":/classic_icons/stop.svg", ":/classic_icons/stop-hover.svg"))
        self._mw.uiReloadAllAction.setIcon(self._getStyleIcon(":/classic_icons/reload.svg", ":/classic_icons/reload-hover.svg"))
        self._mw.uiAuxConsoleAllAction.setIcon(self._getStyleIcon(":/classic_icons/aux-console.svg", ":/classic_icons/aux-console-hover.svg"))
        self._mw.uiConsoleAllAction.setIcon(self._getStyleIcon(":/classic_icons/console.svg", ":/classic_icons/console-hover.svg"))
        self._mw.uiAddNoteAction.setIcon(self._getStyleIcon(":/classic_icons/add-note.svg", ":/classic_icons/add-note-hover.svg"))
        self._mw.uiInsertImageAction.setIcon(self._getStyleIcon(":/classic_icons/image.svg", ":/classic_icons/image-hover.svg"))
        self._mw.uiDrawRectangleAction.setIcon(self._getStyleIcon(":/classic_icons/rectangle.svg", ":/classic_icons/rectangle-hover.svg"))
        self._mw.uiDrawEllipseAction.setIcon(self._getStyleIcon(":/classic_icons/ellipse.svg", ":/classic_icons/ellipse-hover.svg"))
        self._mw.uiDrawLineAction.setIcon(self._getStyleIcon(":/classic_icons/line.svg", ":/classic_icons/line-hover.svg"))
        self._mw.uiEditReadmeAction.setIcon(self._getStyleIcon(":/classic_icons/edit.svg", ":/classic_icons/edit-hover.svg"))
        self._mw.uiOnlineHelpAction.setIcon(self._getStyleIcon(":/classic_icons/help.svg", ":/classic_icons/help-hover.svg"))
        self._mw.uiBrowseRoutersAction.setIcon(self._getStyleIcon(":/classic_icons/router.svg", ":/classic_icons/router-hover.svg"))
        self._mw.uiBrowseSwitchesAction.setIcon(self._getStyleIcon(":/classic_icons/switch.svg", ":/classic_icons/switch-hover.svg"))
        self._mw.uiBrowseEndDevicesAction.setIcon(self._getStyleIcon(":/classic_icons/pc.svg", ":/classic_icons/pc-hover.svg"))
        self._mw.uiBrowseSecurityDevicesAction.setIcon(self._getStyleIcon(":/classic_icons/firewall.svg", ":/classic_icons/firewall-hover.svg"))
        self._mw.uiBrowseAllDevicesAction.setIcon(self._getStyleIcon(":/classic_icons/browse-all-icons.svg", ":/classic_icons/browse-all-icons-hover.svg"))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/classic_icons/add-link.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/classic_icons/add-link-hover.svg"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/classic_icons/add-link-cancel.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._mw.uiAddLinkAction.setIcon(icon)

        # Lock action has 4 different icons
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/classic_icons/lock.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap(":/classic_icons/lock-hover.svg"), QtGui.QIcon.Active, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap(":/classic_icons/unlock.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/classic_icons/unlock-hover.svg"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        self._mw.uiLockAllAction.setIcon(icon)

    def setCharcoalStyle(self):
        """
        Sets the charcoal GUI style.
        """

        style_file = QtCore.QFile(":/styles/charcoal.css")
        style_file.open(QtCore.QFile.ReadOnly)
        style = QtCore.QTextStream(style_file).readAll()
        if sys.platform.startswith("darwin"):
            style += "QDockWidget::title {text-align: center; background-color: #535353}"

        self._mw.setStyleSheet(style)
        self._mw.uiNewProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/new-project.svg", ":/charcoal_icons/new-project-hover.svg"))
        self._mw.uiOpenProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/open.svg", ":/charcoal_icons/open-hover.svg"))
        self._mw.uiOpenApplianceAction.setIcon(self._getStyleIcon(":/charcoal_icons/open.svg", ":/charcoal_icons/open-hover.svg"))
        self._mw.uiNewTemplateAction.setIcon(self._getStyleIcon(":/charcoal_icons/plus.svg", ":/charcoal_icons/plus-hover.svg"))
        self._mw.uiSaveProjectAsAction.setIcon(self._getStyleIcon(":/charcoal_icons/save-as-project.svg", ":/charcoal_icons/save-as-project-hover.svg"))
        self._mw.uiEditProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/edit.svg", ":/charcoal_icons/edit-hover.svg"))
        self._mw.uiImportExportConfigsAction.setIcon(self._getStyleIcon(":/charcoal_icons/import_export_configs.svg", ":/charcoal_icons/import_export_configs-hover.svg"))
        self._mw.uiImportProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/import.svg", ":/charcoal_icons/import-hover.svg"))
        self._mw.uiExportProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/export.svg", ":/charcoal_icons/export-hover.svg"))
        self._mw.uiDeleteProjectAction.setIcon(self._getStyleIcon(":/charcoal_icons/delete.svg", ":/charcoal_icons/delete-hover.svg"))
        self._mw.uiScreenshotAction.setIcon(self._getStyleIcon(":/charcoal_icons/camera-photo.svg", ":/charcoal_icons/camera-photo-hover.svg"))
        self._mw.uiSnapshotAction.setIcon(self._getStyleIcon(":/charcoal_icons/snapshot.svg", ":/charcoal_icons/snapshot-hover.svg"))
        self._mw.uiQuitAction.setIcon(self._getStyleIcon(":/charcoal_icons/quit.svg", ":/charcoal_icons/quit-hover.svg"))
        self._mw.uiPreferencesAction.setIcon(self._getStyleIcon(":/charcoal_icons/preferences.svg", ":/charcoal_icons/preferences-hover.svg"))
        self._mw.uiZoomInAction.setIcon(self._getStyleIcon(":/charcoal_icons/zoom-in.svg", ":/charcoal_icons/zoom-in-hover.svg"))
        self._mw.uiZoomOutAction.setIcon(self._getStyleIcon(":/charcoal_icons/zoom-out.svg", ":/charcoal_icons/zoom-out-hover.svg"))
        self._mw.uiShowPortNamesAction.setIcon(self._getStyleIcon(":/charcoal_icons/show-interface-names.svg", ":/charcoal_icons/show-interface-names-hover.svg"))
        self._mw.uiStartAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/start.svg", ":/charcoal_icons/start-hover.svg"))
        self._mw.uiSuspendAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/pause.svg", ":/charcoal_icons/pause-hover.svg"))
        self._mw.uiStopAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/stop.svg", ":/charcoal_icons/stop-hover.svg"))
        self._mw.uiReloadAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/reload.svg", ":/charcoal_icons/reload-hover.svg"))
        self._mw.uiAuxConsoleAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/aux-console.svg", ":/charcoal_icons/aux-console-hover.svg"))
        self._mw.uiConsoleAllAction.setIcon(self._getStyleIcon(":/charcoal_icons/console.svg", ":/charcoal_icons/console-hover.svg"))
        self._mw.uiAddNoteAction.setIcon(self._getStyleIcon(":/charcoal_icons/add-note.svg", ":/charcoal_icons/add-note-hover.svg"))
        self._mw.uiInsertImageAction.setIcon(self._getStyleIcon(":/charcoal_icons/image.svg", ":/charcoal_icons/image-hover.svg"))
        self._mw.uiDrawRectangleAction.setIcon(self._getStyleIcon(":/charcoal_icons/rectangle.svg", ":/charcoal_icons/rectangle-hover.svg"))
        self._mw.uiDrawEllipseAction.setIcon(self._getStyleIcon(":/charcoal_icons/ellipse.svg", ":/charcoal_icons/ellipse-hover.svg"))
        self._mw.uiDrawLineAction.setIcon(self._getStyleIcon(":/charcoal_icons/line.svg", ":/charcoal_icons/line-hover.svg"))
        self._mw.uiEditReadmeAction.setIcon(self._getStyleIcon(":/charcoal_icons/edit.svg", ":/charcoal_icons/edit-hover.svg"))
        self._mw.uiOnlineHelpAction.setIcon(self._getStyleIcon(":/charcoal_icons/help.svg", ":/charcoal_icons/help-hover.svg"))
        self._mw.uiBrowseRoutersAction.setIcon(self._getStyleIcon(":/charcoal_icons/router.svg", ":/charcoal_icons/router-hover.svg"))
        self._mw.uiBrowseSwitchesAction.setIcon(self._getStyleIcon(":/charcoal_icons/switch.svg", ":/charcoal_icons/switch-hover.svg"))
        self._mw.uiBrowseEndDevicesAction.setIcon(self._getStyleIcon(":/charcoal_icons/pc.svg", ":/charcoal_icons/pc-hover.svg"))
        self._mw.uiBrowseSecurityDevicesAction.setIcon(self._getStyleIcon(":/charcoal_icons/firewall.svg", ":/charcoal_icons/firewall-hover.svg"))
        self._mw.uiBrowseAllDevicesAction.setIcon(self._getStyleIcon(":/charcoal_icons/browse-all-icons.svg", ":/charcoal_icons/browse-all-icons-hover.svg"))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/charcoal_icons/add-link-1.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/charcoal_icons/add-link-1-hover.svg"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/charcoal_icons/add-link-1-cancel.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._mw.uiAddLinkAction.setIcon(icon)

        # Lock action has 4 different icons
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/charcoal_icons/lock.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap(":/charcoal_icons/lock-hover.svg"), QtGui.QIcon.Active, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap(":/charcoal_icons/unlock.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/charcoal_icons/unlock-hover.svg"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        self._mw.uiLockAllAction.setIcon(icon)
