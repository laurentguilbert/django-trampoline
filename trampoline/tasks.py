"""
Celery tasks for trampoline.
"""
from django.contrib.contenttypes.models import ContentType

from celery import shared_task

from trampoline import get_trampoline_config

trampoline_config = get_trampoline_config()


@shared_task
def es_index_object(index_name, content_type_id, object_id):
    """
    Index any object based the methods defined by EsIndexableMixin.
    """
    content_type = ContentType.objects.get_for_id(content_type_id)
    obj = content_type.get_object_for_this_type(pk=object_id)
    doc = obj.get_es_doc_mapping()
    doc.meta.id = obj.pk
    doc.save(index=index_name)


@shared_task
def es_delete_doc(index_name, doc_type_name, doc_id):
    """
    Delete a document from the index.
    """
    trampoline_config.connection.delete(
        index=index_name,
        doc_type=doc_type_name,
        id=doc_id
    )
