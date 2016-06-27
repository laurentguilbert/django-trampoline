# Trampoline

[![Build Status](https://travis-ci.org/laurentguilbert/django-trampoline.svg?branch=develop)](https://travis-ci.org/laurentguilbert/django-trampoline)

Trampoline provides you with tools to easily setup, manage and index your Django models in Elasticsearch. It uses **celery** and is heavily reliant on **elasticsearch_dsl**.

It was designed to allow re-indexing of your documents without any downtime by using intermediary indices along with aliases.

## Settings

Add `trampoline` to your `INSTALLED_APPS`.

Define the setting:
```python
TRAMPOLINE = {
  'HOST': 'localhost',
  'INDICES': {
    'index_name': {
      'models': (
        'app_name.models.ModelName',
      ),
    }
  },
}
```

## ESIndexableMixin

In order to make your model indexable you must make it inherit from `ESIndexableMixin` and implement a few things.

#### es_doc_type (required)

Set the attribute `es_doc_type` with the `DocType` used to serialize your model in Elasticsearch.

#### get_es_doc_mapping (required)

```python
def get_es_doc_mapping(self):
    doc_type = self.es_doc_type()
    doc_type.foo = self.foo
    doc_type.bar = self.bar
    return doc_type
```

Return an instance of `es_doc_type` mapped with your current model instance.

#### is_indexable (optional)

```python
def is_indexable(self):
    return True
```

Tell whether a particular instance of the model should be indexed or skipped (defaults to true).

#### get_indexable_queryset (optional)

```python
@classmethod
def get_indexable_queryset(cls):
    return []
```

Return the list of contents that should be indexed for this model using the command `es_create_documents()` defined bellow. Make sure you don't forget the `classmethod` decorator.

## Management commands

All management commands accept the following arguments:
- **--help**: Display an help message and the available arguments for the command.
- **--dry-run**: Run the command in dry run mode without actually changing anything.
- **--verbosity**: 0 to 3 from least verbose to the most. Default to 1.

### es_create_index

Create a new index based on its definition inside `ES_SETTINGS`.

Arguments:
- **--index**: Name of the index as defined in the settings.
- **--target** *(optional)*: Name of the actual index created.

If **target** is not provided a unique name will be generated by appending the current timestamp to **index**.

### es_delete_index

Delete an index along with all the documents in it.

Arguments:
- **index**: Name of the index.
- **--yes** *(optional)*:  Bypass the command line's verification.

### es_create_alias

Create an alias from one index name to the other.

Arguments:
- **--index**: Name of the index as defined in the settings.
- **--target**: Name of the actual index.

### es_delete_alias

Delete an alias from one index name to the other.

Arguments:
- **--index**: Name of the index as defined in the settings.
- **--target**: Name of the actual index.
- **--yes** *(optional)*:  Bypass the command line's verification.

### es_create_documents

Create documents based on the method `get_indexable_queryset()` on the related models.

Arguments:
- **--index**: Name of the index as defined in the settings.
- **--target** *(optional)*: Name of the actual index.

**target** defaults to **index** if not provided.
