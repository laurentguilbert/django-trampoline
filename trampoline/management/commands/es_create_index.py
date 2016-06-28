"""
Management command for trampoline.
"""
import calendar
import sys
import time

from elasticsearch_dsl import Index

from trampoline.management.base import ESBaseCommand


class Command(ESBaseCommand):
    help = (
        "Create a new index based on its definition inside {0}ES_SETTINGS{2}."
        "\nIf {0}{1}TARGET_NAME{2} is not provided a unique name will be "
        "generated by appending the current timestamp to {0}{1}INDEX_NAME{2}."
    ).format(ESBaseCommand.BOLD, ESBaseCommand.UNDERLINE, ESBaseCommand.RESET)

    option_list = ESBaseCommand.option_list + (
        ESBaseCommand.options['index_name'],
        ESBaseCommand.options['target_name']
    )
    required_options = ('index_name',)

    def run(self, *args, **options):
        self.print_info(u"Creating index '{0}'.".format(self.index_name))

        if self.target_name is None:
            unix_time = calendar.timegm(time.gmtime())
            self.target_name = "{0}_{1}".format(self.index_name, unix_time)

        index = Index(self.target_name)
        models = self.trampoline_config.get_index_models(self.index_name)

        if len(models) == 0:
            self.print_error(
                u"No models defined for index '{0}'."
                .format(self.index_name)
            )
            sys.exit(1)

        for model in models:
            doc_type = model.get_es_doc_type()
            index.doc_type(doc_type)
            self.print_normal(
                u"{0}Add mapping{1} {2}"
                .format(self.GREEN, self.RESET, doc_type._doc_type.name)
            )
        if not self.dry_run:
            index.create()

        self.print_success(
            u"New index created: '{0}'.".format(self.target_name)
        )
