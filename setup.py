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


class PyTest(TestCommand):

    def run_tests(self):
        from tox.session import main
        errno = main(sys.argv[2:])
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
        description='A Python toolkit for applications driven by the Clean Architecture',
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
        install_requires=['virtualenv'],
        tests_require=['tox'],
        packages=find_packages(),
    )
