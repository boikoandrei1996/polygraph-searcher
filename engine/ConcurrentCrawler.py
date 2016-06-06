import time
from multiprocessing import Process, Queue, Event, Pool,\
                            cpu_count, current_process, Manager

from models import DocumentModel
from WebPage import WebPage
from QueueWrapper import create_mymanager
from Indexer import indexer


def start_process():
    pass
    #print 'Starting -> ', current_process().name


class Crawler(Process):

    def __init__(self, queue_task, lockSaveDB, lockCheckDB, lockStemDB,
                 work_allowance, max_width, max_depth):
        Process.__init__(self)

        self.queue_task = queue_task

        self.lockSaveDB = lockSaveDB
        self.lockCheckDB = lockCheckDB
        self.lockStemDB = lockStemDB
        self.work_allowed = work_allowance

        self.max_width = max_width
        self.max_depth = max_depth
        self.count_link = 1

    def run(self):
        pool = Pool(processes=cpu_count(), initializer=start_process)

        while True:
            if self.work_allowed.is_set():
                if self.queue_task.empty():
                    break
                else:
                    url, current_depth = self.queue_task.get()
                print ">>> " + url
            else:
                time.sleep(0.5)
                continue

            web_page = WebPage(url)
            success_download = web_page.download_page()
            if not success_download:
                continue

            res = pool.apply_async(indexer,
                                   args=(web_page, self.lockSaveDB, self.lockStemDB))

            if self.count_link <= self.max_width \
                    and current_depth + 1 <= self.max_depth:
                links = web_page.get_links()
                for link in links:
                    with self.lockCheckDB:
                        if DocumentModel.filter(url=link):
                            continue

                    if self.queue_task.put((link, current_depth + 1)):
                        self.count_link += 1
                    else:
                        continue

                    if self.count_link > self.max_width:
                        break

        pool.close()
        pool.join()


def manager_crawler(queue_task, max_depth, max_width, count_process):
    man = Manager()
    lockSaveDB = man.Lock()
    lockCheckDB = man.Lock()
    lockStemDB = man.Lock()

    work_allowance = Event()
    list_crawlers = list()

    manager = create_mymanager()
    queue = manager.QueueWrapper()

    while not queue_task.empty():
        queue.put(queue_task.get())
    #queue.put(("http://djbook.ru/rel1.9/intro/tutorial03.html", 0))
    #queue.put(("http://djbook.ru/rel1.9/intro/tutorial04.html", 0))

    for i in xrange(count_process):
        crawler = Crawler(queue, lockSaveDB, lockCheckDB, lockStemDB,
                          work_allowance, max_width, max_depth)
        crawler.start()
        list_crawlers.append(crawler)

    work_allowance.set()

    for crawler in list_crawlers:
        crawler.join()
    print "ALL PROCESS CRAWLER FINISHES"


def main():
    queue = Queue()
    queue.put(("http://djbook.ru/rel1.9/intro/tutorial03.html", 0))
    queue.put(("http://djbook.ru/rel1.9/intro/tutorial04.html", 0))
    manager_crawler(queue, 2, 5, 2)

if __name__ == '__main__':
    main()
    #for depth=5 width=100 process=2
    #time = 60-80 sec

    #with light indexer process time = 80-90