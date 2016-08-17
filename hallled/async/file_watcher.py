import sys, os.path, time, logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class MyEventHandler(PatternMatchingEventHandler):
    def on_moved(self, event):
        super(MyEventHandler, self).on_moved(event)
        logging.info("File %s was just moved" % event.src_path)

    def on_created(self, event):
        super(MyEventHandler, self).on_created(event)
        logging.info("File %s was just created" % event.src_path)

    def on_deleted(self, event):
        super(MyEventHandler, self).on_deleted(event)
        logging.info("File %s was just deleted" % event.src_path)

    def on_modified(self, event):
        super(MyEventHandler, self).on_modified(event)
        logging.info("File %s was just modified" % event.src_path)
        self.read_pipe_data()

    def read_pipe_data(self):
        # path = "/tmp/to_webapp"
        # fifo = open(path, "rb")
        # for line in fifo:
        #     logging.info("Received: %s",line)
        # fifo.close()
        path = "/tmp/to_webapp"
        with open(path, "rb") as f:
            line = f.readline()
            if line != "":
                logging.info("received from bridge: %s", line)

        self.delete_content(path)

    def delete_content(self, fName):
        with open(fName, "w"):
            pass


def main(file_path=None):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    watched_dir = os.path.split(file_path)[0]
    print('watched_dir = {watched_dir}'.format(watched_dir=watched_dir))
    patterns = [file_path]
    print('patterns = {patterns}'.format(patterns=', '.join(patterns)))
    event_handler = MyEventHandler(patterns=patterns)
    observer = Observer()
    observer.schedule(event_handler, watched_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        main(file_path=path.strip())
    else:
        sys.exit(1)