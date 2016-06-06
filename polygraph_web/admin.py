from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(DocumentModel)
admin.site.register(StemModel)
admin.site.register(StemDocumentRelationModel)
