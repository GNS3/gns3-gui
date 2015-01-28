import socket
import select
import socketserver
import threading
import logging

log = logging.getLogger(__name__)

debug = True

if logging.getLogger().getEffectiveLevel() < 20:
    enable_debug = True

if debug:
    enable_debug = True

if enable_debug:
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_level = logging.DEBUG
    log.setLevel(log_level)

    log_console = logging.StreamHandler()
    log_console.setFormatter(log_format)
    log_console.setLevel(log_level)
    log.addHandler(log_console)
    log.debug("DEBUG IS ENABLED")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   self.remote_address,
                                                   self.request.getpeername())
        except Exception as e:
            log.critical('Incoming request to %s:%s failed: %s' % (
                self.remote_address,
                repr(e)
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


class Endpoint(object):

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
