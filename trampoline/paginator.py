"""
Paginator for trampoline.
"""


class ESSearchPaginator(object):

    def __init__(self, search, page_size):
        self.search = search
        self.page_size = page_size

    def page(self, page_number):
        return Page(self, page_number)


class Page(object):

    def __init__(self, paginator, page_number):
        self.paginator = paginator
        self.number = page_number

        bottom_offset = self.paginator.page_size * (page_number - 1)
        top_offset = bottom_offset + self.paginator.page_size
        search = self.paginator.search[bottom_offset:top_offset]
        response = search.execute()
        self.hits = response.hits
        self.response = response

        self.total_count = response.hits.total
        if self.total_count > (self.paginator.page_size * page_number):
            self.has_other_pages = True
        else:
            self.has_other_pages = False
