"""
Setup for trampoline.
"""
from setuptools import find_packages
from setuptools import setup

import trampoline

setup(
    name='django-trampoline',
    version=trampoline.__version__,
    keywords='django, elasticsearch',
    author=trampoline.__author__,
    author_email=trampoline.__email__,
    url=trampoline.__url__,
    description="No-frills Elasticsearch's wrapper for your Django project.",
    license=trampoline.__license__,
    classifiers=(
        'Framework :: Django',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    install_requires=(
        'celery',
        'elasticsearch_dsl>=2.0.0,<3.0.0',
        'six',
    )
)
