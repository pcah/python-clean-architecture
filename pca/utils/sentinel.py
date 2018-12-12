"""
Sentinel class for immutables individuals with useful reprs.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Sentinel:
    name: str
    module: str = None
