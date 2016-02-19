# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
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

import jsonschema
import json
import os

from gns3.utils.get_resource import get_resource

def getTopologyValidationErrors(topology):
    """
    Apply a JSON schema to a topology

    :param topology: A dict of the topology
    :returns: Return None if ok otherwise an error message
    """

    with open(get_resource(os.path.join("schemas", "topology.json"))) as f:
        schema = json.load(f)

    v = jsonschema.Draft4Validator(schema)
    errors = sorted(v.iter_errors(topology), key=lambda e: e.path)
    if len(errors) == 0:
        return None

    error_message = ""
    for error in errors:
        # Uncomment for more details
        # for suberror in sorted(error.context, key=lambda e: e.schema_path):
        #    print(list(suberror.schema_path), suberror.message, sep=", ")
        error_message += "{}\n".format(str(error))

    error_message += "Best error message: {}\n".format(jsonschema.exceptions.best_match(v.iter_errors(topology)).message)
    return error_message


if __name__ == "__main__":
    """
        You can test this code with:
        python gns3/topology_check.py PATH_TO_TOPOLOGY.gns3
    """

    import sys

    if len(sys.argv) < 2:
        print("You need to pass a .gns3 file as parameter")
        sys.exit(1)
    sys.argv.pop(0)
    for path in sys.argv:
        with open(path) as f:
            print(path)
            errors = getTopologyValidationErrors(json.load(f))
            if errors:
                print(errors)
                sys.exit(1)
