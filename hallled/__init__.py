import logging
import os

import time

from pyramid.config import Configurator

from hallled.async.file_watcher import MyEventHandler
from watchdog.observers import Observer
import queue
import threading

queueLock = threading.Lock()
workQueue = queue.Queue(10)
threads = []

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

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q

    def run(self):
        print ("Starting " + self.name)
        file_watcher()
        print ("Exiting " + self.name)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('react', '/react')


    # config.add_route('api_led_coa', '/api/led/{command}/{operator}/{amount}')
    # routes targeted to arduino
    config.add_route('api_led_hslm', '/api/led/hslm')
    config.add_route('api_led_rgbm', '/api/led/rgbm/{red}/{green}/{blue}/{modulo}')
    config.add_route('api_serialcommand', '/api/raw/{command}')
    config.add_route('api_named_pipe', '/api/pipe')
    config.add_route('api_options', '/api/options')

    # info route
    config.add_route('api_info', '/api/info')
    config.scan()

    thread = myThread(1, "file_watcher", workQueue)
    thread.start()
    threads.append(thread)


    return config.make_wsgi_app()

