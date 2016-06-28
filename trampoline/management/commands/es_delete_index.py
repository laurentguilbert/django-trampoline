"""
Management command for trampoline.
"""
from elasticsearch_dsl import Index

from trampoline.management.base import ESBaseCommand


class Command(ESBaseCommand):
    help = (
        "Delete the index {0}{1}INDEX_NAME{2} along with all the documents in"
        " it."
    ).format(ESBaseCommand.BOLD, ESBaseCommand.UNDERLINE, ESBaseCommand.RESET)

    option_list = ESBaseCommand.option_list + (
        ESBaseCommand.options['index_name'],
    )
    required_options = ('index_name',)

    def run(self, *args, **options):
        self.confirm(
            u"Are you really sure you want to delete the index '{0}' ?"
            .format(self.index_name)
        )
        index = Index(self.index_name)
        if not self.dry_run:
            index.delete()
        self.print_success(u"Index {0} deleted.".format(self.index_name))
