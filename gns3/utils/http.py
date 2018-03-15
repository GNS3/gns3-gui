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

import sys
import ssl
import http
import json
import base64
import urllib.request

import logging
log = logging.getLogger(__name__)


def getSynchronous(protocol, host, port, endpoint, timeout=2, user=None, password=None):
    """
    :returns: Tuple (Status code, json of anwser). Status 0 is a non HTTP error
    """
    try:
        url = "{protocol}://{host}:{port}/v2/{endpoint}".format(protocol=protocol, host=host, port=port, endpoint=endpoint)
        request = urllib.request.Request(url)

        if user is not None and len(user) > 0:
            log.debug("Synchronous get {} with user '{}'".format(url, user))
            base64string = base64.encodebytes('{}:{}'.format(user, password).encode()).replace(b'\n', b'')
            request.add_header("Authorization", "Basic {}".format(base64string.decode()))
        else:
            log.debug("Synchronous get {} (no authentication)".format(url))

        if sys.version_info >= (3, 5):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            response = urllib.request.urlopen(request, timeout=timeout, context=ctx)
        else:
            response = urllib.request.urlopen(request, timeout=timeout)

        content_type = response.getheader("CONTENT-TYPE")
        if response.status == 200:
            if content_type == "application/json":
                content = response.read()
                json_data = json.loads(content.decode("utf-8"))
                return response.status, json_data
        else:
            return response.status, None
    except http.client.InvalidURL as e:
        log.warning("Invalid local server url: {}".format(e))
        return 0, None
    except http.client.UnknownProtocol:
        log.warning("Unknown server running on {}:{}".format(host, port))
        return 0, None
    except urllib.error.URLError:
        # Connection refused. It's a normal behavior if server is not started
        return 0, None
    except urllib.error.HTTPError as e:
        log.debug("Error during get on {}:{}: {}".format(host, port, e))
        return e.code, None
    except (OSError, http.client.BadStatusLine, ValueError, SystemError) as e:
        log.debug("Error during get on {}:{}: {}".format(host, port, e))
    return 0, None
