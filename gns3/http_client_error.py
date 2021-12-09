#!/usr/bin/env python
#
# Copyright (C) 2021 GNS3 Technologies Inc.
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


class HttpClientError(Exception):
    def __init__(self, message: str):
        super().__init__()
        self._message = message

    def __repr__(self):
        return self._message

    def __str__(self):
        return self._message


class HttpClientNotFoundError(HttpClientError):
    def __init__(self, message: str):
        super().__init__(message)


class HttpClientCancelledRequestError(HttpClientError):
    def __init__(self, message: str):
        super().__init__(message)


class HttpClientBadRequestError(HttpClientError):
    def __init__(self, message: str):
        super().__init__(message)


class HttpClientUnauthorizedError(HttpClientError):
    def __init__(self, message: str):
        super().__init__(message)


class HttpClientForbiddenError(HttpClientError):
    def __init__(self, message: str):
        super().__init__(message)


class HttpClientTimeoutError(HttpClientError):
    def __init__(self, message: str):
        super().__init__(message)
