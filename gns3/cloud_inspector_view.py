# -*- coding: utf-8 -*-
import ast
import logging
import os
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QInputDialog
from PyQt4.QtCore import QAbstractTableModel
from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import pyqtSignal
from PyQt4.Qt import Qt

from .cloud.utils import (ListInstancesThread, CreateInstanceThread, DeleteInstanceThread,
                          StartGNS3ServerThread, WSConnectThread)
from libcloud.compute.types import NodeState
from .topology import Topology

# this widget was promoted on Creator, must use absolute imports
from gns3.ui.cloud_inspector_view_ui import Ui_CloudInspectorView
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


class InstanceTableModel(QAbstractTableModel):
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

        if role == Qt.DecorationRole:
            if col == 1:
                # status
                return QIcon(self._get_status_icon_path(instance))

        elif role == Qt.DisplayRole:
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
            self.beginRemoveRows(QModelIndex(), index, index)
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
            last_index = self.createIndex(index, self.columnCount()-1)
            self.dataChanged.emit(first_index, last_index)
        else:
            self.addInstance(instance)

    def getInstanceById(self, instance_id):
        return self._instances.get(instance_id, None)


class CloudInspectorView(QWidget, Ui_CloudInspectorView):
    """
    Table view showing data coming from InstanceTableModel

    Signals:
        instanceSelected(int) Emitted when users click and select an instance on the inspector.
        Param int is the ID of the instance
    """
    instanceSelected = pyqtSignal(str)

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)

        self._provider = None
        self._settings = None
        self._project_instances_id = []
        self._main_window = None

        self._model = InstanceTableModel()  # shortcut for self.uiInstancesTableView.model()
        self.uiInstancesTableView.setModel(self._model)
        self.uiInstancesTableView.verticalHeader().hide()
        self.uiInstancesTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.uiInstancesTableView.horizontalHeader().setStretchLastSection(True)
        # connections
        self.uiInstancesTableView.customContextMenuRequested.connect(self._contextMenu)
        self.uiInstancesTableView.clicked.connect(self._rowChanged)
        self.uiCreateInstanceButton.clicked.connect(self._create_new_instance)

        self._pollingTimer = QTimer(self)
        self._pollingTimer.timeout.connect(self._polling_slot)

        # map flavor ids to combobox indexes
        self.flavor_index_id = []

        # TODO: Delete me
        self._running = {}

    def _get_flavor_index(self, flavor_id):
        try:
            return self.flavor_index_id.index(flavor_id)
        except ValueError:
            return -1

    def load(self, main_win, instances):
        """
        Fill the model data layer with instances retrieved through libcloud
        """
        self._main_window = main_win
        self._provider = main_win.cloudProvider
        self._settings = main_win.cloudSettings()
        log.info('CloudInspectorView.load')

        for i in instances:
            self._project_instances_id.append(i["id"])

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
            delete_thread = DeleteInstanceThread(self, self._provider, instance)
            delete_thread.instanceDeleted.connect(self._main_window.remove_instance_from_project)
            delete_thread.start()

            instance.name = 'Deleting...'
            self._model.updateInstanceFields(instance, ['name',])

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

    def _gns3server_started_slot(self, id, host_ip, start_response):
        """
        This slot is called when the StartGNS3ServerThread succesfully started
        the server.

        :param id: the id of the instance
        :param host_ip: the host ip of the instance
        :param start_response: the output of the server start script on the remote host
        """
        # instance state transition: GNS3SERVER_STARTING --> GNS3SERVER_STARTED
        instance = self._model.getInstanceById(id)
        instance.state = RunningInstanceState.GNS3SERVER_STARTED
        self._model.updateInstanceFields(instance, ['state'])

        data = ast.literal_eval(start_response)

        # TODO: have the server return the port it is running on
        port = 8000

        username = data['WEB_USERNAME']
        password = data['WEB_PASSWORD']

        ssl_cert = ''.join(data['SSL_CRT'])
        ca_filename = 'cloud_server_{}.crt'.format(host_ip)
        # TODO: Move this directory into projectSettings.
        ca_dir = os.path.join(self._main_window.projectSettings()["project_files_dir"], "keys")
        ca_file = os.path.join(ca_dir, ca_filename)
        try:
            os.makedirs(ca_dir)
        except FileExistsError:
            pass
        with open(ca_file, 'wb') as ca_fh:
            ca_fh.write(ssl_cert.encode('utf-8'))

        topology = Topology.instance()
        top_instance = topology.getInstance(id)
        top_instance.set_later_attributes(host_ip, port, ssl_cert, ca_file)
        ssh_pkey = top_instance.private_key

        log.debug('Cloud server gns3server started.')
        wss_thread = WSConnectThread(self, self._provider, id, host_ip, port, ca_file,
                                     username, password, ssh_pkey, id)
        wss_thread.established.connect(self._wss_connected_slot)
        wss_thread.start()

    def _wss_connected_slot(self, id):
        """
        This slot is called when the WSConnectThread successfully connected to
        the websocket on the remote host
        """
        # instance state transition: GNS3SERVER_STARTED --> WS_CONNECTED
        instance = self._model.getInstanceById(id)
        instance.state = RunningInstanceState.WS_CONNECTED
        self._model.updateInstanceFields(instance, ['state'])

    def _get_public_ip(self, ip_list):
        """
        Pick the ipv4 address from the list of ip addresses that the instance
        has.
        """
        for ip in ip_list:
            log.debug('Cloud server ip {}'.format(ip))
            # Don't use the ipv6 address
            if ':' not in ip:
                log.debug('Chose {} as public ip'.format(ip))
                return ip
        return None

    def _update_model(self, instances):
        if not instances:
            return

        # populate underlying model if this is the first call
        if self._model.rowCount() == 0 and len(instances) > 0:
            self._populate_model(instances)

        instance_manager = CloudInstances.instance()
        instance_manager.update_instances(instances)

        # filter instances to only those in the current project
        project_instances = [i for i in instances if i.id in self._project_instances_id]

        # cleanup removed instances
        real = set(i.id for i in project_instances)
        current = set(self._model.instanceIds)
        for i in current.difference(real):
            self._model.removeInstanceById(i)
        self.uiInstancesTableView.resizeColumnsToContents()

        for i in project_instances:
            # get the customized instance state from self._model
            model_instance = self._model.getInstanceById(i.id)

            # update model instance state if needed
            if i.state != RunningInstanceState.RUNNING:
                self._model.updateInstanceFields(i, ['state'])

            # start gns3server if needed
            if i.state == RunningInstanceState.RUNNING and (
                    model_instance.state >= RunningInstanceState.RUNNING):
                # instance state transition: RUNNING --> GNS3SERVER_STARTING
                model_instance.state = RunningInstanceState.GNS3SERVER_STARTING
                self._model.updateInstanceFields(model_instance, ['state'])

                # start GNS3 server and deadman switch
                public_ip = self._get_public_ip(i.public_ips)
                instance_manager.update_host_for_instance(i.id, public_ip)
                topology_instance = instance_manager.get_instance(i.id)
                ssh_thread = StartGNS3ServerThread(
                    self, public_ip, topology_instance.private_key, i.id,
                    self._provider.username, self._provider.api_key, self._provider.region,
                    1800)
                ssh_thread.gns3server_started.connect(self._gns3server_started_slot)
                ssh_thread.start()

    def _populate_model(self, instances):
        log.info('CloudInspectorView._populate_model')
        self._model.flavors = self._provider.list_flavors()
        # filter instances for current project
        project_instances = [i for i in instances if i.id in self._project_instances_id]
        for i in project_instances:
            self._model.addInstance(i)
        self.uiInstancesTableView.resizeColumnsToContents()

    def _create_new_instance(self):
        idx = self.uiCreateInstanceComboBox.currentIndex()
        flavor_id = self.flavor_index_id[idx]
        image_id = self._settings['default_image']

        name, ok = QInputDialog.getText(self,
                                        "New instance",
                                        "Choose a name for the instance and press Ok,\n"
                                        "then wait for the instance to appear in the inspector.")

        if ok:
            if not name.endswith("-gns3"):
                name += "-gns3"

            create_thread = CreateInstanceThread(self, self._provider, name, flavor_id, image_id)
            create_thread.instanceCreated.connect(self._main_window.add_instance_to_project)
            create_thread.instanceCreated.connect(CloudInstances.instance().add_instance)
            create_thread.start()
