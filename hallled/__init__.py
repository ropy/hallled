import logging
import os
import threading
import time

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import DBSession, Base

from hallled.async.file_watcher import MyEventHandler
from watchdog.observers import Observer


from hallled.async.GatewayClient import GatewayClient


# queueLock = threading.Lock()
# workQueue = queue.Queue(10)
# threads = []

HOST = '192.168.2.95'  # Symbolic name, meaning all available interfaces
PORT = 12345  # Arbitrary non-privileged port

def file_watcher():
    #add the async file listener for incoming data
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    file_path = '/tmp/to_webapp'
    watched_dir = os.path.split(file_path)[0]
    print('watched_dir = {watched_dir}'.format(watched_dir=watched_dir))
    patterns = [file_path]
    print('patterns = {patterns}'.format(patterns=', '.join(patterns)))
    event_handler = MyEventHandler(patterns=patterns)
    observer = Observer()
    observer.schedule(event_handler, watched_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


class ServerThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("Starting " + self.name)
        # start up the Socket Server to handle connection to the bridge
        s = GatewayClient(HOST, PORT)
        s.connect()
        s.socket_handler.handle(s.sock)
        s.socket_handler.run()
        print("Exiting " + self.name)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('react', '/react')
    config.add_route('socket_test', '/socket_test')

    # routes targeted to arduino
    config.add_route('api_led_hslm', '/api/led/hslm')
    config.add_route('api_led_rgbm', '/api/led/rgbm/{red}/{green}/{blue}/{modulo}')
    config.add_route('api_named_pipe', '/api/pipe')
    config.add_route('api_options', '/api/options')


    # info route
    config.add_route('api_info', '/api/info')
    config.scan()

    thread = ServerThread(1, "gateway_client")
    thread.start()

    return config.make_wsgi_app()

