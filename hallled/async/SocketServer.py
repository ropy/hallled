'''
    Simple socket server using threads
'''

import socket
import sys
import hallled.async.SocketHandler as SocketHandler

HOST = '127.0.0.1'  # Symbolic name, meaning all available interfaces
PORT = 12345  # Arbitrary non-privileged port


class SocketServer:
    """
     Socket Server. Implemeted as a singleton.
    """
    class __SocketServer:
        def __init__(self, host, port):
            self.host = host
            self.port = port
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_handler = SocketHandler.ThreadedSocketHandler()
            self.sockets = dict()

        def __str__(self):
            return repr(self) + self.host + self.port

    instance = None

    def __init__(self, host=None, port=None):
        if not SocketServer.instance:
            if host is None:
                host = HOST
            if port is None:
                port = PORT
            SocketServer.instance = SocketServer.__SocketServer(host, port)
        # else:
        #
        #     SocketServer.instance.host = host
        #     SocketServer.instance.port = port

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def run(self):
        try:
            print('Socket created')

            # Bind socket to local host and port
            try:
                self.sock.bind((self.host, self.port))
            except socket.error as msg:
                print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
                sys.exit()

            print('Socket bind complete')

            # Start listening on socket
            self.sock.listen(10)
            print('Socket now listening')

            # now keep talking with the client

            while 1:
                # wait to accept a connection - handle communication within a thread
                conn, addr = self.sock.accept()
                print('Connected with ' + addr[0] + ':' + str(addr[1]))
                print("SocketServer: adding " + str(addr) + " to socket list")
                self.sockets[str(addr)] = str(conn)
                self.socket_handler.handle(conn, addr)
                self.socket_handler.run()

                #remove the address from the sockets dict+
                # print("SocketServer: deleting " + str(addr) + " from socket list")
                # del self.sockets[str(addr)]

        finally:
            print("closing socket in server")
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()

    def info(self):
        return self.sockets

    def write(self, message):
        if self.socket_handler is not None:
            print("writing message" + str(message))
            self.socket_handler.write(message)
        else:
            print("SocketServer socket_handler is none")


if __name__ == "__main__":
    # execute only if run as a script
    s = SocketServer(HOST, PORT)
    s.run()
