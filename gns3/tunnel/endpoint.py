import socket
import select
import socketserver
import threading
import logging

log = logging.getLogger(__name__)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True  # Kill the threads when server is closing


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   self.remote_address,
                                                   self.request.getpeername())
        except Exception as e:
            log.critical('Incoming request to %s failed: %s' % (
                self.remote_address,
                str(e)
            )
            )
            return

        if chan is None:
            log.critical('Incoming request to %s:%s was rejected by the SSH server.' %
                         (self.remote_address))
            return

        log.debug('Connected!  Tunnel open %r -> %r -> %r' % (self.request.getpeername(),
                                                              chan.getpeername(), self.remote_address))

        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        chan.close()
        self.request.close()
        log.debug('Tunnel closed from %r' % (peername,))


class Endpoint:

    def __init__(self, local_address, remote_address, transport):
        """
        Store local and remote tunnel address information in the format:
        (ip, port) format.
        """

        self.local_address = local_address
        self.remote_address = remote_address
        self.transport = transport
        self.thread = None
        self.server = None

    def get(self):
        return (self.local_address, self.remote_address)

    def log_msg(self, msg):
        if self.thread:
            thread_name = self.thread.name
        else:
            thread_name = "Creating ID"

        log.info("%s: local %s:%s for remote %s:%s - %s" % (
            thread_name,
            self.local_address[0],
            self.local_address[1],
            self.remote_address[0],
            self.remote_address[1],
            msg,
        ))

    def _enable(self, local_address, remote_address, ssh_transport):
        # https://github.com/paramiko/paramiko/blob/master/demos/forward.py
        # This is a little convoluted, but lets me configure things for the Handler
        # object.  (SocketServer doesn't give Handlers any way to access the outer
        # server normally.)
        class EndPointHandler(ThreadedTCPRequestHandler):
            remote_address = self.remote_address
            local_address = self.local_address
            ssh_transport = self.transport

        server = ThreadedTCPServer(self.local_address, EndPointHandler)

        # https://docs.python.org/3.4/library/socketserver.html
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        self.thread = server_thread
        self.server = server
        self.log_msg("Server thread running")

    def getId(self):
        return self.thread.name

    def enable(self):
        self.log_msg("Starting server thread")
        self._enable(self.local_address, self.remote_address, self.transport)

    def disable(self):
        if self.server:
            self.log_msg("Stopping server thread")
            self.server.shutdown()
        else:
            self.log_msg("No server thread running to stop")

    @staticmethod
    def find_unused_port(start_port, end_port, host="127.0.0.1", socket_type="TCP", ignore_ports=[]):
        """
        Finds an unused port in a range.

        :param start_port: first port in the range
        :param end_port: last port in the range
        :param host: host/address for bind()
        :param socket_type: TCP (default) or UDP
        :param ignore_ports: list of port to ignore within the range
        """

        if socket_type == "UDP":
            socket_type = socket.SOCK_DGRAM
        else:
            socket_type = socket.SOCK_STREAM

        last_exception = None
        for port in range(start_port, end_port + 1):
            if port in ignore_ports:
                continue
            try:
                for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket_type, 0, socket.AI_PASSIVE):
                    af, socktype, proto, _, sa = res
                    with socket.socket(af, socktype, proto) as s:
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        s.bind(sa)  # the port is available if bind is a success
                return port
            except OSError as e:
                last_exception = e
                if port + 1 == end_port:
                    break
                else:
                    continue

        raise Exception("Could not find a free port between {} and {} on host {}, last exception: {}".format(start_port,
                                                                                                             end_port,
                                                                                                             host,
                                                                                                             last_exception))
