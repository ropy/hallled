import threading
import queue
import socket
import time

current_milli_time = lambda: int(round(time.time() * 1000))

queueLock = threading.Lock()
receivingQueue = queue.LifoQueue(20)
sendingQueue = queue.Queue(10)
threads = []


class ThreadedSocketHandler:
    """
    Handle a connection/address pair from an accepted socket connection.
    """

    def __init__(self, conn, addr):
        """
        Initialize the handler
        :param conn: the accepted connection
        :param addr: the corresponding address
        """
        self.conn = conn
        self.addr = addr

    def run(self):
        """
        Run the sending and receiving thread.
        :return:
        """
        print(type(self.conn))

        sendingQueue.put(self.conn)
        sender = SocketSendingWorker(len(threads) + 1, "socket_sender", sendingQueue)
        sender.start()
        threads.append(sender)

        receivingQueue.put(self.conn)
        receivingQueue.put(sender)
        receiver = SocketReceivingWorker(len(threads) + 1, "socket_receiver", receivingQueue)
        receiver.start()
        threads.append(receiver)


class SocketReceivingWorker (threading.Thread):
    """
    Listen for data arriving on the given connection.
    """
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        self.sender = q.get()
        self.conn = q.get()
        self.connection_closed = False

    def run(self):
        print("Starting " + self.name + str(self.threadID))
        try:
            last_time = current_milli_time()
            print("time is " + str(last_time))
            while True:
                data = self.conn.recv(255)
                if data:
                    print(data)
                    b = bytearray(data)
                    print(b)

                    # put the time sent to us back together
                    l = 0
                    t = 0
                    i = 5
                    while i < len(b):
                        t |= (b[i] << l)
                        l += 8
                        i += 1
                    print(t)

                    response = [111, 107]
                    self.conn.send(bytes(response))
                    if data == "quit\n":
                        print("closing in threads while loop")
                        self.conn.shutdown(socket.SHUT_RDWR)
                        self.conn.close()
                        self.connection_closed = True
                        threads.remove(self)
                        break
                else:
                    print("no data, break")
                    break
        finally:
            if self.connection_closed is False:
                print("Closing connection in threads finally block")
                self.conn.shutdown(socket.SHUT_RDWR)
                self.conn.close()

            threads.remove(self)
            self.sender.stop()



        print ("Exiting " + self.name + str(self.threadID))


class SocketSendingWorker (threading.Thread):
    """
    Send data on the given connection.
    """
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        self.conn = q.get()
        self.connection_closed = False

    def run(self):
        print ("Starting " + self.name + str(self.threadID))
        try:
            last_time = current_milli_time()
            print("time is " + str(last_time))
            while True:
                if current_milli_time() - last_time > 1000:
                    print("Sending ok to socket." + str(current_milli_time()))
                    self.conn.send(bytes([111,111,107]))
                    last_time = current_milli_time()
        finally:
            threads.remove(self)

        print("Exiting " + self.name + str(self.threadID))

    def stop(self):
        threads.remove(self)
        print("stopping " + self.name + str(self.threadID))
        self._stop()