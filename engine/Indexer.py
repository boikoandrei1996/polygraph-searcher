import sys
reload(sys)
sys.setdefaultencoding('UTF8')
from peewee import IntegrityError
from models import *


def indexer(web_page, save_lock, stem_lock):
    if not web_page.isDownload:
        raise Exception("You should use downloaded web_page")

    with save_lock:
        #save document to model
        try:
            doc_obj = DocumentModel()
            doc_obj.url = web_page.page_url
            doc_obj.title = web_page.title
            doc_obj.content = web_page.text
            doc_obj.domain = web_page.get_domain()
            doc_obj.save()
        except IntegrityError:
            doc_obj = DocumentModel.get(DocumentModel.url == web_page.page_url)
        except Exception as e:
            print str(type(e))
            raise e

    text_stems = web_page.get_text_stems()
    for stem in text_stems:
        #check and save stem to model
        with stem_lock:
            try:
                stem_obj = StemModel()
                stem_obj.stem = stem
                stem_obj.save()
            except IntegrityError:
                stem_obj = StemModel.get(StemModel.stem == stem)
            except Exception as e:
                print str(type(e))
                raise e

        relation = StemDocumentRelationModel()
        relation.doc = doc_obj
        relation.stem = stem_obj
        relation.count_stem = text_stems[stem]
        relation.type_stem = 1
        relation.save()

    title_stems = web_page.get_title_stems()
    for stem in title_stems:
        with stem_lock:
            try:
                stem_obj = StemModel()
                stem_obj.stem = stem
                stem_obj.save()
            except IntegrityError:
                stem_obj = StemModel.get(StemModel.stem == stem)
            except Exception as e:
                print str(type(e))
                raise e

        relation = StemDocumentRelationModel()
        relation.doc = doc_obj
        relation.stem = stem_obj
        relation.count_stem = title_stems[stem]
        relation.type_stem = 2
        relation.save()


def main():
    pass


if __name__ == '__main__':
    main()
