from distutils.cmd import Command
from pathlib import Path


class Publish(Command):

    user_options = []
    distributions_glob = 'dist/*'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from twine.commands import upload
        from devops import PROJECT_DIR
        distributions = [
            path.as_posix() for path in Path(PROJECT_DIR).glob(self.distributions_glob)
            if path.is_file()
        ]
        return upload.main(distributions)
