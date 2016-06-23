"""
Base test case for trampoline.
"""
from django.test import TransactionTestCase
from django.test.utils import override_settings

from elasticsearch_dsl.connections import connections


TRAMPOLINE = {
    'INDICES': {
        'foobar': {
            'models': ('trampoline.tests.app.models.Token',)
        },
    }
}


@override_settings(TRAMPOLINE=TRAMPOLINE)
class BaseTestCase(TransactionTestCase):
    connection = connections.get_connection()

    def refresh(self):
        self.connection.indices.refresh('_all')

    def docExists(self, obj, obj_id):
        doc_type = obj.get_es_doc_type()
        doc_type_name = doc_type._doc_type.name
        index_name = doc_type._doc_type.index
        obj_id = obj_id or obj.pk
        return self.connection.exists(
            index=index_name, doc_type=doc_type_name, id=obj_id)

    def aliasExists(self, index, name):
        return self.connection.indices.exists_alias(index=index, name=name)

    def indexExists(self, index):
        return self.connection.indices.exists(index=index)

    def typeExists(self, index, doc_type_name):
        return self.connection.indices.exists_type(
            index=index, doc_type=doc_type_name)

    def assertAliasExists(self, index, name):
        self.assertTrue(self.aliasExists(index, name))

    def assertAliasDoesntExist(self, index, name):
        self.assertFalse(self.aliasExists(index, name))

    def assertIndexExists(self, index):
        self.assertTrue(self.indexExists(index))

    def assertIndexDoesntExist(self, index):
        self.assertFalse(self.indexExists(index))

    def assertTypeExists(self, index, doc_type):
        self.assertTrue(self.typeExists(index, doc_type))

    def assertTypeDoesntExist(self, index, doc_type):
        self.assertFalse(self.typeExists(index, doc_type))

    def assertDocExists(self, obj, obj_id=None):
        self.assertTrue(self.docExists(obj, obj_id))

    def assertDocDoesntExist(self, obj, obj_id=None):
        self.assertFalse(self.docExists(obj, obj_id))
