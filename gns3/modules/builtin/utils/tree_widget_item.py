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

from gns3.qt import QtWidgets


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):

    """
    QTreeWidgetItem reimplementation to allow numeric sort.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

    def __lt__(self, other_item):

        column = self.treeWidget().sortColumn()
        try:
            return int(self.text(column)) < int(other_item.text(column))
        except ValueError:
            return self.text(column).lower() < other_item.text(column).lower()
