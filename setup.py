"""
Setup for trampoline.
"""
from setuptools import find_packages
from setuptools import setup


setup(
    name='django-trampoline',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    install_requires=(
        'celery',
        'elasticsearch_dsl>=2.0.0,<3.0.0',
        'six',
    )
)
