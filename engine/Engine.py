from multiprocessing import cpu_count, Event, Process
from multiprocessing.dummy import Queue
import time
import collections
import threading

import ConcurrentCrawler
import Ranker


class Engine(object):

    def __init__(self):
        self.queue = Queue()
        self.is_loaded_queue = False
        self.event_repeat = Event()

    def load_queue(self, iterable_url):
        if isinstance(iterable_url, collections.Iterable):
            for url in iterable_url:
                self.queue.put((url, 0))
            self.is_loaded_queue = True
        else:
            raise Exception("You should use iterable object")

    def start_crawler(self, max_depth, max_width, isAsync, count_process=cpu_count()):
        if not self.is_loaded_queue:
            raise Exception("You should load queue")

        if isAsync:
            crawler = Process(target=ConcurrentCrawler.manager_crawler,
                              args=(self.queue, max_depth, max_width, count_process))
            crawler.start()
        else:
            ConcurrentCrawler.manager_crawler(self.queue, max_depth, max_width, count_process)

        print "You may continue work"

    def start_ranker(self, isAsync, isRepeat, text_boost=1, title_boost=1000,
                     bm25_b=0.75, bm25_k1=2):
        settings = {
            "text_boost": text_boost,
            "title_boost": title_boost,
            "bm25_b": bm25_b,
            "bm25_k1": bm25_k1
        }

        def _check_crawler(event):
            event.set()
            while event.is_set():
                time.sleep(0.2)
            print "Ranker finished"

        def _check_repeat_crawler(_event_ranker, _event_stop_repeat):
            _event_stop_repeat.clear()
            _event_ranker.clear()
            proc = None
            while not _event_stop_repeat.is_set():
                if _event_ranker.is_set():
                    time.sleep(0.5)
                else:
                    _event_ranker.set()
                    if proc is not None and proc.is_alive():
                        proc.terminate()
                    proc = Ranker.Ranker(settings, _event_ranker)
                    proc.start()
            else:
                print "Ranker finished"

        if not isAsync and isRepeat:
            raise Exception("You will be in deadlock, if you use that configure (Sync and Repeat)")

        event_finish_ranker = Event()
        if isAsync:
            if isRepeat:
                repeat_crawler_process = Process(target=_check_repeat_crawler,
                                                 args=(event_finish_ranker, self.event_repeat))
                repeat_crawler_process.start()
            else:
                process = Ranker.Ranker(settings, event_finish_ranker)
                process.start()

                check_process = Process(target=_check_crawler, args=(event_finish_ranker,))
                check_process.start()
        else:
            process = Ranker.Ranker(settings, event_finish_ranker)
            process.start()

            _check_crawler(event_finish_ranker)

        print "You may continue work"

    def stop_repeat_ranker(self):
        self.event_repeat.set()


def main():
    engine = Engine()
    engine.load_queue(["http://www.tut.by/",
                       "http://www.bbc.com/"])
    engine.start_crawler(max_depth=5, max_width=50, isAsync=False, count_process=2)
    engine.start_ranker(isAsync=True, isRepeat=False)

    #threading.Timer(3, engine.stop_repeat_ranker).start()


if __name__ == '__main__':
    main()
    #d=5 w=50 p=2 time=67m56.230s
