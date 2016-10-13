"""
Views for trampoline tests.
"""
from django.views.generic import TemplateView

from elasticsearch_dsl import Search

from trampoline.views import ESPaginationMixin

from tests.models import Token


class PaginatedContentView(ESPaginationMixin, TemplateView):
    page_size = 2

    def get_search(self):
        return Search(
            index=Token.es_doc_type._doc_type.index,
            doc_type=Token.es_doc_type._doc_type.name
        )
