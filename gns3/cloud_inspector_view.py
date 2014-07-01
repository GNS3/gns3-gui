# -*- coding: utf-8 -*-
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QAction
from PyQt4.QtCore import QAbstractTableModel
from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import QThread
from PyQt4.Qt import Qt

from .settings import CLOUD_PROVIDERS
from .utils import import_from_string

# this widget was promoted on Creator, must use absolute imports
from gns3.ui.cloud_inspector_view_ui import Ui_CloudInspectorView

from libcloud.compute.types import NodeState

POLLING_TIMER = 5000  # in milliseconds


class InstanceTableModel(QAbstractTableModel):
    """
    A custom table model storing data of cloud instances
    """
    def __init__(self, *args, **kwargs):
        super(InstanceTableModel, self).__init__(*args, **kwargs)
        self._header_data = ['Instance', '', 'Size', 'Devices']  # status has an empty header label
        self._width = len(self._header_data)
        self._instances = []

    def _get_status_icon_path(self, state):
        """
        Return a string pointing to the graphic resource
        """
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
            if col == 1:
                # status
                return QIcon(self._get_status_icon_path(instance.state))

        elif role == Qt.DisplayRole:
            if col == 0:
                # name
                return instance.name
            elif col == 2:
                # size
                if instance.size:
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
                return None
        return super(InstanceTableModel, self).headerData(section, orientation, role)

    def addInstance(self, instance):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        if not len(self._instances):
            self.beginInsertColumns(QModelIndex(), 0, self._width-1)
            self.endInsertColumns()
        self._instances.append(instance)
        self.endInsertRows()

    def getInstance(self, index):
        """
        Retrieve the i-th instance if index is in range
        """
        try:
            return self._instances[index]
        except IndexError:
            return None

    def update_instance_status(self, instance):
        """
        Update model data and notify connected views
        """
        try:
            i = self._instances.index(instance)
            current = self._instances[i]
            current.state = instance.state
            first_index = self.createIndex(i, 0)
            last_index = self.createIndex(i, self.columnCount()-1)
            self.dataChanged.emit(first_index, last_index)
        except ValueError:
            pass


class ListInstancesThread(QThread):
    """
    Helper class to retrieve data from the provider in a separate thread,
    avoid freezing the gui
    """
    instancesReady = pyqtSignal(object)

    def __init__(self, parent, provider):
        super(QThread, self).__init__(parent)
        self._provider = provider

    def run(self):
        instances = self._provider.list_instances()
        self.instancesReady.emit(instances)


class CloudInspectorView(QWidget, Ui_CloudInspectorView):
    """
    Table view showing data coming from InstanceTableModel

    Signals:
        instanceSelected(int) Emitted when users click and select an instance on the inspector.
        Param int is the ID of the instance
    """
    instanceSelected = pyqtSignal(int)

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)

        self._provider = None
        self._model = InstanceTableModel()  # shortcut for self.uiInstancesTableView.model()
        self.uiInstancesTableView.setModel(self._model)
        self.uiInstancesTableView.verticalHeader().hide()
        self.uiInstancesTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.uiInstancesTableView.horizontalHeader().setStretchLastSection(True)
        # connections
        self.uiInstancesTableView.customContextMenuRequested.connect(self._contextMenu)
        self.uiInstancesTableView.selectionModel().currentRowChanged.connect(self._rowChanged)

        self._pollingTimer = QTimer(self)
        self._pollingTimer.timeout.connect(self._polling_slot)

    def load(self, cloud_settings):
        """
        Fill the model data layer with instances retrieved through libcloud
        """
        provider_id = cloud_settings['cloud_provider']
        username = cloud_settings['cloud_user_name']
        apikey = cloud_settings['cloud_api_key']
        region = cloud_settings['cloud_region']
        provider_controller_class = import_from_string(CLOUD_PROVIDERS[provider_id][1])
        self._provider = provider_controller_class(username, apikey)

        if not self._provider.authenticate():
            self._provider = None
            return

        if not region:
            region = self._provider.list_regions().values()[0]

        if self._provider.set_region(region):
            update_thread = ListInstancesThread(self, self._provider)
            update_thread.instancesReady.connect(self._populate_model)
            update_thread.start()
            self._pollingTimer.start(POLLING_TIMER)
        else:
            self._provider = None
            return

    def _contextMenu(self, pos):
        # create actions
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self._deleteSelectedInstance)
        # create context menu and add actions
        menu = QMenu(self.uiInstancesTableView)
        menu.addAction(delete_action)
        # show the menu
        menu.popup(self.uiInstancesTableView.viewport().mapToGlobal(pos))

    def _deleteSelectedInstance(self):
        """
        Delete the instance corresponding to the selected table row
        """
        sel = self.uiInstancesTableView.selectedIndexes()
        if len(sel) and self._provider is not None:
            index = sel[0].row()
            instance = self._model.getInstance(index)
            self._provider.delete_instance(instance)
            # FIXME remove this message
            print("delete {}".format(instance.name))

    def _rowChanged(self, current, previous):
        """
        This slot is invoked every time users change the current selected row on the
        inspector
        """
        if current.isValid():
            instance = self._model.getInstance(current.row())
            self.instanceSelected.emit(instance.id)

    def _polling_slot(self):
        """
        Sync model data with instances status
        """
        if self._provider is None:
            return

        update_thread = ListInstancesThread(self, self._provider)
        update_thread.instancesReady.connect(self._update_model)
        update_thread.start()

    def _update_model(self, instances):
        for i in instances:
            self._model.update_instance_status(i)

    def _populate_model(self, instances):
        for i in instances:
            self._model.addInstance(i)
        self.uiInstancesTableView.resizeColumnsToContents()
