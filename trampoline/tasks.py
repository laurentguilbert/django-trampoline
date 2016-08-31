"""
Celery tasks for trampoline.
"""
import logging

from django.contrib.contenttypes.models import ContentType

from celery import shared_task

from trampoline import get_trampoline_config


logger = logging.getLogger(__name__)
trampoline_config = get_trampoline_config()


@shared_task
def es_index_object(index_name, content_type_id, object_id):
    """
    Index objects based on the methods defined by EsIndexableMixin.
    """
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
        doc = obj.get_es_doc_mapping()
        doc.meta.id = obj.pk
        doc.save(index=index_name)
    except:
        if trampoline_config.should_fail_silently:
            logger.exception("Exception occured while indexing object.")
            return False
        else:
            raise
    return True


@shared_task
def es_delete_doc(index_name, doc_type_name, doc_id):
    """
    Delete a document from the index.
    """
    try:
        trampoline_config.connection.delete(
            index=index_name,
            doc_type=doc_type_name,
            id=doc_id,
            ignore=404,
        )
    except:
        if trampoline_config.should_fail_silently:
            logger.exception("Exception occured while deleting document.")
            return False
        else:
            raise
    return True
