#!/usr/bin/env python3
import sys

from setuptools import (
    setup,
    find_packages,
)
from setuptools.command.test import test as TestCommand


PROJECT_NAME = 'python-clean-architecture'
PACKAGE_NAME = 'pca'
VERSION = (0, 0, 1)
INSTALL_REQUIRES = (
    'traitlets>=4.3.2',
    'six',
)
TEST_REQUIRE = (
    'pytest>=3.6.3',
)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def readme():
    with open('README.md') as f:
        return f.read()


if __name__ == '__main__':
    setup(
        name=PROJECT_NAME,
        version='.'.join(str(i) for i in VERSION),
        url=f'https://github.com/pcah/{PROJECT_NAME}',
        license='MIT License',
        author='lhaze',
        author_email='lhaze@lhaze.name',
        description='A framework-agnostic toolkit for Python driven by the Clean Architecture ',
        long_description_content_type='text/markdown',
        long_description=readme(),
        platforms='any',
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Operating System :: OS Independent",
            "Topic :: Software Development",
            "Intended Audience :: Developers",
            "Development Status :: 2 - Pre-Alpha"
        ],

        cmdclass={'test': PyTest},
        install_requires=INSTALL_REQUIRES,
        tests_require=TEST_REQUIRE,
        packages=find_packages(),
    )
