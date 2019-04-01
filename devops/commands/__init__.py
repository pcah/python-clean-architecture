from .dist_build import DistBuild
from .publish import Publish
from .test import PyTest


ALL = {
    'test': PyTest,
    'dist_build': DistBuild,
    'publish': Publish,
}
