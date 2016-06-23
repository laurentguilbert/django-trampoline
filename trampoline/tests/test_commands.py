"""
Test management commands for trampoline.
"""
from django.core.management import call_command

from elasticsearch_dsl import Index

from trampoline import get_trampoline_config
from trampoline.tests.app.models import Token
from trampoline.tests.base import BaseTestCase

trampoline_config = get_trampoline_config()


class TestCommands(BaseTestCase):

    def tearDown(self):
        super(TestCommands, self).tearDown()
        # Delete remnants of previous tests.
        Index('foobar').delete(ignore=404)
        Index('foobar_target').delete(ignore=404)

    def test_es_create_index(self):
        # Index name required.
        with self.assertRaises(SystemExit):
            call_command('es_create_index')

        # Dry run.
        call_command(
            'es_create_index',
            index_name='foobar',
            target_name='foobar_target',
            dry_run=True
        )
        self.assertIndexDoesntExist('foobar_target')

        # Successful call.
        call_command(
            'es_create_index',
            index_name='foobar',
            target_name='foobar_target'
        )
        self.assertIndexExists('foobar_target')
        self.assertTypeExists(index='foobar_target', doc_type='token')

        self.assertIndexDoesntExist('foobar')

        # Index already exists.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_index',
                index_name='foobar',
                target_name='foobar_target'
            )

    def test_es_delete_index(self):
        # Index name required.
        with self.assertRaises(SystemExit):
            call_command('es_delete_index')

        # Index doesn't exist.
        with self.assertRaises(SystemExit):
            call_command(
                'es_delete_index',
                index_name='foobar',
                no_verification=True
            )

        index = Index('foobar')
        index.create()
        self.refresh()
        self.assertIndexExists('foobar')

        call_command(
            'es_delete_index',
            index_name='foobar',
            no_verification=True
        )
        self.assertIndexDoesntExist('foobar')

    def test_es_create_alias(self):
        # Index name required.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_alias',
                target_name='foobar_target'
            )

        # Target name required.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_alias',
                index_name='foobar'
            )

        # Index doesn't exist.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_alias',
                index_name='foobar',
                target_name='foobar_target'
            )

        index = Index('foobar_target')
        index.create()
        self.refresh()

        # Alias with same name as index.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_alias',
                index_name='foobar_target',
                target_name='foobar_target'
            )

        # Dry run.
        call_command(
            'es_create_alias',
            index_name='foobar',
            target_name='foobar_target',
            dry_run=True
        )
        self.assertAliasDoesntExist(index='foobar_target', name='foobar')

        call_command(
            'es_create_alias',
            index_name='foobar',
            target_name='foobar_target'
        )
        self.assertAliasExists(index='foobar_target', name='foobar')

    def test_es_delete_alias(self):
        # Index name required.
        with self.assertRaises(SystemExit):
            call_command(
                'es_delete_alias',
                target_name='foobar_target'
            )

        # Target name required.
        with self.assertRaises(SystemExit):
            call_command(
                'es_delete_alias',
                index_name='foobar'
            )

        # Index doesn't exist.
        with self.assertRaises(SystemExit):
            call_command(
                'es_delete_alias',
                index_name='foobar',
                target_name='foobar_target',
                no_verification=True
            )

        index = Index('foobar_target')
        index.create()
        self.refresh()

        # Alias doesn't exist.
        with self.assertRaises(SystemExit):
            call_command(
                'es_delete_alias',
                index_name='foobar',
                target_name='foobar_target',
                no_verification=True
            )

        self.trampoline_config.connection.indices.put_alias(
            index='foobar_target', name='foobar')
        self.assertAliasExists(index='foobar_target', name='foobar')

        call_command(
            'es_delete_alias',
            index_name='foobar',
            target_name='foobar_target',
            no_verification=True
        )
        self.assertAliasDoesntExist(index='foobar_target', name='foobar')

    def test_es_create_documents(self):
        # Index name required.
        with self.assertRaises(SystemExit):
            call_command('es_create_documents')

        # index_name not in settings.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_documents',
                index_name='barfoo'
            )

        # Index doesn't exist.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_documents',
                index_name='foobar'
            )

        index = Index('foobar')
        doc_type = Token.get_es_doc_type()
        index.doc_type(doc_type)
        index.create()
        self.refresh()

        token = Token.objects.create(name="token")
        token.es_delete()

        token_not_indexable = Token.objects.create(name="not_indexable")

        # Dry run.
        call_command(
            'es_create_documents',
            index_name='foobar',
            dry_run=True
        )
        self.assertDocDoesntExist(token)
        self.assertDocDoesntExist(token_not_indexable)

        call_command(
            'es_create_documents',
            index_name='foobar'
        )
        self.assertDocExists(token)
        self.assertDocDoesntExist(token_not_indexable)
