"""
App config for trampoline.
"""
from copy import deepcopy
import collections

import six

from django.conf import settings
from django.db import transaction
from django.db.models.signals import class_prepared
from django.db.models.signals import post_delete
from django.db.models.signals import post_save

from elasticsearch_dsl.connections import connections

try:
    from django.apps import AppConfig
except ImportError:
    AppConfig = object


DEFAULT_TRAMPOLINE = {
    'HOST': 'localhost',
    'INDICES': {},
    'OPTIONS': {
        'fail_silently': True,
        'disabled': False,
    },
}


def recursive_update(d, u):
    for k, v in six.iteritems(u):
        if isinstance(v, collections.Mapping):
            r = recursive_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def post_save_es_index(sender, instance, **kwargs):
    if instance.is_indexable():
        try:
            # post_save fires after the save occurs but before the transaction
            # is commited.
            transaction.on_commit(lambda: instance.es_index())
        except AttributeError:
            # 1s countdown waiting for the transaction to complete.
            instance.es_index(countdown=1)


def post_delete_es_delete(sender, instance, **kwargs):
    instance.es_delete()


def class_prepared_check_indexable(sender, **kwargs):
    try:
        # Apps unrelated to trampoline might be loaded first.
        from trampoline.mixins import ESIndexableMixin
    except ImportError:
        pass
    else:
        if issubclass(sender, ESIndexableMixin):
            post_save.connect(post_save_es_index, sender=sender)
            post_delete.connect(post_delete_es_delete, sender=sender)


class TrampolineConfig(AppConfig):
    name = 'trampoline'
    verbose_name = "Trampoline"

    def __init__(self, *args, **kwargs):
        class_prepared.connect(class_prepared_check_indexable)
        super(TrampolineConfig, self).__init__(*args, **kwargs)

    def ready(self):
        connections.configure(default={'hosts': self.host})

    def get_index_models(self, index_name):
        try:
            model_paths = self.indices[index_name]['models']
        except KeyError:
            return []

        models = []
        for model_path in model_paths:
            module_path, model_name = model_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[''])
            model = getattr(module, model_name)
            models.append(model)
        return models

    @property
    def settings(self):
        USER_TRAMPOLINE = getattr(settings, 'TRAMPOLINE', {})
        TRAMPOLINE = deepcopy(DEFAULT_TRAMPOLINE)
        return recursive_update(TRAMPOLINE, USER_TRAMPOLINE)

    @property
    def connection(self):
        return connections.get_connection()

    @property
    def host(self):
        return self.settings['HOST']

    @property
    def indices(self):
        return self.settings['INDICES']

    @property
    def should_fail_silently(self):
        return self.settings['OPTIONS']['fail_silently']

    @property
    def is_disabled(self):
        return self.settings['OPTIONS']['disabled']
