# -*- coding: utf-8 -*-
from collections import namedtuple
import logging
import os
import json

from libcloud.compute.types import NodeState

from .qt import QtCore, QtGui
from .cloud.utils import (ListInstancesThread, DeleteInstanceThread)
from .topology import Topology
from .servers import Servers


# this widget was promoted on Creator, must use absolute imports
from gns3.ui.cloud_inspector_view_ui import Ui_CloudInspectorView
from gns3.cloud_builder import CloudBuilder
from gns3.cloud_instances import CloudInstances

log = logging.getLogger(__name__)

POLLING_TIMER = 10000  # in milliseconds


class RunningInstanceState(NodeState):

    """
    GNS3 states for running instances
    """
    GNS3SERVER_STARTING = -1
    GNS3SERVER_STARTED = -2
    WS_CONNECTED = -3


class InstanceTableModel(QtCore.QAbstractTableModel):

    """
    A custom table model storing data of cloud instances
    """

    def __init__(self, *args, **kwargs):
        super(InstanceTableModel, self).__init__(*args, **kwargs)
        self._header_data = ['Instance', '', 'Size', 'Devices']  # status has an empty header label
        self._width = len(self._header_data)
        self._instances = {}
        self._ids = []
        self.flavors = {}

    @property
    def instanceIds(self):
        return self._ids

    def clear(self):
        self._instances = {}
        self._ids = []
        self.reset()

    def _get_status_icon_path(self, instance):
        """
        Return a string pointing to the graphic resource
        """
        if instance.state == RunningInstanceState.WS_CONNECTED:
            return ':/icons/led_green.svg'
        elif instance.state in (RunningInstanceState.STOPPED,
                                RunningInstanceState.TERMINATED,
                                RunningInstanceState.UNKNOWN):
            return ':/icons/led_red.svg'
        else:
            return ':/icons/led_yellow.svg'

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._instances)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self._width if len(self._instances) else 0

    def data(self, index, role=None):
        instance = self._instances.get(self._ids[index.row()])
        col = index.column()

        if role == QtCore.Qt.DecorationRole:
            if col == 1:
                # status
                return QtGui.QIcon(self._get_status_icon_path(instance))

        elif role == QtCore.Qt.DisplayRole:
            if col == 0:
                # name
                return instance.name
            elif col == 2:
                # size
                try:
                    # for Rackspace instances, update flavor id with a verbose description
                    return self.flavors.get(instance.extra['flavorId'])
                except KeyError:
                    # fallback to libcloud size property
                    if instance.size:
                        return instance.size.ram
                    # giveup on showing size
                    return 'Unknown'
            elif col == 3:
                # devices
                count = 0
                topology = Topology.instance()
                for node in topology.nodes():
                    id = node._server.instance_id or 0
                    if instance.id == id:
                        count += 1
                return count
            return None

    def headerData(self, section, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            try:
                return self._header_data[section]
            except IndexError:
                return None
        return super(InstanceTableModel, self).headerData(section, orientation, role)

    def addInstance(self, instance):
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        if not len(self._instances):
            self.beginInsertColumns(QtCore.QModelIndex(), 0, self._width - 1)
            self.endInsertColumns()
        self._ids.append(instance.id)
        self._instances[instance.id] = instance
        self.endInsertRows()

    def getInstance(self, index):
        """
        Retrieve the i-th instance if index is in range
        """
        try:
            return self._instances.get(self._ids[index])
        except IndexError:
            return None

    def removeInstance(self, instance):
        self.removeInstanceById(instance.id)

    def removeInstanceById(self, instance_id):
        try:
            index = self._ids.index(instance_id)
            self.beginRemoveRows(QtCore.QModelIndex(), index, index)
            del self._instances[instance_id]
            del self._ids[index]
            self.endRemoveRows()
        except ValueError:
            pass

    def updateInstanceFields(self, instance, field_names):
        """
        Update model data and notify connected views
        """
        if instance.id in self._ids:
            index = self._ids.index(instance.id)
            current = self._instances[instance.id]
            for field in field_names:
                setattr(current, field, getattr(instance, field))
            first_index = self.createIndex(index, 0)
            last_index = self.createIndex(index, self.columnCount() - 1)
            self.dataChanged.emit(first_index, last_index)
        else:
            self.addInstance(instance)

    def getInstanceById(self, instance_id):
        return self._instances.get(instance_id, None)


class CloudInspectorView(QtGui.QWidget, Ui_CloudInspectorView):

    """
    Table view showing data coming from InstanceTableModel

    Signals:
        instanceSelected(int) Emitted when users click and select an instance on the inspector.
        Param int is the ID of the instance
    """
    instanceSelected = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)

        self._provider = None
        self._settings = None
        self._project_instances_id = []
        self._main_window = None

        self._model = InstanceTableModel()  # shortcut for self.uiInstancesTableView.model()
        self.uiInstancesTableView.setModel(self._model)
        self.uiInstancesTableView.verticalHeader().hide()
        self.uiInstancesTableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiInstancesTableView.horizontalHeader().setStretchLastSection(True)
        # connections
        self.uiInstancesTableView.customContextMenuRequested.connect(self._contextMenu)
        self.uiInstancesTableView.clicked.connect(self._rowChanged)
        self.uiCreateInstanceButton.clicked.connect(self._create_new_instance)

        self._pollingTimer = QtCore.QTimer(self)
        self._pollingTimer.timeout.connect(self._polling_slot)

        # map flavor ids to combobox indexes
        self.flavor_index_id = []

        # A dictionary of {image_id, CloudBuilder}
        self._builders = {}

    def _get_flavor_index(self, flavor_id):
        try:
            return self.flavor_index_id.index(flavor_id)
        except ValueError:
            return -1

    def load(self, main_win, instance_ids):
        """
        Fill the model data layer with instance info loaded from the topology file
        """
        self._main_window = main_win
        self._provider = main_win.cloudProvider
        self._settings = main_win.cloudSettings()
        log.info('CloudInspectorView.load')

        for instance_id in instance_ids:
            self._project_instances_id.append(instance_id)

        update_thread = ListInstancesThread(self, self._provider)
        update_thread.instancesReady.connect(self._update_model)
        update_thread.start()
        self._pollingTimer.start(POLLING_TIMER)
        # fill sizes comboboxes
        for id, name in self._provider.list_flavors().items():
            self.uiCreateInstanceComboBox.addItem(name)
            self.flavor_index_id.append(id)
        # select default flavor
        new_instance_flavor = self._settings["new_instance_flavor"]
        self.uiCreateInstanceComboBox.setCurrentIndex(self._get_flavor_index(new_instance_flavor))

    def addInstance(self, instance):
        """
        Add a new instance to the inspector
        """
        self._project_instances_id.append(instance.id)

    def clear(self):
        """
        Clear contents and stop polling timer
        """
        self._model.clear()
        self._pollingTimer.stop()
        self._project_instances_id = []

    def _contextMenu(self, pos):
        # create actions
        delete_action = QtGui.QAction("Delete", self)
        delete_action.triggered.connect(self._deleteSelectedInstance)
        # create context menu and add actions
        menu = QtGui.QMenu(self.uiInstancesTableView)
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

            # warn user this is destructive
            msg = "Do you want to remove the instance and any devices running on it?"
            proceed = QtGui.QMessageBox.question(self, 'Warning', msg,
                                                 QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if proceed == QtGui.QMessageBox.Yes:
                # disconnect and remove the server
                servers = Servers.instance()
                cs = servers.cloudServerById(instance.id)
                if cs is not None:
                    servers.removeCloudServer(cs)

                # remove instance from the the topology
                topology = Topology.instance()
                topology.removeInstance(instance.id)

                delete_thread = DeleteInstanceThread(self, self._provider, instance)
                delete_thread.instanceDeleted.connect(self._main_window.remove_instance_from_project)
                delete_thread.start()

                instance.name = 'Deleting...'
                self._model.updateInstanceFields(instance, ['name'])

    def _rowChanged(self, index):
        """
        This slot is invoked every time users change the current selected row on the
        inspector
        """
        selection = self.uiInstancesTableView.selectionModel().selection()
        if selection.isEmpty():
            return

        item = selection.indexes()[0]
        if item.isValid():
            instance = self._model.getInstance(item.row())
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

    def _instanceBuilt(self, id):
        """
        This slot is called when instance has finished building.
        """
        instance = self._model.getInstanceById(id)
        instance.state = RunningInstanceState.WS_CONNECTED
        self._model.updateInstanceFields(instance, ['state'])

        if self._main_window.loading_cloud_project:
            project = self._main_window.project()
            path = project.topologyPath()
            with open(path, "r") as f:
                json_topology = json.load(f)
                topology = Topology.instance()
                topology.load(json_topology)
            self._main_window.loading_cloud_project = False

    def _update_model(self, instances):
        if not instances:
            return

        # Filter instances to only those in the current project
        project_instances = [i for i in instances if i.id in self._project_instances_id]

        # populate underlying model if this is the first call
        if self._model.rowCount() == 0 and len(project_instances) > 0:
            self._populate_model(project_instances)
            self._rebuild_instances(project_instances)

        instance_manager = CloudInstances.instance()
        instance_manager.update_instances(instances)

        # Clean up removed instances
        real = set(i.id for i in project_instances)
        current = set(self._model.instanceIds)
        for i in current.difference(real):
            self._model.removeInstanceById(i)
        self.uiInstancesTableView.resizeColumnsToContents()

        # Update instance status
        for i in project_instances:
            # get the customized instance state from self._model
            model_instance = self._model.getInstanceById(i.id)

            # update model instance state if needed
            if i.state != RunningInstanceState.RUNNING:
                self._model.updateInstanceFields(i, ['state'])

    def _populate_model(self, instances):
        log.info('CloudInspectorView._populate_model')
        self._model.flavors = self._provider.list_flavors()
        # filter instances for current project
        for inst in instances:
            self._model.addInstance(inst)
        self.uiInstancesTableView.resizeColumnsToContents()

    def _create_new_instance(self):
        idx = self.uiCreateInstanceComboBox.currentIndex()
        flavor_id = self.flavor_index_id[idx]
        image_id = self._settings['default_image']

        name, ok = QtGui.QInputDialog.getText(self,
                                              "New instance",
                                              "Choose a name for the instance and press Ok,\n"
                                              "then wait for the instance to appear in the inspector.")

        if ok:
            self.createInstance(name, flavor_id, image_id)

    def createInstance(self, instance_name, flavor_id, image_id):
        if not instance_name.endswith("-gns3"):
            instance_name += "-gns3"
        # TODO: Add a keys_dir to projectSettings
        ca_dir = os.path.join(self._main_window.projectSettings()["project_files_dir"], "keys")

        builder = CloudBuilder(self, self._provider, ca_dir)
        builder.startAtCreate(instance_name, flavor_id, image_id)
        builder.instanceCreated.connect(self._main_window.add_instance_to_project)
        builder.instanceCreated.connect(CloudInstances.instance().add_instance)
        builder.instanceIdExists.connect(self._associateBuilderWithInstance)
        builder.instanceHasIP.connect(CloudInstances.instance().update_host_for_instance)
        builder.buildComplete.connect(self._instanceBuilt)
        builder.start()
        return builder

    def _associateBuilderWithInstance(self, builder, instance_id):
        self._builders[instance_id] = builder

    def _rebuild_instances(self, instances):
        # TODO: Add a keys_dir to projectSettings
        ca_dir = os.path.join(self._main_window.projectSettings()["project_files_dir"], "keys")

        for instance in instances:
            log.debug('CloudInspectorView._rebuild_instances {}'.format(instance.name))
            builder = CloudBuilder(self, self._provider, ca_dir)
            cloud_instance = CloudInstances.instance().get_instance(instance.id)
            public_key = cloud_instance.public_key
            private_key = cloud_instance.private_key
            # Fake a KeyPair object because we don't store it.
            keypair = namedtuple('KeyPair', ['private_key', 'public_key'])(private_key, public_key)
            builder.startAtSetup(instance, keypair)
            builder.instanceCreated.connect(self._main_window.add_instance_to_project)
            builder.instanceCreated.connect(CloudInstances.instance().add_instance)
            builder.instanceIdExists.connect(self._associateBuilderWithInstance)
            builder.instanceHasIP.connect(CloudInstances.instance().update_host_for_instance)
            builder.buildComplete.connect(self._instanceBuilt)
            builder.start()
            return builder
