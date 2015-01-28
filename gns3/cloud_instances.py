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

"""
Keeps track of all cloud instances the app has started.
"""

from .qt import QtCore
from gns3.topology import TopologyInstance

import logging

log = logging.getLogger(__name__)


class CloudInstances(QtCore.QObject):

    """
    This class stores the instances that gns3 gui has started.  This can be different than the list
    of instances in the topology that can be changed when switching projects.  This list is not touched
    when switching projects and is stored in the .ini file.
    """

    def __init__(self, *args, **kwargs):
        super(CloudInstances, self).__init__(*args, **kwargs)
        self._instances = []

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of CloudInstances.

        :returns: instance of CloudInstances
        """

        if not hasattr(CloudInstances, "_instance"):
            CloudInstances._instance = CloudInstances()
        return CloudInstances._instance

    @property
    def instances(self):
        return self._instances

    def clear(self):
        self._instances.clear()

    def add(self, topology_instance):
        self._instances.append(topology_instance)

    def add_instance(self, instance, keypair):
        if instance is None:
            return
        existing = self.get_instance(instance.id)
        if existing is None:
            ti = TopologyInstance(instance.name, instance.id, instance.extra['flavorId'],
                                  instance.extra['imageId'], keypair.private_key, keypair.public_key)
            self._instances.append(ti)
            self.save()

    def update_instances(self, instances):
        """
        Compare with the existing list of instances to purge instances that no
        longer exist.
        """
        save_needed = False
        # Look for instances that have been deleted
        for stored in self._instances:
            found = False
            for dynamic in instances:
                if stored.id == dynamic.id:
                    found = True
                    break

            if not found:
                self._instances.remove(stored)
                save_needed = True

        if save_needed:
            self.save()

    def update_host_for_instance(self, host, instance_id):
        """
        Update the public IP for the instance.
        """
        for instance in self.instances:
            if instance.id == instance_id:
                if instance.host != host:
                    instance.host = host
                    self.save()

    def save(self):
        """
        Save the list of cloud instances to the config file
        """
        log.debug('Saving cloud instances')
        settings = QtCore.QSettings()
        settings.beginGroup("CloudInstances")
        settings.remove("")

        # Save the instances
        settings.beginWriteArray("cloud_instance", len(self._instances))
        index = 0
        for instance in self._instances:
            settings.setArrayIndex(index)
            for name in instance.fields():
                value = getattr(instance, name) if not None else ""
                log.debug('{}={}'.format(name, str(value)[0:60]))
                settings.setValue(name, value)
            index += 1
        settings.endArray()
        settings.endGroup()

    def load(self):
        """
        Load instance info from the config file to the topology
        """
        log.debug('Loading cloud instances')
        settings = QtCore.QSettings()
        settings.beginGroup("CloudInstances")

        # Load the instances
        size = settings.beginReadArray("cloud_instance")
        for index in range(0, size):
            settings.setArrayIndex(index)
            info = {}
            for name in TopologyInstance.fields():
                value = settings.value(name, "")
                log.debug('{}={}'.format(name, str(value)[0:60]))
                info[name] = value
            ti = TopologyInstance(**info)
            self._instances.append(ti)

    def get_instance(self, instance_id):
        """
        Retrieve a TopologyInstance objects if present
        """
        for i in self._instances:
            if i.id == instance_id:
                return i
        return None
