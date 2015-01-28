"""
This script can be used to ssh to a cloud server started by GNS3.  It copies
the ssh keys for a server to a temp file on disk and starts ssh using the
keys.

Right now it only connects to the first cloud server listed in the config
file.
"""

import getopt
import os
import sys

from PyQt4 import QtCore, QtGui


SCRIPT_NAME = os.path.basename(__file__)


def parse_cmd_line(argv):
    """
    Parse command line arguments

    argv: Passed in sys.argv
    """

    usage = """
    USAGE: %s [-l] [-s <server_num>]

    If no options are supplied a connection to server 1 will be opened.
    Options:

      -h, --help          Display this menu :)
      -l, --list          List instances that are tracked
      -s, --server-num    Connect to this server number (1-indexed)
    """ % (SCRIPT_NAME)

    short_args = "hls:"
    long_args = ("help", "list", "server-num=")
    try:
        opts, extra_opts = getopt.getopt(argv[1:], short_args, long_args)
    except getopt.GetoptError as e:
        print("Unrecognized command line option or missing required argument: %s" % (e))
        print(usage)
        sys.exit(2)

    cmd_line_option_list = {'action': 'ssh', 'server': '1'}

    for opt, val in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit(0)
        elif opt in ("-l", "--list"):
            cmd_line_option_list['action'] = 'list'
        elif opt in ("-s", "--server-num"):
            cmd_line_option_list['server'] = val

    return cmd_line_option_list


def setup():
    if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
        QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)

    app = QtGui.QApplication([])
    app.setOrganizationName("GNS3")
    app.setOrganizationDomain("gns3.net")
    app.setApplicationName("GNS3")

    if not os.path.isfile(QtCore.QSettings().fileName()):
        print('Config file {} not found! Aborting...'.format(QtCore.QSettings().fileName()))
        sys.exit(1)

    print('Config file: {}'.format(QtCore.QSettings().fileName()))


def read_cloud_settings():
    settings = QtCore.QSettings()
    settings.beginGroup("CloudInstances")

    instances = []
    # Load the instances
    size = settings.beginReadArray("cloud_instance")
    for index in range(0, size):
        settings.setArrayIndex(index)
        name = settings.value('name')
        host = settings.value('host')
        private_key = settings.value('private_key')
        public_key = settings.value('public_key')
        uid = settings.value('id')

        instances.append((name, host, private_key, public_key, uid))

    if len(instances) == 0:
        raise Exception("Could not find any servers")

    return instances


def main():
    options = parse_cmd_line(sys.argv)
    setup()
    instances = read_cloud_settings()

    if options['action'] == 'ssh':
        name, host, private_key, public_key, uid = instances[int(options['server']) - 1]
        print('Instance name: {}'.format(name))
        print('Host ip: {}'.format(host))

        public_key_path = '/tmp/id_rsa.pub'
        open(public_key_path, 'w').write(public_key)
        private_key_path = '/tmp/id_rsa'
        open(private_key_path, 'w').write(private_key)
        cmd = 'chmod 0600 {}'.format(private_key_path)
        os.system(cmd)
        print('Per-instance ssh keys written to {}'.format(private_key_path))

        cmd = 'ssh -i /tmp/id_rsa root@{}'.format(host)
        print(cmd)
        os.system(cmd)
    elif options['action'] == 'list':
        print('ID   Name   IP   UID')
        for idx, info in enumerate(instances):
            name, host, private_key, public_key, uid = info
            print('{:2d}   {}   {}   {}'.format(idx + 1, name, host, uid))

    return 0


if __name__ == "__main__":
    sys.exit(main())
