'''
    Simple gateway client using threads
'''

import socket
import time
import hallled.async.SocketHandler as SocketHandler
from hallled.network.PackageBuilder import PackageBuilder
import logging

log = logging.getLogger(__name__)


HOST = '192.168.2.95'  # Symbolic name, meaning all available interfaces
PORT = 12345  # Arbitrary non-privileged port


class GatewayClient:
    """
     Gateway Client. Implemented as a singleton.
    """
    class __GatewayClient:
        def __init__(self, host, port):
            log.debug("GWC instance: init")
            self.host = host
            self.port = port
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_handler = SocketHandler.ThreadedSocketHandler()
            self.sockets = dict()
            self.connected = False
            log.debug("GWC instance: init done")

        def __str__(self):
            return repr(self) + self.host + self.port

    instance = None

    def __init__(self, host=None, port=None):
        log.debug("GWC init")
        if not GatewayClient.instance:
            log.debug("GWC creating new instance")
            if host is None:
                host = HOST
            if port is None:
                port = PORT
            GatewayClient.instance = GatewayClient.__GatewayClient(host, port)
        else:
            log.debug("GWC instance already created")

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def connect(self):
        log.debug("connecting")
        if not self.connected:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.socket_handler.handle(self.sock)

            GatewayClient.instance.connected = True

    def reconnect(self):
        log.debug("reconnecting...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.socket_handler.handle(self.sock)
        self.socket_handler.run()


    def disconnect(self):
        log.debug("disconnecting")
        if self.connected:
            self.sock.close()
            GatewayClient.instance.connected = False

    def info(self):
        return self.sockets

    def write(self, message):
        log.debug("gateway client: socket still connected: %s", str(self.socket_handler.alive()))
        if not self.socket_handler.alive():
            GatewayClient.instance.connected = False
            self.reconnect()

        if self.socket_handler is not None:
            package = PackageBuilder.build_arduino_package(message)
            log.debug("writing message %s ", str(package))
            self.socket_handler.write(package)
            if self.socket_handler.has_error():
                log.debug("socket handler error: %s", self.socket_handler.get_latest_error())
                log.debug("retry connect and send")
                self.reconnect()
                self.socket_handler.write(package)
                if self.socket_handler.has_error():
                    log.debug("socket handler still has  error: %s", self.socket_handler.get_latest_error())

if __name__ == "__main__":
    # execute only if run as a script
    s = GatewayClient(HOST, PORT)
    s.connect()
    s.socket_handler.handle(s.sock)
    # s.socket_handler.run()
    bytes_to_write = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 104, 100, 255, 127, 1]
    s.write(bytes_to_write)
    while 1:
 
        time.sleep(10)
        s.write(bytes_to_write)
        received = s.socket_handler.read()
        if received is not None:
            print(received)
    s.disconnect()
