import os
import sys
import time
from optparse import OptionParser
import getpass

import tunnel

HELP = """\
Set up a forward tunnel across an SSH server, using paramiko. A local port
(given with -p) is forwarded across an SSH session to an address:port from
the SSH server. This is similar to the openssh -L option.
"""

SSH_PORT = 22


def get_host_port(spec, default_port):
    "parse 'hostname:22' into a host and port, with the port optional"
    args = (spec.split(':', 1) + [default_port])[:2]
    args[1] = int(args[1])
    return args[0], args[1]


def parse_options():
    global g_verbose

    parser = OptionParser(usage='usage: %prog [options] <ssh-server>[:<server-port>]',
                          version='%prog 1.0', description=HELP)
    parser.add_option('-u', '--user', action='store', type='string', dest='user',
                      default=getpass.getuser(),
                      help='username for SSH authentication (default: %s)' % getpass.getuser())
    parser.add_option('-K', '--key', action='store', type='string', dest='keyfile',
                      default=None,
                      help='private key file to use for SSH authentication')
    parser.add_option('-r', '--remote', action='store', type='string', dest='remote', default=None, metavar='host:port',
                      help='remote host and port to forward to')
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Incorrect number of arguments.')
    if options.remote is None:
        parser.error('Remote address required (-r).')

    server_host, server_port = get_host_port(args[0], SSH_PORT)
    remote_host, remote_port = get_host_port(options.remote, SSH_PORT)
    return options, (server_host, server_port), (remote_host, remote_port)


def main():
    options, server, remote = parse_options()

    if options.keyfile:
        my_key = open(options.keyfile, 'r')

    t = tunnel.Tunnel(server[0], server[1], username=options.user, client_key=my_key)

    print("Adding defaults ...")
    t1 = t.add_endpoint('127.0.0.1', 25)
    t2 = t.add_endpoint('127.0.0.1', 80)

    print("Adding command line destination")
    t3 = t.add_endpoint(remote[0], remote[1])

    print("Removing defaults ...")
    t.remove_endpoint(t1)
    t.remove_endpoint(t2)

    t.disconnect()

if __name__ == '__main__':
    main()
