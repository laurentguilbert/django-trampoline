"""
Test paginator for trampoline.
"""
from elasticsearch_dsl import Index
from elasticsearch_dsl import Search

from trampoline.paginator import ESSearchPaginator

from tests.base import BaseTestCase
from tests.models import Token
from tests.views import PaginatedContentView


class TestPaginator(BaseTestCase):

    def setUp(self):
        super(TestPaginator, self).setUp()
        self.doc_type = Token.get_es_doc_type()
        self.index = Index(self.doc_type._doc_type.index)
        self.index.doc_type(self.doc_type)
        self.index.create()
        self.refresh()

        for i in range(3):
            Token.objects.create(name='token {0}'.format(i))
        self.refresh()

    def tearDown(self):
        super(TestPaginator, self).tearDown()
        self.index.delete()

    def test_paginator(self):
        search = Search(
            index=Token.es_doc_type._doc_type.index,
            doc_type=Token.es_doc_type._doc_type.name
        )
        search = search.sort('name')

        page_size = 2
        paginator = ESSearchPaginator(search, page_size)

        page = paginator.page(1)

        self.assertTrue(page.has_other_pages)
        self.assertEqual(len(page.hits), page_size)
        self.assertEqual(page.total_count, 3)

        self.assertEqual(page.hits[0]['name'], 'token 0')
        self.assertEqual(page.hits[1]['name'], 'token 1')

        self.assertEqual(page.paginator, paginator)
        self.assertEqual(page.number, 1)
        self.assertIsNotNone(page.response)

        page = paginator.page(2)

        self.assertFalse(page.has_other_pages)
        self.assertEqual(len(page.hits), 1)

        self.assertEqual(page.hits[0]['name'], 'token 2')

    def test_pagination_mixin(self):
        class Request(object):
            GET = {}

        view = PaginatedContentView()
        view.request = Request()

        self.assertEqual(view.page_size, 2)

        view.request.GET = {}
        self.assertEqual(view.get_page_number(), 1)
        view.request.GET = {'page': -2}
        self.assertEqual(view.get_page_number(), 1)
        view.request.GET = {'page': 'foobar'}
        self.assertEqual(view.get_page_number(), 1)
        view.request.GET = {'page': 5}
        self.assertEqual(view.get_page_number(), 5)

        page = view.paginate_search()
        self.assertIsNotNone(page)
        self.assertIsNotNone(view.page)

        self.assertEqual(view.get_context_data()['page'], view.page)
