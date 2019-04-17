import typing as t


class Version:
    """
    Representation of the package version in the sense of PEP 440 and a bit of
    the semantic versioning.

    https://www.python.org/dev/peps/pep-0440/
    https://semver.org/
    """
    # We can't use either dataclass package nor dataclass builtin as there is a Py36
    # compatibility, and the code is interpreted during setup.py, long before the package can
    # install its dependencies.

    major: int
    minor: int
    micro: t.Optional[int] = None
    pre_phase: t.Optional[str] = None
    pre_number: t.Optional[int] = None
    # currently not supporting: epochs, post-releases nor dev-releases

    initial_pre_phase: t.ClassVar[str] = 'a'
    initial_pre_number: t.ClassVar[int] = 0
    pre_phase_sequence: t.ClassVar[t.Dict[str, str]] = {
        'a': 'b',
        'b': 'rc',
        'rc': None,
    }

    @property
    def pre(self):
        return None if self.pre_phase is None \
            else f'{self.pre_phase}{self.pre_number}'

    def __init__(self, major, minor, micro=None, pre_phase=None, pre_number=None):
        self.major = major
        self.minor = minor
        self.micro = micro
        self.pre_phase = {
            'a': 'a',
            'alpha': 'a',
            'b': 'b',
            'beta': 'b',
            'rc': 'rc',
            'c': 'rc',
            'pre': 'rc',
            'preview': 'rc',
            None: None,
        }[pre_phase]
        self.pre_number = pre_number

    def __eq__(self, other):
        return isinstance(other, Version) and other.__dict__ == self.__dict__

    def __repr__(self):
        """Self-representation of the instances"""
        pre_release = "" if self.pre_phase is None else \
            f", {repr(self.pre_phase)}, {self.pre_number}"
        return (
            f'{self.__class__.__name__}('
            f'{self.major}, '
            f'{self.minor}'
            f'{"" if self.micro is None and not pre_release else f", {self.micro}"}'
            f'{pre_release}'
            ')'
        )

    def as_release(self) -> t.Sequence[int]:
        return (self.major, self.minor) if self.micro is None \
            else (self.major, self.minor, self.micro)

    def as_string(self) -> str:
        return f"{'.'.join(str(i) for i in self.as_release())}{self.pre or ''}"

    def as_git_tag(self) -> str:
        return f"v{self.as_string()}"

    def bump_major(self, add_pre=True):
        assert self.pre_phase is None, \
            "You can't bump major without promoting the version to final"
        return self.__class__(
            major=self.major + 1,
            minor=0,
            micro=None if self.micro is None else 0,
            pre_phase=self.initial_pre_phase if add_pre else None,
            pre_number=self.initial_pre_number if add_pre else None,
        )

    def bump_minor(self, add_pre=True) -> 'Version':
        assert self.pre_phase is None, \
            "You can't bump minor without promoting the version to final"
        return self.__class__(
            major=self.major,
            minor=self.minor + 1,
            micro=None if self.micro is None else 0,
            pre_phase=self.initial_pre_phase if add_pre else None,
            pre_number=self.initial_pre_number if add_pre else None,
        )

    def bump_micro(self, add_pre=False) -> 'Version':
        assert self.pre_phase is None, \
            "You can't bump micro without promoting the version to final"
        return self.__class__(
            major=self.major,
            minor=self.minor,
            micro=self.micro + 1 if self.micro else 1,
            pre_phase=None,
            pre_number=None,
        )

    def bump_pre(self, add_pre=None) -> 'Version':
        assert self.pre_phase is not None, \
            "You can't bump pre release the version that is final"
        return self.__class__(
            major=self.major,
            minor=self.minor,
            micro=self.micro,
            pre_phase=self.pre_phase,
            pre_number=self.pre_number + 1,
        )

    def promote_pre(self, add_pre=None) -> 'Version':
        assert self.pre_phase is not None, \
            "You can't promote the version that is not a pre release"
        phase = self.pre_phase_sequence[self.pre_phase]
        return self.__class__(
            major=self.major,
            minor=self.minor,
            micro=self.micro,
            pre_phase=phase,
            pre_number=None if phase is None else self.initial_pre_number,
        )
