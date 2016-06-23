"""
Setup for nose-trampoline.
"""
from setuptools import setup


setup(
    name='nose_trampoline',
    entry_points={
        'nose.plugins': [
            'trampoline_setup = trampoline_setup:TrampolineSetup',
        ]
    }
)
