"""
Management command for trampoline.
"""
from __future__ import print_function
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from optparse import make_option
import logging
import sys

from tqdm import tqdm

from elasticsearch_dsl import Index

from django.contrib.contenttypes.models import ContentType

from trampoline.management.base import ESBaseCommand
from trampoline.tasks import es_index_object
from trampoline.tasks import STATUS_FAILED
from trampoline.tasks import STATUS_IGNORED
from trampoline.tasks import STATUS_INDEXED


logger = logging.getLogger(__name__)


class Command(ESBaseCommand):
    help = (
        "Create documents on {0}{1}INDEX_NAME{2} based on the method "
        "{0}get_indexable_queryset{2} on the related models."
    ).format(ESBaseCommand.BOLD, ESBaseCommand.UNDERLINE, ESBaseCommand.RESET)

    MAX_THREADS_DEFAULT = 4

    option_list = ESBaseCommand.option_list + (
        ESBaseCommand.options['index_name'],
        ESBaseCommand.options['target_name'],
        make_option(
            '--threads',
            dest='max_threads',
            default=MAX_THREADS_DEFAULT,
            help="Number of threads."
        ),
        make_option(
            '--cleanup',
            dest='cleanup',
            action='store_true',
            default=False,
            help="Delete stale documents."
        ),
    )
    required_options = ('index_name',)

    def run(self, *args, **options):
        self.target_name = self.target_name or self.index_name
        self.log_file = open('trampoline.log', 'w')

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
            queryset = model.get_indexable_queryset()
            object_ids = queryset.values_list('pk', flat=True)
            content_type_id = ContentType.objects.get_for_model(model).pk

            model_name = model.__name__
            self.print_info(u"Processing model: '{0}'.".format(model_name))

            if self.cleanup:
                self.delete_stale_documents(model, object_ids)

            progress_status = {
                STATUS_INDEXED: 0,
                STATUS_FAILED: 0,
                STATUS_IGNORED: 0,
            }
            desc = self.get_progress_bar_desc(progress_status)
            progress_bar = tqdm(
                total=len(object_ids),
                dynamic_ncols=True,
                desc=desc
            )

            max_threads = self.get_max_threads()
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                tasks = [
                    executor.submit(
                        self.index_object,
                        content_type_id,
                        object_id
                    )
                    for object_id in object_ids
                ]
                for task in as_completed(tasks):
                    result = task.result()

                    status = result['status']
                    if status in progress_status:
                        progress_status[status] += 1

                    exc = result.get('exc')
                    if exc is not None:
                        print(
                            "FAILED: pk {0} (content_type {1})\n"
                            .format(
                                result['content_type_id'],
                                result['object_id'],
                            ),
                            str(exc),
                            file=self.log_file
                        )

                    desc = self.get_progress_bar_desc(progress_status)
                    progress_bar.set_description(desc)
                    progress_bar.update()
            progress_bar.close()

        self.log_file.close()
        self.print_success("Indexation completed.")

    def delete_stale_documents(self, model, object_ids):
        self.print_info("Deleting stale documents.")
        es_ids = []
        for item in model.es_doc_type.search().fields([]).scan():
            es_ids.append(str(item.meta.id))
        es_ids = set(es_ids)
        stale_ids = es_ids - set(map(str, object_ids))
        for stale_id in stale_ids:
            model.es_doc_type.get(stale_id).delete(ignore=404)
        self.print_success("Cleanup completed.")

    def get_progress_bar_desc(self, progress_status):
        desc = (
            "{0}S {1} {2}F {3} {4}I {5}{6}"
            .format(
                self.GREEN,
                progress_status[STATUS_INDEXED],
                self.RED,
                progress_status[STATUS_FAILED],
                self.YELLOW,
                progress_status[STATUS_IGNORED],
                self.RESET,
            )
        )
        return desc

    def get_max_threads(self):
        try:
            max_threads = int(self.max_threads)
        except:
            max_threads = self.MAX_THREADS_DEFAULT
        else:
            if max_threads < 1 or max_threads > 10:
                max_threads = self.MAX_THREADS_DEFAULT
        return max_threads

    def index_object(self, content_type_id, object_id):
        result = {
            'status': STATUS_INDEXED,
            'object_id': object_id,
            'content_type_id': content_type_id,
        }
        if not self.dry_run:
            try:
                result['status'] = es_index_object.run(
                    self.target_name,
                    content_type_id,
                    object_id,
                    fail_silently=False
                )
            except Exception as exc:
                result['status'] = STATUS_FAILED
                result['exc'] = exc
        return result
