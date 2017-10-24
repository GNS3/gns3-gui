# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 GNS3 Technologies Inc.
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

import pathlib
import urllib.parse

from gns3.http_client import HTTPClient

import logging
log = logging.getLogger(__name__)


class ImageUploadManager(object):
    """
    Manager over the image upload. Encapsulates file uploads to computes or via controller.
    """

    def __init__(self, image, controller, compute_id, callback=None, direct_file_upload=False):
        self._image = image
        self._compute_id = compute_id
        self._callback = callback
        self._direct_file_upload = direct_file_upload
        self._controller = controller

    def upload(self):
        if self._direct_file_upload:
            # first obtain endpoint and know when target request
            self._controller.getEndpoint(
                self._getComputePath(), self._compute_id, self._on_load_endpoint_callback)
        else:
            self._file_upload_to_controller()

    def _getComputePath(self):
        return '/{emulator}/images/{filename}'.format(
            emulator=self._image.emulator, filename=self._image.filename)

    def _on_load_endpoint_callback(self, result, error=False, **kwargs):
        if error:
            if "message" in result:
                log.error("Error while getting endpoint: {}".format(result["message"]))
            return

        # we know where is the endpoint and we trying to post there a file
        endpoint = result['endpoint']
        self._file_upload_to_compute(endpoint)

    def _check_if_successful_callback(self, result, error=False, **kwargs):
        if error:
            connection_error = kwargs.get('connection_error', False)
            if connection_error:
                # there was an issue with connection, probably we don't have a direct access to compute
                # we need to fallback to uploading files via controller
                self._file_upload_to_controller()
            else:
                if "message" in result:
                    log.error("Error while direct file upload: {}".format(result["message"]))
            return
        self._callback(result, error, **kwargs)

    def _file_upload_to_compute(self, endpoint):
        parse_results = urllib.parse.urlparse(endpoint)
        network_manager = self._controller.getHttpClient().getNetworkManager()
        client = HTTPClient.fromUrl(endpoint, network_manager=network_manager)
        # We don't retry connection as in case of fail we try direct file upload
        client.setMaxRetryConnection(0)
        client.createHTTPQuery(
            'POST', parse_results.path, self._check_if_successful_callback, body=pathlib.Path(self._image.path),
            progressText="Uploading {}".format(self._image.filename), timeout=None, prefix="")

    def _file_upload_to_controller(self):
        self._controller.postCompute(
            self._getComputePath(), self._compute_id, self._callback, body=pathlib.Path(self._image.path),
            progressText="Uploading {}".format(self._image.filename), timeout=None)