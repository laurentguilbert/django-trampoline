"""
Models for trampoline tests.
"""
from django.db import models

from tests.doc_types import TokenDoc, PersonDoc
from trampoline.mixins import ESIndexableMixin


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
        if doc.name == 'raise_exception':
            raise RuntimeError
        return doc


class Person(ESIndexableMixin, models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    es_doc_type = PersonDoc
    es_auto_doc_type_mapping = True
