"""
Init for trampoline.
"""
from .version import __version__  # noqa

from trampoline.apps import get_trampoline_config  # noqa

default_app_config = 'trampoline.apps.TrampolineConfig'
