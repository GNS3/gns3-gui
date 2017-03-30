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

import os
from .qt import QtCore, qpartial, QtWidgets, QtNetwork

from gns3.controller import Controller
from gns3.compute_manager import ComputeManager
from gns3.topology import Topology
from gns3.local_config import LocalConfig
from gns3.settings import GRAPHICS_VIEW_SETTINGS


import logging
log = logging.getLogger(__name__)


class Project(QtCore.QObject):

    """Current project"""

    # Called before project closing
    project_about_to_close_signal = QtCore.Signal()

    # Called when the project is closed on all servers
    project_closed_signal = QtCore.Signal()

    # Called when the creation of a project failed, the argument is the error message
    project_creation_error_signal = QtCore.Signal(str)

    project_updated_signal = QtCore.Signal()

    def __init__(self):

        self._id = None
        self._closed = True
        self._closing = False
        self._files_dir = None
        self._images_dir = None
        self._auto_start = False
        self._auto_open = False
        self._auto_close = False

        graphic_settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, GRAPHICS_VIEW_SETTINGS)
        self._scene_width = graphic_settings["scene_width"]
        self._scene_height = graphic_settings["scene_height"]

        self._name = "untitled"
        self._filename = None

        # Due to bug in Qt on some version we need a dedicated network manager
        self._notification_network_manager = QtNetwork.QNetworkAccessManager()
        self._notification_stream = None

        super().__init__()

    def name(self):
        """
        :returns: Project name (string)
        """

        return self._name

    def setSceneWidth(self, val):
        self._scene_width = val

    def sceneWidth(self):
        return self._scene_width

    def setSceneHeight(self, val):
        self._scene_height = val

    def sceneHeight(self):
        return self._scene_height

    def setAutoOpen(self, val):
        """
        Open the project with GNS3 server
        """
        self._auto_open = val

    def autoOpen(self):
        return self._auto_open

    def setAutoClose(self, val):
        """
        Close the project when last client is disconnected from the notification feed
        """
        self._auto_close = val

    def autoClose(self):
        return self._auto_close

    def setAutoStart(self, val):
        """
        Start the project when opened
        """
        self._auto_start = val

    def autoStart(self):
        return self._auto_start

    def setName(self, name):
        """
        Set project name

        :param name: Project name (string)
        """

        assert name is not None
        if len(name) > 0:
            self._name = name

    def closed(self):
        """
        :returns: True if project is closed
        """

        return self._closed

    def id(self):
        """
        Get project identifier
        """

        return self._id

    def setId(self, project_id):
        """
        Set project identifier
        """

        self._id = project_id

    def path(self):
        """
        Return the path of the .gns3
        """
        if self._files_dir:
            return os.path.join(self._files_dir, self._filename)
        return None

    def filesDir(self):
        """
        Project directory on the local server
        """

        return self._files_dir

    def setFilesDir(self, files_dir):

        self._files_dir = files_dir

    def filename(self):
        """
        Project filename
        """
        return self._filename

    def setFilename(self, name):
        """
        Set project filename
        """
        self._filename = name

    def start_all_nodes(self):
        """Start all nodes belonging to this project"""

        # Don't do anything if the project doesn't exist on the server
        if self._id is None:
            return

        Controller.instance().post("/projects/{project_id}/nodes/start".format(project_id=self._id), None, body={}, timeout=None)

    def duplicate(self, name=None, path=None, callback=None):
        """
        Duplicate a project
        """
        Controller.instance().post("/projects/{project_id}/duplicate".format(project_id=self._id), qpartial(self._duplicateCallback, callback), body={"name": name, "path": path}, timeout=None)

    def _duplicateCallback(self, callback, result, error=False, **kwargs):
        if error:
            if "message" in result:
                QtWidgets.QMessageBox.critical(None, "Duplicate project", "Error while duplicate: {}".format(result["message"]))
            return
        if callback:
            callback(result["project_id"])

    def stop_all_nodes(self):
        """Stop all nodes belonging to this project"""

        # Don't do anything if the project doesn't exist on the server
        if self._id is None:
            return

        Controller.instance().post("/projects/{project_id}/nodes/stop".format(project_id=self._id), None, body={}, timeout=None)

    def suspend_all_nodes(self):
        """Suspend all nodes belonging to this project"""

        # Don't do anything if the project doesn't exist on the server
        if self._id is None:
            return

        Controller.instance().post("/projects/{project_id}/nodes/suspend".format(project_id=self._id), None, body={}, timeout=None)

    def reload_all_nodes(self):
        """Reload all nodes belonging to this project"""

        # Don't do anything if the project doesn't exist on the server
        if self._id is None:
            return

        Controller.instance().post("/projects/{project_id}/nodes/reload".format(project_id=self._id), None, body={}, timeout=None)

    def get(self, path, callback, **kwargs):
        """
        HTTP GET on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery("GET", path, callback, **kwargs)

    def post(self, path, callback, body={}, **kwargs):
        """
        HTTP POST on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery("POST", path, callback, body=body, **kwargs)

    def put(self, path, callback, body={}, **kwargs):
        """
        HTTP PUT on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery("PUT", path, callback, body=body, **kwargs)

    def delete(self, path, callback, body={}, **kwargs):
        """
        HTTP DELETE on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery("DELETE", path, callback, body=body, **kwargs)

    def _projectHTTPQuery(self, method, path, callback, body={}, **kwargs):
        """
        HTTP query on the remote server

        :param method: HTTP Method type (string)
        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)
        :param params: Answer from the creation on server
        :param error: HTTP error

        Full arg list in createHTTPQuery
        """

        path = "/projects/{project_id}{path}".format(project_id=self._id, path=path)
        Controller.instance().createHTTPQuery(method, path, callback, body=body, **kwargs)

    def create(self):
        """
        Create the project on the remote server.
        """
        body = {
            "name": self._name,
            "path": self.filesDir()
        }
        Controller.instance().post("/projects", self._projectCreatedCallback, body=body)

    def update(self):
        """
        Update the project on remote server
        """
        body = {
            "name": self._name,
            "auto_open": self._auto_open,
            "auto_close": self._auto_close,
            "auto_start": self._auto_start,
            "scene_width": self._scene_width,
            "scene_height": self._scene_height
        }
        self.put("", self._projectUpdatedCallback, body=body)

    def _projectUpdatedCallback(self, result, error=False, **kwargs):
        if error:
            self.project_creation_error_signal.emit(result["message"])
            return
        self._parseResponse(result)
        self.project_updated_signal.emit()

    def _projectCreatedCallback(self, result, error=False, **kwargs):
        if error:
            self.project_creation_error_signal.emit(result["message"])
            return
        self._parseResponse(result)
        if self._closed:
            self._closed = False
            self._closing = False
            self._startListenNotifications()
        self.project_updated_signal.emit()

    def _parseResponse(self, result):
        """
        Parse response from API and update the object
        """
        self._id = result["project_id"]
        self._name = result["name"]
        self._filename = result.get("filename")
        self._files_dir = result.get("path")
        self._auto_start = result.get("auto_start", False)
        self._auto_open = result.get("auto_open", True)
        self._auto_close = result.get("auto_close", False)
        self._scene_width = result.get("scene_width", 2000)
        self._scene_height = result.get("scene_height", 1000)

    def load(self, path=None):
        if not path:
            path = self.path()
        if path:
            body = {"path": path}
            Controller.instance().post("/projects/load", self._projectOpenCallback, body=body, timeout=None)
        else:
            self.post("/open", self._projectOpenCallback, timeout=None)

    def _projectOpenCallback(self, result, error=False, **kwargs):
        if error:
            self.project_creation_error_signal.emit(result["message"])
            return

        self._parseResponse(result)

        if self._closed:
            self._closed = False
            self._closing = False
            self._startListenNotifications()
        self.project_updated_signal.emit()

        self.get("/nodes", self._listNodesCallback)

    def _listNodesCallback(self, result, error=False, **kwargs):
        if error:
            log.error("Error while listing project: {}".format(result["message"]))
            return
        topo = Topology.instance()
        for node in result:
            topo.createNode(node)
        self.get("/links", self._listLinksCallback)

    def _listLinksCallback(self, result, error=False, **kwargs):
        if error:
            log.error("Error while listing links: {}".format(result["message"]))
            return
        topo = Topology.instance()
        for link in result:
            topo.createLink(link)
        self.get("/drawings", self._listDrawingsCallback)

    def _listDrawingsCallback(self, result, error=False, **kwargs):
        if error:
            log.error("Error while listing drawings: {}".format(result["message"]))
            return
        topo = Topology.instance()
        for drawing in result:
            topo.createDrawing(drawing)

    def close(self, local_server_shutdown=False):
        """Close project"""

        if self._closed or self._closing:
            return
        self._closing = True
        if self._id:
            self.project_about_to_close_signal.emit()
            Controller.instance().post("/projects/{project_id}/close".format(project_id=self._id), self._projectClosedCallback, body={}, progressText="Close the project")
        else:
            # The project is not initialized when we close it
            self._closed = True
            self.project_about_to_close_signal.emit()
            self.project_closed_signal.emit()

    def destroy(self):
        """
        Delete the project from all servers
        """
        self.project_about_to_close_signal.emit()
        Controller.instance().delete("/projects/{project_id}".format(project_id=self._id), self._projectClosedCallback, body={}, progressText="Delete the project")

    def _projectClosedCallback(self, result, error=False, server=None, **kwargs):

        # Status 404 could be when someone else already closed the project
        if error and "status" in result and result["status"] != 404:
            log.error("Error while closing project {}: {}".format(self._id, result["message"]))
        else:
            self.stopListenNotifications()
            log.info("Project {} closed".format(self._id))

        self._closed = True
        self.project_closed_signal.emit()
        Topology.instance().setProject(None)

    def stopListenNotifications(self):
        if self._notification_stream:
            log.debug("Stop listening for notifications from project %s", self._id)
            stream = self._notification_stream
            self._notification_stream = None
            stream.abort()

    def _startListenNotifications(self):
        if not Controller.instance().connected():
            return
        path = "/projects/{project_id}/notifications".format(project_id=self._id)
        self._notification_stream = Controller.instance().createHTTPQuery("GET", path, self._endListenNotificationCallback,
                                                                          downloadProgressCallback=self._event_received,
                                                                          networkManager=self._notification_network_manager,
                                                                          timeout=None,
                                                                          showProgress=False,
                                                                          ignoreErrors=True)

    def _endListenNotificationCallback(self, result, error=False, **kwargs):
        """
        If notification stream disconnect we reconnect to it
        """
        if self._notification_stream:
            self._notification_stream = None
            self._startListenNotifications()

    def _event_received(self, result, server=None, **kwargs):

        log.debug("Event received: %s", result)
        if result["action"] == "node.created":
            node = Topology.instance().getNodeFromUuid(result["event"]["node_id"])
            if node is None:
                Topology.instance().createNode(result["event"])
        elif result["action"] == "node.updated":
            node = Topology.instance().getNodeFromUuid(result["event"]["node_id"])
            if node is not None:
                node.updateNodeCallback(result["event"])
        elif result["action"] == "node.deleted":
            node = Topology.instance().getNodeFromUuid(result["event"]["node_id"])
            if node is not None:
                node.delete(skip_controller=True)
        elif result["action"] == "link.created":
            link = Topology.instance().getLinkFromUuid(result["event"]["link_id"])
            if link is None:
                Topology.instance().createLink(result["event"])
        elif result["action"] == "link.updated":
            link = Topology.instance().getLinkFromUuid(result["event"]["link_id"])
            if link is not None:
                link.updateLinkCallback(result["event"])
        elif result["action"] == "link.deleted":
            link = Topology.instance().getLinkFromUuid(result["event"]["link_id"])
            if link is not None:
                link.deleteLink(skip_controller=True)
        elif result["action"] == "drawing.created":
            drawing = Topology.instance().getDrawingFromUuid(result["event"]["drawing_id"])
            if drawing is None:
                Topology.instance().createDrawing(result["event"])
        elif result["action"] == "drawing.updated":
            drawing = Topology.instance().getDrawingFromUuid(result["event"]["drawing_id"])
            if drawing is not None:
                drawing.updateDrawingCallback(result["event"])
        elif result["action"] == "drawing.deleted":
            drawing = Topology.instance().getDrawingFromUuid(result["event"]["drawing_id"])
            if drawing is not None:
                drawing.delete(skip_controller=True)
        elif result["action"] == "project.closed":
            Topology.instance().setProject(None)
        elif result["action"] == "project.updated":
            self._projectUpdatedCallback(result["event"])
        elif result["action"] == "snapshot.restored":
            Topology.instance().createLoadProject({"project_id": result["event"]["project_id"]})
        elif result["action"] == "log.error":
            log.error(result["event"]["message"])
        elif result["action"] == "log.warning":
            log.warning(result["event"]["message"])
        elif result["action"] == "log.info":
            log.info(result["event"]["message"], extra={"show": True})
        elif result["action"] == "compute.created" or result["action"] == "compute.updated":
            cm = ComputeManager.instance()
            cm.computeDataReceivedCallback(result["event"])
        elif result["action"] == "settings.updated":
            LocalConfig.instance().refreshConfigFromController()
        elif result["action"] == "ping":
            pass
