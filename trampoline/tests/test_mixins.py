"""
Test mixins for trampoline.
"""
from django.test.utils import override_settings

from elasticsearch_dsl import Index

from trampoline.tests.app.models import Token
from trampoline.tests.base import BaseTestCase


class TestMixins(BaseTestCase):

    def setUp(self):
        super(TestMixins, self).setUp()
        self.doc_type = Token.get_es_doc_type()
        self.index = Index(self.doc_type._doc_type.index)
        self.index.doc_type(self.doc_type)
        self.index.create()
        self.refresh()

    def tearDown(self):
        super(TestMixins, self).tearDown()
        self.index.delete()

    def test_es_index(self):
        token = Token(name='token')

        with override_settings(TRAMPOLINE={'OPTIONS': {'disabled': True}}):
            token.save()
            self.assertDocDoesntExist(token)

        token.save()
        doc = token.get_es_doc()
        self.assertEqual(doc.name, 'token')
        self.assertEqual(doc._id, str(token.pk))

        # Update model and synchronise doc.
        token.name = 'kento'
        token.save()
        doc = token.get_es_doc()
        self.assertEqual(doc.name, 'kento')

    def test_es_delete(self):
        token = Token.objects.create(name='token')
        token_id = token.pk
        self.assertDocExists(token)

        with override_settings(TRAMPOLINE={'OPTIONS': {'disabled': True}}):
            token.delete()
            self.assertDocExists(Token, token_id)

        token.save()
        token_id = token.pk
        token.delete()
        self.assertDocDoesntExist(Token, token_id)
