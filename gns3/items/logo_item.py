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


import urllib.parse

from ..qt import QtCore, QtGui, QtWidgets, QtSvg
from ..qt.qimage_svg_renderer import QImageSvgRenderer
from ..controller import Controller


import logging
log = logging.getLogger(__name__)


class LogoItem(QtSvg.QGraphicsSvgItem):
    """
    Margin for the logo
    """
    MARGIN = 20

    """
    Logo for the scene.

    :param logo_path: Path to the logo (remote)
    :param logo_url: URL which needs to be open user clicks on the logo
    :param project: Current project
    """

    def __init__(self, logo_path, logo_url, project):
        super().__init__()

        self._logo_path = logo_path
        self._logo_url = logo_url
        self._project = project

        # Temporary symbol during loading
        renderer = QImageSvgRenderer(":/icons/reload.svg")
        renderer.setObjectName("symbol_loading")
        self.setSharedRenderer(renderer)

        effect = QtWidgets.QGraphicsColorizeEffect()
        effect.setColor(QtGui.QColor("black"))
        effect.setStrength(0.8)
        self.setGraphicsEffect(effect)
        self.graphicsEffect().setEnabled(False)

        # set graphical settings for this item
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        from ..main_window import MainWindow
        self._main_window = MainWindow.instance()
        self._settings = self._main_window.uiGraphicsView.settings()

        self.updatePosition()

        self._main_window.uiGraphicsView.viewport().installEventFilter(self)

        remote_file = urllib.parse.quote('project-files/images/{}'.format(logo_path))

        Controller.instance().getStatic(
            '/projects/{}/files/{}'.format(project.id(), remote_file),
            self.updateImage
        )

        # make it the last one
        self.setZValue(-2)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Paint:
            self.updatePosition()
        return QtWidgets.QWidget.eventFilter(self, source, event)


    def updateImage(self, local_path):
        renderer = QImageSvgRenderer(local_path)
        renderer.setObjectName("project_logo")
        self.setSharedRenderer(renderer)


    def updatePosition(self):
        """
        Updates position to be located in the right bottom corner
        """
        logo_rect = self.boundingRect()
        width = self._main_window.uiGraphicsView.viewport().width()
        height = self._main_window.uiGraphicsView.viewport().height()
        rect = self._main_window.uiGraphicsView.mapToScene(QtCore.QRect(0, 0, width, height)).boundingRect()
        x = rect.x() + rect.width() - self.MARGIN - logo_rect.width()
        y = rect.y() + rect.height() - self.MARGIN - logo_rect.height()

        # update only when changes
        if [int(self.x()), int(self.y())] != [int(x), int(y)]:
            self.setX(x)
            self.setY(y)
            self.update()

    def hoverEnterEvent(self, event):
        """
        Handles all hover enter events for this item.

        :param event: QGraphicsSceneHoverEvent instance
        """

        if self._logo_url is not None:
            self.graphicsEffect().setEnabled(True)

    def hoverLeaveEvent(self, event):
        """
        Handles all hover leave events for this item.

        :param event: QGraphicsSceneHoverEvent instance
        """

        self.graphicsEffect().setEnabled(False)

    def mousePressEvent(self, event):
        url = QtCore.QUrl(self._logo_url)
        if not QtGui.QDesktopServices.openUrl(url):
            QtWidgets.QMessageBox.warning(self, 'Open Url', 'Could not open url')
