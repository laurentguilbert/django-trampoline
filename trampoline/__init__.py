"""
Init for trampoline.
"""
from .version import __version__  # noqa

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
