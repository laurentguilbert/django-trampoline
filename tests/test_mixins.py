"""
Test mixins for trampoline.
"""
from django.conf import settings

from elasticsearch_dsl import Index

from trampoline.mixins import ESIndexableMixin

from tests.base import BaseTestCase
from tests.models import Person
from tests.models import Token


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

    def test_is_indexable(self):
        self.assertTrue(ESIndexableMixin().is_indexable())

    def test_is_index_update_needed(self):
        self.assertTrue(ESIndexableMixin().is_index_update_needed())

    def test_get_indexable_queryset(self):
        self.assertEqual(
            str(Token.get_indexable_queryset().query),
            str(Token.objects.all().query)
        )

    def test_get_es_doc(self):
        token = Token(name="token")
        self.assertIsNone(token.get_es_doc())
        token.save()
        self.assertIsNotNone(token.get_es_doc())

    def test_auto_doc_type_mapping(self):
        person = Person(first_name="Simion", last_name="Baws")
        person.save()
        doc_type = person.get_es_doc_mapping()
        self.assertEqual(doc_type.first_name, person.first_name)
        self.assertEqual(doc_type.last_name, person.last_name)
        self.assertEqual(
            doc_type.full_name,
            u"{0} {1}".format(person.first_name, person.last_name)
        )

    def test_es_index(self):
        # Asynchronous call.
        token = Token.objects.create(name='not_indexable')
        self.assertDocDoesntExist(token)
        token.es_index()
        self.assertDocExists(token)

        # Synchronous call.
        token = Token.objects.create(name='not_indexable')
        self.assertDocDoesntExist(token)
        token.es_index(async=False)
        self.assertDocExists(token)

        # Fail silently.
        settings.TRAMPOLINE['OPTIONS']['disabled'] = True
        token = Token.objects.create(name='raise_exception')
        settings.TRAMPOLINE['OPTIONS']['disabled'] = False
        token.es_index()
        self.assertDocDoesntExist(token)

        # Hard fail.
        settings.TRAMPOLINE['OPTIONS']['fail_silently'] = False
        with self.assertRaises(RuntimeError):
            token.es_index()
        settings.TRAMPOLINE['OPTIONS']['fail_silently'] = True

    def test_es_delete(self):
        # Asynchronous call.
        token = Token.objects.create(name='token')
        self.assertDocExists(token)
        token.es_delete()
        self.assertDocDoesntExist(Token, token.pk)

        # Synchronous call.
        token = Token.objects.create(name='token')
        self.assertDocExists(token)
        token.es_delete(async=False)
        self.assertDocDoesntExist(Token, token.pk)

        # Fail silently if document doesn't exist.
        token.es_delete()

        from trampoline import get_trampoline_config
        trampoline_config = get_trampoline_config()

        # Fake delete to raise exception.
        backup_delete = trampoline_config.connection.delete

        def delete_raise_exception(*args, **kwargs):
            raise RuntimeError
        trampoline_config.connection.delete = delete_raise_exception

        # Fail silently
        token.es_delete()

        # Hard fail.
        settings.TRAMPOLINE['OPTIONS']['fail_silently'] = False
        with self.assertRaises(RuntimeError):
            token.es_delete()
        settings.TRAMPOLINE['OPTIONS']['fail_silently'] = True

        trampoline_config.connection.delete = backup_delete

    def test_save(self):
        token = Token(name='token')

        settings.TRAMPOLINE['OPTIONS']['disabled'] = True
        token.save()
        settings.TRAMPOLINE['OPTIONS']['disabled'] = False
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

        # Instance is not indexable.
        token = Token.objects.create(name='not_indexable')
        self.assertDocDoesntExist(token)

    def test_delete(self):
        token = Token.objects.create(name='token')
        token_id = token.pk
        self.assertDocExists(token)

        settings.TRAMPOLINE['OPTIONS']['disabled'] = True
        token.delete()
        settings.TRAMPOLINE['OPTIONS']['disabled'] = False
        self.assertDocExists(Token, token_id)

        token.save()
        token_id = token.pk
        token.delete()
        self.assertDocDoesntExist(Token, token_id)
