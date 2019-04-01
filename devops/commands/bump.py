import argparse
from distutils.cmd import Command
import sys

from twine import utils


class BumpVersion(Command):
    """
    PEP-440 compatible bump-version command.
    """
    # git status check
    # new version in pca/__init__.py
    # build release notes
    # is the diff ok?
    # git commit -m "foo" -a
    # git push
    # git tag new_tag
    # git push --tags

    def initialize_options(self):
        pass

    def finalize_options(self):
        args = sys.argv[1:]
        parser = argparse.ArgumentParser(prog="twine upload")
        parser.add_argument(
            "-r", "--repository",
            action=utils.EnvironmentDefault,
            env="TWINE_REPOSITORY",
            default="pypi",
            help="The repository (package index) to upload the package to. "
                 "Should be a section in the config file (default: "
                 "%(default)s). (Can also be set via %(env)s environment "
                 "variable.)",
        )
        parser.add_argument(
            "--repository-url",
            action=utils.EnvironmentDefault,
            env="TWINE_REPOSITORY_URL",
            default=None,
            required=False,
            help="The repository (package index) URL to upload the package to."
                 " This overrides --repository. "
                 "(Can also be set via %(env)s environment variable.)"
        )
        parser.add_argument(
            "-s", "--sign",
            action="store_true",
            default=False,
            help="Sign files to upload using GPG.",
        )
        parser.add_argument(
            "--sign-with",
            default="gpg",
            help="GPG program used to sign uploads (default: %(default)s).",
        )
        parser.add_argument(
            "-i", "--identity",
            help="GPG identity used to sign files.",
        )
        parser.add_argument(
            "-u", "--username",
            action=utils.EnvironmentDefault,
            env="TWINE_USERNAME",
            required=False,
            help="The username to authenticate to the repository "
                 "(package index) as. (Can also be set via "
                 "%(env)s environment variable.)",
        )
        parser.add_argument(
            "-p", "--password",
            action=utils.EnvironmentDefault,
            env="TWINE_PASSWORD",
            required=False,
            help="The password to authenticate to the repository "
                 "(package index) with. (Can also be set via "
                 "%(env)s environment variable.)",
        )
        parser.add_argument(
            "-c", "--comment",
            help="The comment to include with the distribution file.",
        )
        parser.add_argument(
            "--config-file",
            default="~/.pypirc",
            help="The .pypirc config file to use.",
        )
        parser.add_argument(
            "--skip-existing",
            default=False,
            action="store_true",
            help="Continue uploading files if one already exists. (Only valid "
                 "when uploading to PyPI. Other implementations may not "
                 "support this.)",
        )
        parser.add_argument(
            "--cert",
            action=utils.EnvironmentDefault,
            env="TWINE_CERT",
            default=None,
            required=False,
            metavar="path",
            help="Path to alternate CA bundle (can also be set via %(env)s "
                 "environment variable).",
        )
        parser.add_argument(
            "--client-cert",
            metavar="path",
            help="Path to SSL client certificate, a single file containing the"
                 " private key and the certificate in PEM format.",
        )
        parser.add_argument(
            "--verbose",
            default=False,
            required=False,
            action="store_true",
            help="Show verbose output."
        )
        parser.add_argument(
            "--disable-progress-bar",
            default=False,
            required=False,
            action="store_true",
            help="Disable the progress bar."
        )
        parser.add_argument(
            "dists",
            nargs="+",
            metavar="dist",
            help="The distribution files to upload to the repository "
                 "(package index). Usually dist/* . May additionally contain "
                 "a .asc file to include an existing signature with the "
                 "file upload.",
        )
        parser = argparse.ArgumentParser(prog="twine")
        parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s version {} ({})".format(
                '',
                '',
            ),
        )
        parser.add_argument(
            "command",
            choices=[],
        )
        parser.add_argument(
            "args",
            help=argparse.SUPPRESS,
            nargs=argparse.REMAINDER,
        )

        args = parser.parse_args(args)
        return args

    def run(self):
        pass
