import threading
import queue
from time import sleep
from time import time
import logging

log = logging.getLogger(__name__)

current_milli_time = lambda: int(round(time() * 1000))

queueLock = threading.Lock()
receivingQueue = queue.LifoQueue(20)
sendingQueue = queue.Queue(10)
errorQueue = queue.Queue(10)
threads = []


class ThreadedSocketHandler:
    """
    Handle a connection/address pair from an accepted socket connection.
    """

    def __init__(self):
        log.debug("ThreadedSocketHandler: init")
        self.sock = None
        self.sender = None
        self.sender_stop = None
        self.receiver = None
        self.receiver_stop = None
        log.debug("ThreadedSocketHandler: init done")

    def handle(self, sock):
        """

        :param sock:
        :return:
        """
        log.debug("handling")
        log.debug(type(sock))
        self.sock = sock
        self.sender_stop = threading.Event()
        self.receiver_stop = threading.Event()
        self.sender = SocketSendingWorker(len(threads) + 1, "socket_sender", self.sock, self.sender_stop, self.receiver_stop)
        self.receiver = SocketReceivingWorker(len(threads) + 1, "socket_receiver", self.sock, self.receiver_stop, self.sender_stop)
        log.debug("handling setup done")

    def run(self):
        """
        Run the sending and receiving thread.
        :return:
        """
        log.debug("run")
        log.debug(type(self.sock))

        self.sender.start()
        threads.append(self.sender)

        self.receiver.start()
        threads.append(self.receiver)

        log.debug("ThreadedSocketHandler thread list: " + str(threads))

    def stop(self):
        self.sender.stop()
        self.receiver.stop()
        self.sock.close()

    def alive(self):
        if not threads:
            return False
        else:
            return True

    @staticmethod
    def info(self):
        """

        :return: array of currently running threads
        """
        return threads

    @staticmethod
    def write(message):
        log.debug("putting message to sending queue")
        sendingQueue.put(message)

    @staticmethod
    def read():
        if not receivingQueue.empty():
            item = receivingQueue.get()
            receivingQueue.task_done()
            return item

    @staticmethod
    def has_error():
        if not errorQueue.empty():
            return True

        return False

    @staticmethod
    def get_latest_error():
        if not errorQueue.empty():
            try:
                err = errorQueue.get_nowait()
                errorQueue.task_done()
                return err
            except queue.Empty:
                return None


class SocketReceivingWorker (threading.Thread):
    """
    Listen for data arriving on the given connection.
    """
    def __init__(self, threadID, name, socket, self_stop_event, other_stop_event):
        log.debug("SocketReceivingWorker init")
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.sock = socket
        self.connection_closed = False
        self.self_stop_event = self_stop_event
        self.other_stop_event = other_stop_event
        log.debug("init finished")

    def run(self):
        try:
            in_message = receivingQueue.get_nowait()
        except queue.Empty:
            in_message = None

        if in_message == "stop":
            self.stop()

        if self.sock is None:
            log.debug("no socket, can't start SocketReceivingWorker")
        else:
            log.debug("Starting " + self.name + str(self.threadID))
            try:
                last_time = current_milli_time()
                log.debug("time is " + str(last_time))
                while not self.self_stop_event.isSet():
                    data = self.sock.recv(255)
                    # print("SocketReceivingWorker: got data: '" + str(data) + "'")
                    if data:
                        # print(data)
                        b = bytearray(data)
                        log.debug(b)
                        log.debug(len(b))
                        # put the time sent to us back together
                        # l = 0
                        # t = 0
                        # i = 6
                        #
                        # if i < len(b):
                        #     log.debug(i)
                        #     while b[i] is not 172:
                        #         t |= (b[i] << l)
                        #         l += 8
                        #         i += 1
                        #         if i > len(b):
                        #             break
                        #     print(t)

                        # put the received item to the queue
                        receivingQueue.put(b)

                        #response = [111, 107]
                        #self.conn.send(bytes(response))
                        if data == "quit\n":
                            log.debug("closing connection in threads while loop")
                            # self.sock.shutdown(socket.SHUT_RDWR)
                            self.sock.close()
                            self.connection_closed = True
                            threads.remove(self)
                            break
                    else:
                        log.debug("no data, break")
                        # continue
                        break
            finally:
                if self.connection_closed is False:
                    log.debug("Closing connection in SocketReceivingWorker finally block")
                    # self.conn.shutdown(socket.SHUT_RDWR)
                    self.sock.close()
                    self.connection_closed = True

                threads.remove(self)

        log.debug("Exiting " + self.name + str(self.threadID))

    def stop(self):
        log.debug("stopping %s (id %s)", self.name, str(self.threadID))
        self.self_stop_event.set()
        log.debug("stopping other")
        self.other_stop_event.set()
        if not self.connection_closed:
            self.sock.close()
            self.connection_closed = True
        try:
            threads.remove(self)
        except ValueError:
            pass

        log.debug("%s (id %s) stopped", self.name, str(self.threadID))


class SocketSendingWorker (threading.Thread):
    """
    Send data on the given connection.
    """
    def __init__(self, threadID, name, socket, self_stop_event, other_stop_event):
        log.debug("SocketSendingWorker: init")
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.sock = socket
        self.self_stop_event = self_stop_event
        self.other_stop_event = other_stop_event
        log.debug("SocketSendingWorker: socket " + str(type(self.sock)))

        self.connection_closed = False
        log.debug("init finished")

    def run(self):
        if self.sock is None:
            log.debug("no socket, can't start SocketSendingWorker")
        else:
            log.debug("Starting " + self.name + str(self.threadID))
            try:
                last_time = current_milli_time()
                log.debug("time is " + str(last_time))
                while not self.self_stop_event.isSet():
                    message = None
                    try:
                        message = sendingQueue.get_nowait()
                    except queue.Empty:
                        # TODO: find better way to keep the cpu calm
                        sleep(0.01)
                        pass

                    if message is not None:
                        try:
                            log.info("sending " + str(message) + " to " + str(self.sock.getpeername()))
                            self.sock.send(bytes(message))
                            sendingQueue.task_done()
                        except OSError as ose:
                            errorQueue.put("OS error: connection gone {0}".format(ose))
                            log.debug("OS error: connection gone {0}".format(ose))
                            self.stop()



                    # if current_milli_time() - last_time > 1000:
                    #     print("Sending heartbeat to socket." + str(current_milli_time()))
                    #     try :
                    #         self.conn.send(bytes([111,107]))
                    #     except BrokenPipeError:
                    #         print("SocketSendingWorker: Lost connection, BrokenPipe")
                    #     last_time = current_milli_time()
            finally:
                try:
                    threads.remove(self)
                except ValueError:
                    print("SocketSendingWorker: can't remove self from thread list")
                    print(str(threads))

        print("Exiting " + self.name + str(self.threadID))

    def stop(self):
        log.debug("stopping %s (id %s)", self.name, str(self.threadID))
        self.self_stop_event.set()
        log.debug("stopping other")
        self.other_stop_event.set()
        if not self.connection_closed:
            self.sock.close()
            self.connection_closed = True
        try:
            threads.remove(self)
        except ValueError:
            pass

        log.debug("%s (id %s) stopped", self.name, str(self.threadID))
