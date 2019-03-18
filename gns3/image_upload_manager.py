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

import os
import pathlib
import urllib.parse

from gns3.http_client import HTTPClient

import logging
log = logging.getLogger(__name__)


class ImageUploadManager(object):
    """
    Manager over the image upload. Encapsulates file uploads to computes or via controller.
    """

    def __init__(self, image, controller, compute_id, callback=None, directFileUpload=False):
        self._image = image
        self._compute_id = compute_id
        self._callback = callback
        self._directFileUpload = directFileUpload
        self._controller = controller

    def upload(self):
        if not os.path.exists(self._image.path):
            log.error("Image '{}' could not be found".format(self._image.path))
            return
        if self._directFileUpload:
            # first obtain endpoint and know when target request
            self._controller.getEndpoint(self._getComputePath(), self._compute_id, self._onLoadEndpointCallback, showProgress=False)
        else:
            self._fileUploadToController()

    def _getComputePath(self):
        return '/{emulator}/images/{filename}'.format(emulator=self._image.emulator, filename=self._image.filename)

    def _onLoadEndpointCallback(self, result, error=False, **kwargs):
        if error:
            if "message" in result:
                log.error("Error while getting endpoint: {}".format(result["message"]))
            return

        # we know where is the endpoint and we trying to post there a file
        endpoint = result['endpoint']
        self._fileUploadToCompute(endpoint)

    def _checkIfSuccessfulCallback(self, result, error=False, **kwargs):
        if error:
            connection_error = kwargs.get('connection_error', False)
            if connection_error:
                log.debug("During direct file upload compute is not visible. Fallback to upload via controller.")
                # there was an issue with connection, probably we don't have a direct access to compute
                # we need to fallback to uploading files via controller
                self._fileUploadToController()
            else:
                if "message" in result:
                    log.error("Error while direct file upload: {}".format(result["message"]))
            return
        self._callback(result, error, **kwargs)

    def _fileUploadToCompute(self, endpoint):
        log.debug("Uploading image '{}' to compute".format(self._image.path))
        parse_results = urllib.parse.urlparse(endpoint)
        network_manager = self._controller.getHttpClient().getNetworkManager()
        client = HTTPClient.fromUrl(endpoint, network_manager=network_manager)
        # We don't retry connection as in case of fail we try direct file upload
        client.setMaxRetryConnection(0)
        client.createHTTPQuery('POST', parse_results.path, self._checkIfSuccessfulCallback, body=pathlib.Path(self._image.path),
                               context={"image_path": self._image.path}, progressText="Uploading {}".format(self._image.filename), timeout=None, prefix="")

    def _fileUploadToController(self):
        log.debug("Uploading image '{}' to controller".format(self._image.path))
        self._controller.postCompute(self._getComputePath(), self._compute_id, self._callback, body=pathlib.Path(self._image.path),
                                     context={"image_path": self._image.path}, progressText="Uploading {}".format(self._image.filename), timeout=None)
