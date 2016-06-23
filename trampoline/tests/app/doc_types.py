"""
Doc types for test app.
"""
from elasticsearch_dsl import DocType
from elasticsearch_dsl import String


class TokenDoc(DocType):
    name = String()

    class Meta:
        index = 'foobar'
        doc_type = 'token'
