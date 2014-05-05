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
Base cloud controller class.

Base class for interacting with Cloud APIs to create and manage cloud
instances.

"""


class BaseCloudCtrl(object):

    """ Base class for interacting with a cloud provider API. """

    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def authenticate(self):
        raise NotImplementedError

    def create_instance(self, name, size, image, keypair):
        """ Create a new instance with the supplied attributes. """

        pass
        #self.

    def delete_instance(self, instance_id):
        """ Delete the instance with id of instance_id. Return True/False. """

        #class FakeNode(object):
        #
        #    def __init__(self):
        #        pass

        ## TODO: remove this temporary bit
        #self.instances[instance_id] = FakeNode()
        #setattr(self.instances[instance_id], 'id', instance_id)

        try:
            return self.driver.destroy_node(self.instances[instance_id])

        except (KeyError, Exception) as e:

            # libcloud raises generic 'Exception' with error in text
            if (type(e) is KeyError) or str(e) == \
                    "404 Not Found Instance could not be found":

                raise LookupError('Instance with id "%s" not found' %
                                 instance_id)

    def get_instance(self, instance_id):
        """ Return a Node object representing the requested instance. """

        return self.instances[instance_id]

    def list_instances(self):
        """ Return a dict of instances in the current region ('id' as key). """

        # save the list of instances to reduce API calls
        self.instances = self.driver.list_nodes()

        return {i.id: i for i in self.instances}

    def list_regions(self):
        raise NotImplementedError

    def terminate_instance(self, instance_id):
        raise NotImplementedError
