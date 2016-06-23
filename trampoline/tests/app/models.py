"""
Models for test app.
"""
from django.db import models

from trampoline.mixins import ESIndexableMixin
from trampoline.tests.app.doc_types import TokenDoc


class Token(ESIndexableMixin, models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    es_doc_type = TokenDoc

    def is_indexable(self):
        if self.name == 'not_indexable':
            return False
        return True

    @classmethod
    def get_indexable_queryset(cls):
        return Token.objects.all()

    def get_es_doc_mapping(self):
        doc = TokenDoc()
        doc.name = self.name
        return doc
