#!/usr/bin/env python3
from setuptools import (
    setup,
    find_packages,
)

import devops
import pca


def readme():
    with open('README.md') as f:
        return f.read()


if __name__ == '__main__':
    devops.PROJECT_PACKAGE = pca
    setup(
        name=pca.PROJECT_NAME,
        version=pca.VERSION.as_string(),
        url=f'https://github.com/pcah/{pca.PROJECT_NAME}',
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

        cmdclass=devops.commands.ALL,
        install_requires=[
            "dataclasses; python_version < '3.7'",
            "gitpython",
            'twine',
            'virtualenv',
            'wheel',
        ],
        tests_require=['tox'],
        packages=find_packages(),
    )
