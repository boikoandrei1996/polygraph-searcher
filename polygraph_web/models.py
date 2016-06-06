from django.db import models

# Create your models here.


class DocumentModel(models.Model):
    url = models.CharField(max_length=255, unique=True)
    title = models.TextField()
    content = models.TextField()
    domain = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return "{0} ({1})".format(self.title, self.url)


class StemModel(models.Model):
    stem = models.CharField(max_length=255, unique=True)
    idf = models.FloatField()

    def __str__(self):
        return "{0} <idf: {1}>".format(self.stem, self.idf)


class StemDocumentRelationModel(models.Model):
    doc = models.ForeignKey(DocumentModel, db_index=True)
    stem = models.ForeignKey(StemModel, db_index=True)
    count_stem = models.IntegerField()
    type_stem = models.IntegerField()
    rank_weight = models.FloatField()

    def __str__(self):
        return "{0} -> {1}".format(self.doc.url, self.stem.stem)
