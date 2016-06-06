from peewee import *

db = MySQLDatabase("polygraph_db", host="127.0.0.1", user="boikoandrei", passwd="1610")


class DocumentModel(Model):
    url = CharField(unique=True)
    title = TextField()
    content = TextField()
    domain = CharField(index=True)

    class Meta:
        database = db
        db_table = "polygraph_web_documentmodel"


class StemModel(Model):
    stem = CharField(unique=True)
    idf = FloatField()

    class Meta:
        database = db
        db_table = "polygraph_web_stemmodel"


class StemDocumentRelationModel(Model):
    doc = ForeignKeyField(DocumentModel, index=True)
    stem = ForeignKeyField(StemModel, index=True)
    count_stem = IntegerField()
    type_stem = IntegerField()
    rank_weight = FloatField()

    class Meta:
        database = db
        db_table = "polygraph_web_stemdocumentrelationmodel"


#class QueueModel(Model):
#    url = CharField()
#    depth = IntegerField()


def main():
    pass


if __name__ == '__main__':
    main()
