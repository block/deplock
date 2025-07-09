from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class PythonRequirement:
    """
    Represents an external specification for a Python package.

    Attributes:
        name: The name of the package.
        version: The version of the package.
        fingerprint: The sha256 hash of a distribution for
            the package.
        index_url: The URL of the package index to use when
            attempting to download the package. Pip will use
            the configuration locally or from an environment
            variable if not provided.
    """

    name: str
    version: str
    fingerprint: Optional[str]
    index_url: Optional[str]

    def __str__(self):
        return f"{self.name}=={self.version}"


@dataclass(frozen=True)
class LocalPythonRequirement(PythonRequirement):
    """
    Represents a Python requirement that references
    a distribution that needs to be built from a
    local directory.
    """

    directory: Path
