"""
Views for trampoline.
"""
from django.utils.functional import cached_property

from trampoline.paginator import ESSearchPaginator


class ESPaginationMixin(object):
    page_size = 10

    def get_search(self):
        raise NotImplementedError

    def get_page_number(self):
        number = 1
        try:
            number = int(self.request.GET.get('page'))
        except (TypeError, ValueError):
            pass
        if number < 1:
            number = 1
        return number

    def paginate_search(self):
        search = self.get_search()
        paginator = ESSearchPaginator(search, self.page_size)
        page_number = self.get_page_number()
        return paginator.page(page_number)

    @cached_property
    def page(self):
        return self.paginate_search()

    def get_context_data(self, *args, **kwargs):
        context = (
            super(ESPaginationMixin, self).get_context_data(*args, **kwargs)
        )
        context.update({'page': self.page})
        return context
