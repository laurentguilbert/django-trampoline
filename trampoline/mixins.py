"""
Mixins for trampoline.
"""
from django.contrib.contenttypes.models import ContentType

from trampoline import get_trampoline_config
from trampoline.tasks import es_delete_doc
from trampoline.tasks import es_index_object

trampoline_config = get_trampoline_config()


class ESIndexableMixin(object):
    """
    Provide the required methods and attributes to index django models.
    """
    es_doc_type = None
    es_auto_doc_type_mapping = False

    @classmethod
    def get_indexable_queryset(cls):  # pragma: no cover
        return cls._default_manager.all()

    @classmethod
    def get_es_doc_type(cls):  # pragma: no cover
        return cls.es_doc_type

    def is_indexable(self):
        return True

    def is_index_update_needed(self):
        return True

    def get_es_doc_mapping(self):
        if self.es_auto_doc_type_mapping is True:
            return self.get_es_auto_doc_mapping()
        raise NotImplementedError

    def get_es_auto_doc_mapping(self):
        """
        Automatically map values from the model to the doc_type.
        If a field is not present on the model, a method "prepare_{field}"
        must be implemented on the doc_type.
        """
        doc_type = self.es_doc_type()
        for field in doc_type._doc_type.mapping:
            prep_func = getattr(doc_type, 'prepare_{0}'.format(field), None)
            if prep_func is not None and callable(prep_func):
                value = prep_func(self)
            elif hasattr(self, field):
                value = getattr(self, field, None)
            else:
                raise NotImplementedError(
                    u"Field {0} is not on {1} and {2} doesn't implement a "
                    "\"prepare_{3}\" method."
                    .format(field, self.__class__, doc_type.__class__, field)
                )
            setattr(doc_type, field, value)
        return doc_type

    def get_es_doc(self):
        if not self.pk:
            return None
        doc_type = self.get_es_doc_type()
        index_name = doc_type._doc_type.index
        doc = doc_type.get(index=index_name, id=self.pk, ignore=404)
        return doc

    def es_index(self, async=True, countdown=0, index_name=None):
        if trampoline_config.is_disabled:
            return

        doc_type = self.get_es_doc_type()
        index_name = index_name or doc_type._doc_type.index

        content_type = ContentType.objects.get_for_model(self)
        if async:
            result = es_index_object.apply_async(
                args=(index_name, content_type.pk, self.pk),
                countdown=countdown,
                queue=trampoline_config.celery_queue
            )
        else:
            if trampoline_config.should_fail_silently:
                result = es_index_object.apply(
                    args=(index_name, content_type.pk, self.pk)
                )
            else:  # pragma: no cover
                result = es_index_object.run(
                    index_name,
                    content_type.pk,
                    self.pk
                )
        return result

    def es_delete(self, async=True, index_name=None):
        if trampoline_config.is_disabled:
            return

        doc_type = self.get_es_doc_type()
        doc_type_name = doc_type._doc_type.name
        index_name = index_name or doc_type._doc_type.index
        using = doc_type._doc_type.using

        if async:
            es_delete_doc.delay(index_name, doc_type_name, self.pk, using)
        else:
            es_delete_doc.apply((index_name, doc_type_name, self.pk, using))
