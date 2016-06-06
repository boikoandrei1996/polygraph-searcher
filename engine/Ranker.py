from models import *
from multiprocessing import Process, Pool, cpu_count, current_process, Event
from peewee import fn
from math import log


lst_args = {}


def start_process():
    pass
    #print 'Starting -> ', current_process().name


class Ranker(Process):

    def __init__(self, settings, event_finish_ranker):
        Process.__init__(self)
        lst_args.setdefault("b", float(settings["bm25_b"]))
        lst_args.setdefault("boost_factor_type1", settings["text_boost"])
        lst_args.setdefault("boost_factor_type2", settings["title_boost"])
        self.event = event_finish_ranker

    def run(self):
        self.event.set()

        avg_length_type1 = DocumentModel.select(fn.Avg(fn.Length(DocumentModel.content)))
        avg_length_type2 = DocumentModel.select(fn.Avg(fn.Length(DocumentModel.title)))

        lst_args.setdefault("avg_length_type1", avg_length_type1)
        lst_args.setdefault("avg_length_type2", avg_length_type2)

        pool = Pool(processes=cpu_count(), initializer=start_process)
        pool.map_async(calculate, StemDocumentRelationModel.select())

        pool.close()
        pool.join()

        self.event.clear()


def calculate(relation):
    count_doc_all = DocumentModel.select().count()
    if relation.type_stem == 1:
        field_len = len(relation.doc.content)
        boost_factor = lst_args["boost_factor_type1"]
        avg_length = lst_args["avg_length_type1"]
    elif relation.type_stem == 2:
        field_len = len(relation.doc.title)
        boost_factor = lst_args["boost_factor_type2"]
        avg_length = lst_args["avg_length_type1"]
    else:
        raise NotImplementedError

    b = lst_args["b"]
    weight = relation.count_stem * boost_factor / ((1 - b) + b * (field_len / avg_length))

    relation.rank_weight = weight
    relation.save()

    count_doc_with_stem = StemDocumentRelationModel.select().where(StemDocumentRelationModel.stem == relation.stem).count()

    z = (count_doc_all - count_doc_with_stem + 0.5) / (count_doc_with_stem + 0.5)
    if z > 1:
        relation.stem.idf = log(z)
    else:
        relation.stem.idf = 0
    relation.stem.save()


def main():
    settings = {
        "text_boost": 1,
        "title_boost": 1000,
        "bm25_b": 0.75,
        "bm25_k1": 2
    }

    event = Event()
    proc = Ranker(settings, event)
    proc.start()


if __name__ == '__main__':
    main()
