"""
Management command for trampoline.
"""
import logging
import sys

from django.contrib.contenttypes.models import ContentType
from elasticsearch_dsl import Index

from trampoline.management.base import ESBaseCommand
from trampoline.tasks import es_index_object

logger = logging.getLogger(__name__)


class Command(ESBaseCommand):
    help = (
        "Rebuilds index {0}{1}INDEX_NAME{2} based on the method "
        "{0}get_indexable_queryset{2} on the related models. "
        "Compares ids fro ES and queryset"
    ).format(ESBaseCommand.BOLD, ESBaseCommand.UNDERLINE, ESBaseCommand.RESET)

    option_list = ESBaseCommand.option_list + (
        ESBaseCommand.options['index_name'],
        ESBaseCommand.options['target_name'],
        ESBaseCommand.options['async'],
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

            db_pks = set([int(pk) for pk in queryset.values_list('pk',
                                                                 flat=True)])
            es_ids = []
            for item in model.es_doc_type.search().fields([]).scan():
                es_ids.append(int(item.meta.id))
            es_ids = set(es_ids)

            bad_ids = es_ids - db_pks

            if not self.dry_run:
                if bad_ids:
                    self.print_info(u"Deleting {0} items".format(len(bad_ids)))
                    for es_id in bad_ids:
                        model.es_doc_type.get(es_id).delete()

                ct_id = ContentType.objects.get_for_model(model).pk

                self.print_info(u"Reindexing {0} items".format(len(db_pks)))

                pbar = self.init_progressbar(len(db_pks))

                for pk in db_pks:
                    if options['async']:
                        es_index_object.apply_async(
                            args=(self.target_name, ct_id, pk),
                            queue=self.trampoline_config.celery_queue)
                    else:
                        es_index_object.apply(
                            args=(self.target_name, ct_id, pk))
                    pbar.increment()
                    sys.stdout.flush()

                pbar.finish()
            else:
                self.print_info('ES Items to delete: {}'.format(len(bad_ids)))
                self.print_info('Records to reindex: {}'.format(len(db_pks)))

        self.print_success("Indexation completed.")
