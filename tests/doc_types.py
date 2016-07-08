"""
Doc types for trampoline tests.
"""
from elasticsearch_dsl import DocType
from elasticsearch_dsl import String


class TokenDoc(DocType):
    name = String(index='not_analyzed')

    class Meta:
        index = 'foobar'
        doc_type = 'token'
