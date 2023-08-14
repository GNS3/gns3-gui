#!/usr/bin/env python
#
# Copyright (C) 2023 GNS3 Technologies Inc.
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
import sys
import shutil

import logging
log = logging.getLogger(__name__)


def macos_ubridge_setuid():

    # AuthorizationExecuteWithPrivileges() has been deprecated since macOS 10.7 but it still works
    # and much simpler than using SMJobBless() which requires a separate helper tool

    import ctypes
    import ctypes.util
    from ctypes import byref

    authorize_ubridge = shutil.which("authorize_ubridge", path=os.path.dirname(sys.executable))
    if authorize_ubridge is None:
        raise OSError("Could not find the authorize_ubridge executable")

    # https://developer.apple.com/documentation/security
    sec = ctypes.cdll.LoadLibrary(ctypes.util.find_library("Security"))

    try:
        sec.AuthorizationCreate
    except AttributeError:
        raise OSError("macOS security library does not support AuthorizationCreate")

    kAuthorizationFlagDefaults = 0
    auth = ctypes.c_void_p()
    r_auth = byref(auth)
    err = sec.AuthorizationCreate(None, None, kAuthorizationFlagDefaults, r_auth)
    if err:
        raise OSError("Could not create authorization: {}".format(err))

    exe = [authorize_ubridge]
    log.info("Executing '{}' with privileges".format(exe))
    args = (ctypes.c_char_p * len(exe))()
    for i, arg in enumerate(exe[1:]):
        args[i] = arg.encode('utf8')
    io = ctypes.c_void_p()
    err = sec.AuthorizationExecuteWithPrivileges(auth, exe[0].encode('utf8'), 0, args, byref(io))
    if err:
        raise OSError("Could not authorize uBridge: {}".format(err))
    else:
        log.info("Successfully authorized uBridge")
