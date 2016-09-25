from hallled.async.SocketServer import SocketServer

HOST = '127.0.0.1'  # Symbolic name, meaning all available interfaces
PORT = 12345  # Arbitrary non-privileged port

s = SocketServer(HOST, PORT)
s.run()