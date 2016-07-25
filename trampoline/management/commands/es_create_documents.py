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

    def run(self, *args, **options):
        self.target_name = self.target_name or self.index_name

        index = Index(self.target_name)
        if not index.exists():
            self.print_error(u"Index '{0}' does not exist.".format(
                self.target_name))
            sys.exit(1)

        self.print_info(u"Indexing objects on '{0}'.".format(self.target_name))

        models = self.trampoline_config.get_index_models(self.index_name)

        for model in models:
            self.print_info(u"Processing model: '{0}'.".format(model.__name__))
            queryset = model.get_indexable_queryset()
            for obj in queryset:
                if obj.is_indexable():
                    if not self.dry_run:
                        try:
                            obj.es_index(
                                async=False,
                                index_name=self.target_name
                            )
                        except Exception:
                            logger.exception(
                                "Exception while indexing object (pk={0})"
                                .format(obj.pk)
                            )
                        else:
                            self.print_normal(
                                "{0}Indexed{1} {2} (pk={3})"
                                .format(self.GREEN, self.RESET, obj, obj.pk),
                                verbosity=2
                            )
                else:
                    self.print_normal("{0}Skipped{1} {2}".format(
                        self.DIM, self.RESET, obj), verbosity=2)

        self.print_success("Indexation completed.")
