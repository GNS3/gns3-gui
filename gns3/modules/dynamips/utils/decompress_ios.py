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

import os
import mmap
import zipfile
import shutil
import tempfile


def isIOSCompressed(ios_image):
    """
    Checks either an IOS image is compressed or not.
    Returns True if compressed.

    :param ios_image: IOS image path

    :returns: boolean
    """

    fd = open(ios_image, "r+b")
    mapped_file = mmap.mmap(fd.fileno(), 0)

    # look for ZIP 'end of central directory' signature
    pos = mapped_file.rfind(b"\x50\x4b\x05\x06")

    # look for another ZIP 'end of central directory' signature
    # if we find one it means the IOS image itself contains zipped files
    multiple_zipped_files = mapped_file.find(b"\x50\x4b\x05\x06", 0, pos)

    # let's find the 'CISCO SYSTEMS' string between our last signature and the end of our file
    # so we can know the IOS image is compressed even if there are other ZIP signatures in our file
    cisco_string = mapped_file.find(b"\x43\x49\x53\x43\x4F\x20\x53\x59\x53\x54\x45\x4D\x53", pos + 4)

    mapped_file.close()
    fd.close()

    if pos > 0 and not (multiple_zipped_files > 0 and not cisco_string > 0):
        return True
    return False


def decompressIOS(ios_image, destination_file):
    """
    Decompress an IOS image.

    :param ios_image: IOS image path
    :param destination_file: destination path for the decompressed IOS image
    """

    # we don't touch the original image
    tmp_fd = tempfile.NamedTemporaryFile(delete=False)
    shutil.copyfile(ios_image, tmp_fd.name)
    data = tmp_fd.read()

    # look for ZIP 'end of central directory' signature
    pos = data.rfind(b"\x50\x4b\x05\x06")
    if pos > 0:
        # size of 'ZIP end of central directory record'
        tmp_fd.seek(pos + 22)
        # this make a clean zipped file
        tmp_fd.truncate()

    # decompress the IOS image
    is_zipfile = zipfile.is_zipfile(tmp_fd.name)
    if is_zipfile:
        zip_file = zipfile.ZipFile(tmp_fd.name, "r")
        for member in zip_file.namelist():
            source = zip_file.open(member)
            target = open(destination_file, "wb")
            shutil.copyfileobj(source, target)
            source.close()
            target.close()
        zip_file.close()
    try:
        tmp_fd.close()
        os.remove(tmp_fd.name)
    except OSError:
        pass

if __name__ == '__main__':

    # for testing
    image = "/home/grossmj/Documents/IOS/c3725-adventerprisek9-mz.124-15.T14.bin"
    extracted_image = "/tmp/c3725.image"
    print(isIOSCompressed(image))
    decompressIOS(image, extracted_image)
    print(isIOSCompressed(extracted_image))
