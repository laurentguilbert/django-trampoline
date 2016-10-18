"""
Base management command for trampoline.
"""
from __future__ import print_function
from optparse import make_option
import contextlib
import sys
import traceback

from tqdm import tqdm

import six
import time

from django.core.management.base import BaseCommand

from trampoline import get_trampoline_config


class DummyTqdmFile(object):
    file = None

    def __init__(self, file):
        self.file = file

    def write(self, x):
        if len(x.rstrip()) > 0:
            tqdm.write(x, file=self.file)


@contextlib.contextmanager
def stdout_redirect_to_tqdm():
    save_stdout = sys.stdout
    try:
        sys.stdout = DummyTqdmFile(sys.stdout)
        yield save_stdout
    except Exception as exc:  # pragma: no cover
        raise exc
    finally:
        sys.stdout = save_stdout


class ESBaseCommand(BaseCommand):
    required_options = []

    options = {
        'index_name': make_option(
            '--index',
            '-i',
            dest='index_name',
            default=None,
            help="Name of the index."
        ),
        'target_name': make_option(
            '--target',
            '-t',
            dest='target_name',
            default=None,
            help="Name of the target index."
        ),
        'using': make_option(
            '--using',
            '-u',
            dest='using',
            default='default',
            help="Connection name."
        ),
        'async': make_option(
            '--async',
            dest='async',
            action='store_true',
            default=False,
            help="Async indexing."
        ),
    }

    option_list = BaseCommand.option_list + (
        make_option(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help=(
                "Run the command in dry run mode without actually changing "
                "anything."
            )
        ),
        make_option(
            '--yes',
            action='store_true',
            dest='yes',
            default=False,
            help="Bypass the command line's verification."
        ),
    )

    def handle(self, *args, **options):
        self.trampoline_config = get_trampoline_config()
        try:
            self.parse_options(**options)
            self.run(*args, **options)
        except Exception as exc:
            if options.get('traceback', False):
                traceback.print_exc()
            self.print_error(repr(exc))
            sys.exit(1)

    def parse_options(self, **options):
        for required_option in self.required_options:
            if options.get(required_option) is None:
                self.print_error(u"{0} is required (use -h for help).".format(
                    required_option))
                sys.exit(1)

        for key, value in six.iteritems(options):
            setattr(self, key, value)

        try:
            self.verbosity = int(self.verbosity)
        except ValueError:
            self.verbosity = 1

    ##################################################
    #                     Print                      #
    ##################################################

    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    DIM = '\033[2m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

    def confirm(self, message):  # pragma: no cover
        if self.yes:
            return True
        message += u" [Y/n]"
        self.print_warning(message)
        try:
            choice = raw_input()
        except NameError:
            choice = input()
        if choice != 'Y':
            self.print_error("Operation canceled.")
            sys.exit(1)

    def print_normal(self, message, verbosity=1):
        if self.verbosity >= verbosity:
            print(message)

    def print_info(self, message, verbosity=1):
        if self.verbosity >= verbosity:
            print(u"{0}{1}{2}".format(self.BLUE, message, self.RESET))

    def print_success(self, message, verbosity=1):
        if self.verbosity >= verbosity:
            print(u"{0}{1}{2}".format(self.GREEN, message, self.RESET))

    def print_error(self, message):
        print(
            u"{0}{1}{2}".format(self.RED, message, self.RESET),
            file=sys.stderr
        )

    def print_warning(self, message):  # pragma: no cover
        print(u"{0}{1}{2}".format(self.YELLOW, message, self.RESET))
