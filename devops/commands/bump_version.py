import typing as t

from enum import Enum
from functools import partial

from setuptools import Command

from devops.utils.os import replace_in_file
from devops.utils.repo import get_repo
from devops.utils.version import Version


class BumpType(Enum):
    major = partial(Version.bump_major)
    minor = partial(Version.bump_minor)
    micro = partial(Version.bump_micro)
    pre = partial(Version.bump_pre)
    promote = partial(Version.promote_pre)

    def __call__(self, version, **kwargs):
        return self.value(version, **kwargs)


# noinspection PyAttributeOutsideInit
class BumpVersion(Command):
    """
    PEP-440 compatible bump-version command. Computes the next version based on given bump type,
    updates the version declaration & builds a commit and a proper release tag.
    """

    # is the diff ok?
    # git commit -m "foo" -a
    # git push
    # git tag new_tag
    # git push --tags

    description = (
        "computes the next version based on given type, updates the version declaration & builds "
        "a commit and a proper release tag"
    )
    user_options = [
        ("bump=", "b", "type of the bump: major/minor/micro/pre/promote (required)"),
        ("final", "f", "should bump be already promoted to a final release (flag)"),
        ("no-commit", "c", "must not automatically build a commit (flag)"),
        ("no-tag", "t", "must not automatically make a git tag (flag)"),
    ]
    boolean_options = ["final", "no_commit", "no_tag"]

    commit_message_pattern = "Bump version: {} -> {}"
    release_notes_filepaths = ("CHANGELOG.md", "ROADMAP.md")

    def initialize_options(self):
        from devops import PROJECT_PACKAGE

        assert hasattr(PROJECT_PACKAGE, "VERSION"), "No VERSION variable declared"
        assert PROJECT_PACKAGE.VERSION, "No VERSION variable injected"
        self.package = PROJECT_PACKAGE
        self.project_init_filepath = self.package.__file__
        self.version = PROJECT_PACKAGE.VERSION
        self.bump: t.Optional[BumpType] = None
        self.final: bool = False
        self.no_commit: bool = False
        self.no_tag: bool = False

    def finalize_options(self):
        if not self.bump:
            raise ValueError(
                "`type` option is not defined; it should be one of: major/minor/micro/pre/promote"
            )
        try:
            self.bump = BumpType[self.bump]
        except KeyError:
            raise ValueError(
                "`type` option is not valid; it should be one of: major/minor/micro/pre/promote"
            )
        for option_name in self.boolean_options:
            setattr(self, option_name, bool(getattr(self, option_name, None)))

    def run(self):
        should_be_pre = not self.final
        self.next_version = self.bump(self.version, add_pre=should_be_pre)
        self.repo = get_repo()
        if self.repo.is_dirty(working_tree=False):
            raise ValueError("Can't operate on dirty index. Clean your index first.")
        self._add_release_notes()
        self._replace_version_definition()
        self._build_commit()
        self._build_tag()

    def _add_release_notes(self):
        """Looks for changes in `changelog_doc_filepath` & `roadmap_doc_filepath` files."""
        assert hasattr(self.package, "PROJECT_DIR"), "No PROJECT_DIR variable declared"
        project_dir = self.package.PROJECT_DIR
        assert project_dir, "No PROJECT_DIR variable injected"
        changed_files = [item.a_path for item in self.repo.index.diff(None)]
        for doc_filepath in self.release_notes_filepaths:
            if doc_filepath in changed_files:
                self.repo.git.add(doc_filepath)

    def _replace_version_definition(self):
        project_init_module_path = self.package.__file__
        success = replace_in_file(
            filepath=project_init_module_path,
            pattern=r"(?<=VERSION = )Version\([^)]*\)(?=\n)",
            substitute=repr(self.next_version),
        )
        if success:
            self.repo.git.add(project_init_module_path)
        else:
            raise RuntimeError(
                f"Version definition in `{project_init_module_path}` has not been found."
            )

    def _build_commit(self):
        if self.no_commit:
            return
        commit_message = self.commit_message_pattern.format(
            self.version.as_string(), self.next_version.as_string()
        )
        self.repo.index.commit(commit_message)

    def _build_tag(self):
        if not (self.no_commit or self.no_tag):
            self.repo.create_tag(self.next_version.as_git_tag())
