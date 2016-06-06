# -*- coding: utf-8 -*-

from langdetect import detect, detect_langs, language
from LANGUAGES import LANGUAGES
import snowballstemmer

from models import *


def search_result(request_words):
    request_stems = []
    filters = []
    document_ratings = dict()

    request_words = [word.decode("utf-8") for word in request_words]
    for word in request_words:
        if word.startswith("domain:"):
            filters.append(("domain", word.replace("domain:", "").lower()))
        else:
            correct_lang = "english"
            current_prob = 0
            try:
                for lang in detect_langs(word):
                    lng = lang.lang
                    prob = lang.prob
                    if lng in LANGUAGES \
                            and LANGUAGES[lng].lower() in snowballstemmer.algorithms() \
                            and prob > current_prob:
                        correct_lang = LANGUAGES[lng].lower()
                        current_prob = prob

                request_stems.append(snowballstemmer.stemmer(correct_lang).stemWord(word))
            except Exception as e:
                print "detect --- " + str(type(e))
                request_stems.append(word)

    for word in request_stems:
        try:
            _stem = StemModel.get(StemModel.stem == word)
            print "found " + word
        except Exception as e:
            print "not found " + word
            continue

        term_ratings = dict()
        for relation in StemDocumentRelationModel.select().where(StemDocumentRelationModel.stem == _stem.get_id()):
            #print relation.doc.url
            #print relation.stem.stem

            corresponding = True
            for filt in filters:
                if filt[0] == "domain" and filt[1] != relation.doc.domain:
                    corresponding = False

            if not corresponding:
                continue

            rank_weight = relation.rank_weight
            if rank_weight < 0:
                rank_weight = 0

            if relation.doc_id in term_ratings:
                term_ratings[relation.doc_id] += rank_weight
            else:
                term_ratings[relation.doc_id] = rank_weight

        for doc_id in term_ratings:
            term_ratings[doc_id] = term_ratings[doc_id] / (2 + term_ratings[doc_id]) * _stem.idf

            if doc_id in document_ratings:
                document_ratings[doc_id] += term_ratings[doc_id]
            else:
                document_ratings[doc_id] = term_ratings[doc_id]

        del term_ratings

    #result_dict = {}
    #for doc_id in document_ratings:
    #    url = DocumentModel.get(DocumentModel.id == doc_id).url
    #    result_dict[url] = document_ratings[doc_id]

    return document_ratings


def main():
    dct = search_result(["Швейцарцы", "отвергли", "доход", "доллар"])
    print dct
    #for doc_id in dct:
    #    print DocumentModel.get(DocumentModel.id == doc_id).url
    dct = search_result(["django", "tutorial"])
    print dct
    #for doc_id in dct:
    #    print DocumentModel.get(DocumentModel.id == doc_id).url
    #dct = search_result(["what"])
    #print dct
    #for doc_id in dct:
    #    print DocumentModel.get(DocumentModel.id == doc_id).url
    #dct = search_result(['"белтелеком"'])
    #print dct
    #for doc_id in dct:
    #    print DocumentModel.get(DocumentModel.id == doc_id).url


if __name__ == '__main__':
    main()
