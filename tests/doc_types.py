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


class PersonDoc(DocType):
    first_name = String(index='not_analyzed')
    last_name = String(index='not_analyzed')
    full_name = String(index='not_analyzed')

    class Meta:
        index = 'foobar'
        doc_type = 'person'

    @staticmethod
    def prepare_full_name(obj):
        return u"{0} {1}".format(obj.first_name, obj.last_name)
