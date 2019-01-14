#!/usr/bin/env python
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

import copy

from .qt import QtCore
from .controller import Controller
from .template import Template
from .utils.server_select import server_select

import logging
log = logging.getLogger(__name__)


class TemplateManager(QtCore.QObject):
    """
    Manager for templates.
    """

    templates_changed_signal = QtCore.Signal()
    created_signal = QtCore.Signal(str)
    updated_signal = QtCore.Signal(str)
    deleted_signal = QtCore.Signal(str)

    def __init__(self):

        super().__init__()
        self._templates = {}
        self._controller = Controller.instance()
        self._controller.connected_signal.connect(self.refresh)
        self._controller.disconnected_signal.connect(self._controllerDisconnectedSlot)

    def refresh(self, update=False):
        """
        Gets the templates from the controller.
        """

        if self._controller.connected():
            self._controller.get("/templates", self._listTemplatesCallback)

    def _controllerDisconnectedSlot(self):
        """
        Called when the controller has been disconnected.
        """

        self._templates = {}
        self.templates_changed_signal.emit()

    def createTemplate(self, template, callback=None):
        """
        Creates a template on the controller.

        :param template: template object.
        :param callback: callback to receive response from the controller.
        """

        log.debug("Create template '{}' (ID={})".format(template.name(), template.id()))
        self._controller.post("/templates", callback, body=template.__json__())

    def deleteTemplate(self, template_id):
        """
        Deletes a template on the controller.

        :param template_id: template identifier
        """

        if template_id in self._templates and not self._templates[template_id].builtin():
            template = self._templates[template_id]
            log.debug("Delete template '{}' (ID={})".format(template.name(), template_id))
            self._controller.delete("/templates/{template_id}".format(template_id=template_id), None)

    def deleteTemplateCallback(self, result, error=False, **kwargs):
        """
        Callback to delete a template.
        """

        if error is True:
            log.warning("Error while deleting template: {}".format(result.get("message", "unknown")))

        template_id = result["template_id"]
        if template_id in self._templates and not self._templates[template_id].builtin():
            del self._templates[template_id]
            self.deleted_signal.emit(template_id)
            self.templates_changed_signal.emit()

    def updateTemplate(self, template):
        """
        Updates a template on the controller.

        :param template: template object.
        """

        log.debug("Update template '{}' (ID={})".format(template.name(), template.id()))
        self._controller.put("/templates/{template_id}".format(template_id=template.id()), None, body=template.__json__())

    def updateList(self, templates):
        """
        Sync an array of templates with the controller.
        """

        for template_id in copy.copy(self._templates):
            # Delete missing templates
            if template_id not in [template.id() for template in templates]:
                self.deleteTemplate(template_id)
            else:
                # Update the changed templates
                for template in templates:
                    if template.id() == template_id and template != self._templates[template_id]:
                        self.updateTemplate(template)

        # Create the new templates
        for template in templates:
            if template.id() not in self._templates:
                self.createTemplate(template)

    def templateDataReceivedCallback(self, result, error=False, **kwargs):
        """
        Callback to add or update a template
        """

        if error is True:
            log.error("Error while adding/updating template: {}".format(result.get("message", "unknown")))
            return

        template_id = result["template_id"]
        if template_id not in self._templates:
            self._templates[template_id] = Template(result)
            self.created_signal.emit(template_id)
        else:
            template = self._templates[template_id]
            template.setSettings(result)
            self.updated_signal.emit(template_id)

        self.templates_changed_signal.emit()

    def templates(self):
        """
        Returns the templates

        :returns: array of templates
        """

        return self._templates

    def getTemplate(self, template_id):
        """
        Look for an appliance by template ID.

        :param template_id: template identifier
        :returns: template or None
        """

        try:
            return self._templates[template_id]
        except KeyError:
            return None

    def _listTemplatesCallback(self, result, error=False, **kwargs):
        """
        Callback to get the templates.
        """

        if error is True:
            log.error("Error while getting templates list: {}".format(result.get("message", "unknown")))
            return

        for template in result:
            template_id = template["template_id"]
            if template_id not in self._templates:
                self._templates[template_id] = Template(template)
                self.created_signal.emit(template_id)
        self.templates_changed_signal.emit()

    def createNodeFromTemplateId(self, project, template_id, x, y):
        """
        Creates a new node from a template.
        """

        for template in self._templates.values():
            if template.id() == template_id:
                break

        if not self._controller.connected():
            log.error("Cannot create node: not connected to any controller server")
            return

        if not project or not project.id():
            log.error("Cannot create node: please create a project first!")
            return

        params = {"x": int(x), "y": int(y)}
        if template.compute_id() is None:
            from .main_window import MainWindow
            server = server_select(MainWindow.instance(), node_type=template.template_type())
            if server is None:
                return False
            params["compute_id"] = server.id()

        self._controller.post("/projects/{project_id}/templates/{template_id}".format(project_id=project.id(), template_id=template_id),
                              self._createNodeFromTemplateCallback,
                              params,
                              timeout=None)
        return True

    def _createNodeFromTemplateCallback(self, result, error=False, **kwargs):
        """
        Callback to create node from template (for errors only).
        """

        if error and "message" in result:
            log.error("Error while creating node from template: {}".format(result["message"]))
            return

    def is_name_available(self, name):
        """
        :param name: Template name
        :returns: True if name is not already used
        """

        for template in self._templates.values():
            if template.name() == name:
                return False
        return True

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of TemplateManager.
        :returns: instance of TemplateManager
        """

        if not hasattr(TemplateManager, '_instance') or TemplateManager._instance is None:
            TemplateManager._instance = TemplateManager()
        return TemplateManager._instance
