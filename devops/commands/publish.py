from pathlib import Path

from setuptools import Command


class Publish(Command):

    user_options = []
    description = "publishes distributions to PyPI using `twine` library"

    distributions_glob = "dist/*"

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from twine.commands import upload

        from devops import PROJECT_PACKAGE

        assert hasattr(PROJECT_PACKAGE, "PROJECT_DIR"), "No PROJECT_DIR variable declared"
        assert PROJECT_PACKAGE.PROJECT_DIR, "No PROJECT_DIR variable injected"

        distributions = [
            path.as_posix()
            for path in Path(PROJECT_PACKAGE.PROJECT_DIR).glob(self.distributions_glob)
            if path.is_file()
        ]
        return upload.main(distributions)
