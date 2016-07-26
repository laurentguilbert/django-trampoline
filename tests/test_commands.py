"""
Test management commands for trampoline.
"""
from django.conf import settings
from django.core.management import call_command

from elasticsearch_dsl import Index

from tests.base import BaseTestCase
from tests.models import Token
from trampoline import get_trampoline_config

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

        # Index name isn't defined.
        with self.assertRaises(SystemExit):
            call_command('es_create_index', index_name='doesntexist')

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
        # If verbosity is not an int it defaults to 1.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_index',
                index_name='foobar',
                target_name='foobar_target',
                traceback=True,
                verbosity='notint'
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
                yes=True
            )

        index = Index('foobar')
        index.create()
        self.refresh()
        self.assertIndexExists('foobar')

        call_command(
            'es_delete_index',
            index_name='foobar',
            yes=True
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
                yes=True
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
                yes=True
            )

        trampoline_config.connection.indices.put_alias(
            index='foobar_target', name='foobar')
        self.assertAliasExists(index='foobar_target', name='foobar')

        call_command(
            'es_delete_alias',
            index_name='foobar',
            target_name='foobar_target',
            yes=True
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

        # Disable auto indexing while creating objects.
        settings.TRAMPOLINE['OPTIONS']['disabled'] = True
        token = Token.objects.create(name="token")
        token_not_indexable = Token.objects.create(name='not_indexable')
        token_raise_exception = Token.objects.create(name='raise_exception')
        settings.TRAMPOLINE['OPTIONS']['disabled'] = False

        # Dry run.
        call_command(
            'es_create_documents',
            index_name='foobar',
            dry_run=True
        )
        self.assertDocDoesntExist(token)
        self.assertDocDoesntExist(token_not_indexable)
        self.assertDocDoesntExist(token_raise_exception)

        call_command(
            'es_create_documents',
            index_name='foobar',
            verbosity=3
        )
        self.assertDocExists(token)
        self.assertDocDoesntExist(token_not_indexable)
        self.assertDocDoesntExist(token_raise_exception)
