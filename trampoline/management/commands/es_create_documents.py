"""
Management command for trampoline.
"""
import logging
import sys

from elasticsearch_dsl import Index

from trampoline.management.base import ESBaseCommand


logger = logging.getLogger(__name__)


class Command(ESBaseCommand):
    help = (
        "Create documents on {0}{1}INDEX_NAME{2} based on the method "
        "{0}get_indexable_queryset{2} on the related models."
    ).format(ESBaseCommand.BOLD, ESBaseCommand.UNDERLINE, ESBaseCommand.RESET)

    option_list = ESBaseCommand.option_list + (
        ESBaseCommand.options['index_name'],
        ESBaseCommand.options['target_name']
    )
    required_options = ('index_name',)

    STATUS_INDEXED = 0
    STATUS_SKIPPED = 1
    STATUS_FAILED = 2

    def run(self, *args, **options):
        self.target_name = self.target_name or self.index_name

        index = Index(self.target_name)
        if not index.exists():
            self.print_error(
                u"Index '{0}' does not exist."
                .format(self.target_name)
            )
            sys.exit(1)

        self.print_info(u"Indexing objects on '{0}'.".format(self.target_name))

        models = self.trampoline_config.get_index_models(self.index_name)

        for model in models:
            self.print_info(u"Processing model: '{0}'.".format(model.__name__))
            queryset = model.get_indexable_queryset()
            for obj in queryset:
                if obj.is_indexable():
                    if not self.dry_run:
                        result = obj.es_index(
                            async=False,
                            index_name=self.target_name
                        )
                        if result.result is False:
                            status = self.STATUS_FAILED
                        else:
                            status = self.STATUS_INDEXED
                    else:
                        status = self.STATUS_INDEXED
                else:
                    status = self.STATUS_SKIPPED
                self.print_obj_status(obj, model.__name__, status)

        self.print_success("Indexation completed.")

    def print_obj_status(self, obj, model_name, status):
        obj_str = u"{0:<15} {1}".format(model_name, obj.pk)
        if status == self.STATUS_FAILED:
            self.print_error("{0:<15} {1}".format("Failed", obj_str))
        elif status == self.STATUS_SKIPPED:
            self.print_normal(
                u"{0}{1:<15}{2} {3}"
                .format(
                    self.DIM,
                    "Skipped",
                    self.RESET,
                    obj_str
                ),
                verbosity=2
            )
        elif status == self.STATUS_INDEXED:
            self.print_normal(
                u"{0}{1:<15}{2} {3}"
                .format(
                    self.GREEN,
                    "Indexed",
                    self.RESET,
                    obj_str
                ),
                verbosity=2
            )
