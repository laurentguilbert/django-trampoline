"""
Init for trampoline.
"""
try:
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
