"""
Setup for trampoline.
"""
import sys

from setuptools import find_packages
from setuptools import setup

exec(open('trampoline/version.py').read())

install_requires = [
    'celery',
    'elasticsearch_dsl>=2.0.0,<3.0.0',
    'tqdm',
    'six',
]
if sys.version_info.major == 2:
    install_requires.append('futures')

setup(
    name='django-trampoline',
    version=__version__,  # noqa
    keywords='django, elasticsearch',
    author='Laurent Guilbert',
    author_email='laurent@guilbert.me',
    url='https://github.com/laurentguilbert/django-trampoline',
    description="No-frills Elasticsearch's wrapper for your Django project.",
    license='MIT License',
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
    install_requires=install_requires,
    entry_points={
        'nose.plugins': (
            'trampoline_setup = nose_plugins:TrampolineSetup',
        )
    },
)
