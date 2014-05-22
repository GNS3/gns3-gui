# -*- coding: utf-8 -*-
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import QAbstractTableModel
from PyQt4.QtCore import QModelIndex
from PyQt4.Qt import Qt

# this widget was promoted on Creator, must use absolute imports
from gns3.ui.cloud_inspector_view_ui import Ui_CloudInspectorView

from libcloud.compute.types import NodeState
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
        self._width = len(self._header_data)
        self._instances = []

    def _get_status_icon_path(self, state):
        if state == NodeState.RUNNING:
            return ':/icons/led_green.svg'
        elif state in (NodeState.REBOOTING, NodeState.PENDING, NodeState.UNKNOWN):
            return ':/icons/led_yellow.svg'
        else:
            return ':/icons/led_red.svg'

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._instances)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self._width if len(self._instances) else 0

    def data(self, index, role=None):
        instance = self._instances[index.row()]
        col = index.column()

        if role == Qt.DecorationRole:
            if col == 0:
                # status
                return QIcon(self._get_status_icon_path(instance.state))

        elif role == Qt.DisplayRole:
            if col == 1:
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
            self.beginInsertColumns(QModelIndex(), 0, self._width-1)
            self.endInsertColumns()
        self._instances.append(instance)
        self.endInsertRows()

    def update_instance_status(self, instance):
        try:
            i = self._instances.index(instance)
            current = self._instances[i]
            current.state = instance.state
            self.dataChanged.emit(self.createIndex(i, 0), self.createIndex(i, self._width-1))
        except ValueError:
            pass


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

