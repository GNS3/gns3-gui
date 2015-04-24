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

"""
This script generate a licence key for an user.
You need the GNS 3 private key if you want to use
this key with the public GNS 3 distribution.
"""

import rsa
import argparse
import base64
from gns3.licence import check_licence_file

BITS = 4096


def generate():
    """Generate licence key pair"""
    print("Generate licence it can be slow")
    (pubkey, privkey) = rsa.newkeys(BITS)
    with open("keys/private.pem", "w+") as f:
        f.write(privkey.save_pkcs1())
    with open("keys/pub.pem", "w+") as f:
        f.write(pubkey.save_pkcs1())

# generate()


parser = argparse.ArgumentParser(description="Generate licences files")
parser.add_argument("--private", dest="private",
                    action="store",
                    required=True,
                    help="The private key")
parser.add_argument("--out", dest="out",
                    action="store",
                    required=True,
                    help="The output file")
parser.add_argument("--email", dest="email",
                    action="store",
                    required=True,
                    help="The user email")

args = parser.parse_args()

with open(args.private, "rb") as privatefile:
    keydata = privatefile.read()
    privkey = rsa.PrivateKey.load_pkcs1(keydata)

signature = rsa.sign(args.email.encode("utf-8"), privkey, "SHA-512")
with open(args.out, "wb+") as f:
    f.write(args.email.encode("utf-8"))
    f.write(b"\n")
    f.write(base64.b64encode(signature))
    f.write(b"\n")

print("Check licence: {}".format(check_licence_file(args.out)))
