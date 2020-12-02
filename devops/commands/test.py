from setuptools.command.test import test
import sys


class PyTest(test):
    def run_tests(self):
        from tox.session import main

        errno = main(sys.argv[2:])
        sys.exit(errno)
