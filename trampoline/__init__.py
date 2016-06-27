"""
Init for trampoline.
"""
__version__ = '1.0'
__license__ = 'MIT License'
__author__ = 'Laurent Guilbert'
__email__ = 'laurent@guilbert.me'
__url__ = 'https://github.com/laurentguilbert/django-trampoline'

try:
    # Try to import AppConfig to check if this feature is available.
    from django.apps import AppConfig  # noqa
    default_app_config = 'trampoline.apps.TrampolineConfig'

    def get_trampoline_config():
        from django.apps import apps
        return apps.get_app_config('trampoline')
except ImportError:
    from trampoline.apps import TrampolineConfig
    app_config = TrampolineConfig()
    app_config.ready()

    def get_trampoline_config():
        return app_config
