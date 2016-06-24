"""
Test settings for trampoline.
"""

DATABASES = {
    'default': {
        'NAME': 'trampoline.db',
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'trampoline',
    'tests',
)

SECRET_KEY = 'secret-key'

##################################################
#                   Trampoline                   #
##################################################

TRAMPOLINE = {
    'INDICES': {
        'foobar': {
            'models': ('tests.models.Token',)
        },
    }
}

##################################################
#                     Celery                     #
##################################################

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

from . import celery_app  # noqa
