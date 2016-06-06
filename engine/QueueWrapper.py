from multiprocessing import Queue, Lock
from multiprocessing.managers import BaseManager


class MyManager(BaseManager):
    pass


def create_mymanager():
    man = MyManager()
    man.start()
    return man


class QueueWrapper(object):

    def __init__(self):
        self.queue = Queue()
        self.container = set()
        self.lock_container = Lock()

    def put(self, item):
        with self.lock_container:
            for elem in self.container:
                if item[0] == elem[0]:
                    return False
            self.container.add(item)
            self.queue.put(item)
            return True

    def get(self):
        item = self.queue.get()
        with self.lock_container:
            self.container.remove(item)
        return item

    def qsize(self):
        return self.queue.qsize()

    def empty(self):
        return self.queue.empty()

    def full(self):
        return self.queue.full()


MyManager.register("QueueWrapper", QueueWrapper)


def main():
    pass


if __name__ == '__main__':
    main()
