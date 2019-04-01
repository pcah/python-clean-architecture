from os import path

from devops.utils.version import Version


PROJECT_NAME = 'python-clean-architecture'
PACKAGE_NAME = 'pca'
VERSION = Version(0, 0, 2)

PACKAGE_DIR = path.dirname(__file__)
PROJECT_DIR = path.dirname(PACKAGE_DIR)
