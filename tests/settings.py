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

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'trampoline.tasks': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

SECRET_KEY = 'secret-key'

##################################################
#                   Trampoline                   #
##################################################

TRAMPOLINE = {
    'INDICES': {
        'foobar': {
            'models': [
                'tests.models.Token',
                # Make sure only one doc_type is created.
                'tests.models.Token',
                'tests.models.Person',
            ]
        },
    },
    'OPTIONS': {
        'disabled': False,
        'fail_silently': True,
    },
}

##################################################
#                     Celery                     #
##################################################

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

from . import celery_app  # noqa
