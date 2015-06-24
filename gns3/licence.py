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

import rsa
import sys
import os
import base64

PUB_KEY = b"""-----BEGIN RSA PUBLIC KEY-----
MIICCgKCAgEAiE4Zgzge3Cg6EUfct7vnzcmXkIvsy6g/QkfEeKSz3Cd+L7kxVZGE
weOXySrSSrRBoF1i2JhL2KkqZTY31972deviL+fv+TgE5RueyERFey3fw7+oN/RW
i8UIUvRqHjwocCuJq5yUiOv+AdGKG3TNeYXvx4Xvnrr4AJnJRThDfqd0nr8QAXRn
/Ifx4MKivL8RDyqHoVlHvHeyJmtaZIzsYthsK3FU2XED6d6xwbga3t2cb4+DfJa3
rBtWnoIXHiRdZZUtl34dGiiyxKL2yco+Dpd5pUvw6F7+n77SnSwN+F0ZzrrgUMHA
vBHBnF4WB6mjRFxbO+B/H1OxnXcjwxgYWLCbkrhQogqyfdkmacppWLOH9OyzGUkY
r7qITLCWSAHuIqXmQF4VAqCPYwEK7o6ndebFk1jaAAPGIw52AA1YOSXJ6jpKiO7f
5gXT3xRfv4kW1Fp6le0hp0Laz6VGbOv44vauxk516v5MI+CUL3u5TOmGWM53u1OG
qq6SfL+5Cu0/4L+SUaJ7nzN+PgWx6BEd0LRzEVQcmRPA4zHbhJ7ebBbYOul9RFyW
8D7yy7mUQZwVQDcuaB6l2pu0BfZppb+Uf81h0nRQIrHt7BRBiyaGojQIHsw8CrqP
3fsnHUvqtNLipC26FSTW4wlPIEktsWU8TABgjbuS45+zFTI141/J77ECAwEAAQ==
-----END RSA PUBLIC KEY-----"""

import logging
log = logging.getLogger(__name__)


def checkLicence():
    """
    Return true if the user as correctly installed the licence file
    """
    appname = "GNS3"

    filename = "licence.txt"

    if sys.platform.startswith("win"):
        # On windows, the user specific configuration file location is %APPDATA%/GNS3/gns3_gui.conf
        appdata = os.path.expandvars("%APPDATA%")
        licence_file = os.path.join(appdata, appname, filename)

    else:
        # On UNIX-like platforms, the user specific configuration file location is /etc/xdg/GNS3/gns3_gui.conf
        home = os.path.expanduser("~")
        licence_file = os.path.join(home, ".config", appname, filename)

    return check_licence_file(licence_file)


def check_licence_file(licence_file):
    if os.path.exists(licence_file):
        with open(licence_file) as f:
            email = f.readline().strip()
            key = f.readline().strip()
        pubkey = rsa.PublicKey.load_pkcs1(PUB_KEY)
        try:
            rsa.verify(email.encode("utf-8"), base64.b64decode(key), pubkey)
            log.info("Found a valid licence file. Thanks for your support")
            return True
        except rsa.pkcs1.VerificationError:
            log.error("Invalid licence file.")
            return False
    return False
