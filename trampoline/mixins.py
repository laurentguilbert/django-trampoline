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

    @classmethod
    def get_indexable_queryset(cls):  # pragma: no cover
        return cls.objects.all()

    @classmethod
    def get_es_doc_type(cls):  # pragma: no cover
        return cls.es_doc_type

    def is_indexable(self):
        return True

    def get_es_doc_mapping(self):
        raise NotImplementedError

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
                (index_name, content_type.pk, self.pk),
                countdown=countdown
            )
        else:
            result = es_index_object.apply((
                index_name,
                content_type.pk,
                self.pk
            ))
        return result

    def es_delete(self, async=True, index_name=None):
        if trampoline_config.is_disabled:
            return

        doc_type = self.get_es_doc_type()
        doc_type_name = doc_type._doc_type.name
        index_name = index_name or doc_type._doc_type.index

        if async:
            es_delete_doc.delay(index_name, doc_type_name, self.pk)
        else:
            es_delete_doc.apply((index_name, doc_type_name, self.pk))
