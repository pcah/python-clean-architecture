from setuptools import Command
from setuptools.command.sdist import sdist
from wheel.bdist_wheel import bdist_wheel


# noinspection PyAttributeOutsideInit
class DistBuild(Command):

    user_options = []
    description = "build preferred distributions (source & wheel) to publish to PyPI"

    def initialize_options(self):
        self.sdist = sdist(self.distribution)
        self.bdist_wheel = bdist_wheel(self.distribution)
        self.sdist.initialize_options()
        self.bdist_wheel.initialize_options()

    def finalize_options(self):
        self.sdist.finalize_options()
        self.bdist_wheel.finalize_options()
        self.finalized = 1

    def run(self):
        self.sdist.run()
        self.bdist_wheel.run()
