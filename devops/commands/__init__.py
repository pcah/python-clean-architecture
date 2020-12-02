from .bump_version import BumpVersion
from .dist_build import DistBuild
from .publish import Publish
from .test import PyTest


ALL = {
    "test": PyTest,
    "bump_version": BumpVersion,
    "dist_build": DistBuild,
    "publish": Publish,
}
