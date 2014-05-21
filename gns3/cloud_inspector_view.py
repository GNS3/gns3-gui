# -*- coding: utf-8 -*-
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import QAbstractTableModel
from PyQt4.QtCore import QModelIndex
from PyQt4.Qt import Qt

# this widget was promoted on Creator, must use absolute imports
from gns3.ui.cloud_inspector_view_ui import Ui_CloudInspectorView

from libcloud.compute.drivers.dummy import DummyNodeDriver


def gen_fake_nodes(how_many):
    """
    Generate a number of fake nodes, temporary hack
    """
    driver = DummyNodeDriver(0)
    for i in range(how_many):
        yield driver.create_node()


class InstanceTableModel(QAbstractTableModel):
    """

    """
    def __init__(self, *args, **kwargs):
        super(InstanceTableModel, self).__init__(*args, **kwargs)
        self._header_data = ['Status', 'Instance', 'Size', 'Devices']
        self._instances = []

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._instances)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 4 if len(self._instances) else 0

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            instance = self._instances[index.row()]
            col = index.column()
            if col == 0:
                # status
                return 'running'
            elif col == 1:
                # name
                return instance.name
            elif col == 2:
                # size
                return instance.size.ram
            elif col == 3:
                # devices
                return 0
            return None

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return self._header_data[section]
            except IndexError:
                return 'fava'
        return super(InstanceTableModel, self).headerData(section, orientation, role)

    def addInstance(self, instance):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        if not len(self._instances):
            self.beginInsertColumns(QModelIndex(), 0, 3)
            self.endInsertColumns()
        self._instances.append(instance)
        self.endInsertRows()


class CloudInspectorView(QWidget, Ui_CloudInspectorView):
    """

    """
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)

        self._model = InstanceTableModel()
        self.uiInstancesTableView.setModel(self._model)
        self.uiInstancesTableView.verticalHeader().hide()

    def load(self):
        for i in gen_fake_nodes(5):
            self._model.addInstance(i)

