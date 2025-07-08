from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
import platform
import sys
from typing import Any, Iterable, List, Optional, Sequence, Type, Union

from packaging.markers import Marker
import packaging.tags


@dataclass
class PythonVersion:
    major: int
    minor: int
    micro: Optional[Union[int, str]] = None

    @staticmethod
    def current_version() -> PythonVersion:
        return PythonVersion(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro
        )

    def __post_init__(self):
        self.major = int(self.major)
        self.minor = int(self.minor)
        if self.micro:
            try:
                self.micro = int(self.micro)
            except ValueError:
                assert self.micro == "*"

    def is_full_spec(self) -> bool:
        return self.micro is not None

    def major_minor_only_spec(self) -> str:
        return f"{self.major}.{self.minor}"

    def __str__(self) -> str:
        if self.micro or self.micro == 0:
            micro = f".{self.micro}"
        else:
            micro = ""
        return f"{self.major}.{self.minor}{micro}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PythonVersion):
            return False
        if self.micro and isinstance(self.micro, int):
            return (
                self.major == other.major
                and self.minor == other.minor
                and self.micro == other.micro
            )
        return self.major == other.major and self.minor == other.minor


@dataclass(frozen=True)
class EnvironmentMarkers:
    """
    Represents the allowed environment markers.

    These are used to determine when a dependency should be
    used and which distributions are compatible with the specified
    markers.
    """

    os_name: str
    sys_platform: str
    platform_machine: str
    platform_python_implementation: str
    platform_release: str
    platform_system: str
    platform_version: str
    implementation_name: str

    @property
    def implementation(self) -> str:
        if self.platform_python_implementation == "CPython":
            return "cp"
        if self.platform_python_implementation == "PyPy":
            return "pp"
        if self.platform_python_implementation == "IronPython":
            return "ip"
        if self.platform_python_implementation == "Jython":
            return "jy"
        raise ValueError(f"Unknown implementation: {self.implementation_name}")

    @classmethod
    def from_current_env(cls: Type[EnvironmentMarkers]) -> EnvironmentMarkers:
        return cls(
            os_name=os.name,
            sys_platform=sys.platform,
            platform_machine=platform.machine(),
            platform_python_implementation=platform.python_implementation(),
            platform_release=platform.release(),
            platform_system=platform.system(),
            platform_version=platform.version(),
            implementation_name=sys.implementation.name,
        )

    def __hash__(self):
        environment_hash = sha256()
        environment_hash.update(self.os_name.encode())
        environment_hash.update(self.sys_platform.encode())
        environment_hash.update(self.platform_machine.encode())
        environment_hash.update(self.platform_python_implementation.encode())
        environment_hash.update(self.platform_release.encode())
        environment_hash.update(self.platform_system.encode())
        environment_hash.update(self.platform_version.encode())
        environment_hash.update(self.implementation_name.encode())
        return int.from_bytes(environment_hash.digest(), byteorder="big")


@dataclass(frozen=True)
class PythonEnvironment:
    """
    Represents the requirements for a Python environment
    to ensure compatible distributions are used
    and Layers are placed in the correct location.
    """

    python_version: PythonVersion
    platforms: Sequence[str]
    environment_location: str
    environment_markers: EnvironmentMarkers

    @property
    def major_python(self) -> int:
        return self.python_version.major

    @property
    def minor_python(self) -> int:
        return self.python_version.minor

    @property
    def micro_python(self) -> Optional[int]:
        return self.python_version.minor

    @property
    def supported_abis(self) -> Iterable[str]:
        return [
            f"{self.environment_markers.implementation}{self.major_python}{self.minor_python}",
            "abi3",
            "none",
        ]

    @property
    def supported_platforms(self) -> Iterable[str]:
        return list(self.platforms) + ["any"]

    @property
    def site_packages(self) -> str:
        return os.path.join(
            self.environment_location,
            "lib",
            f"python{self.major_python}.{self.minor_python}",
            "site-packages",
        )

    @property
    def python_executable(self) -> str:
        return os.path.join(self.environment_location, "bin", "python")

    def supported_tags(self) -> List[packaging.tags.Tag]:
        """
        Computes the supported tags for the environment.

        The result is ordered by priority for matching
        with the tag of a distribution. For example,
        if two distributions are found to be compatible
        with the environment, the distribution that
        matches the earlier tag in the results will be used.

        Returns:
            Iterable[packaging.tags.Tag]: An ordered list of tags.
        """
        cpython_tags = packaging.tags.cpython_tags(
            python_version=(self.major_python, self.minor_python),
            abis=self.supported_abis,
            platforms=self.supported_platforms,
        )
        compatible_tags = packaging.tags.compatible_tags(
            python_version=(self.major_python, self.minor_python),
            interpreter=f"{self.environment_markers.implementation_name}{self.major_python}{self.minor_python}",
            platforms=self.supported_platforms,
        )
        return list(cpython_tags) + list(compatible_tags)

    def is_compatible_with_marker(self, marker: Marker) -> bool:
        """Check if this environment satisfies the given PEP 508 marker."""
        environment = {
            "os_name": self.environment_markers.os_name,
            "sys_platform": self.environment_markers.sys_platform,
            "platform_machine": self.environment_markers.platform_machine,
            "platform_python_implementation": self.environment_markers.platform_python_implementation,  # noqa
            "platform_release": self.environment_markers.platform_release,
            "platform_system": self.environment_markers.platform_system,
            "platform_version": self.environment_markers.platform_version,
            "implementation_name": self.environment_markers.implementation_name,
            "python_version": str(self.python_version),
            "python_full_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro or 0}",  # noqa
        }
        return marker.evaluate(environment)

    def __hash__(self):
        environment_hash = sha256()
        environment_hash.update(self.environment_location.encode())
        environment_hash.update(str(self.python_version).encode())
        platforms = "|".join(sorted(self.platforms))
        environment_hash.update(platforms.encode())

        hashed_env_markers = hash(self.environment_markers)
        environment_hash.update(
            hashed_env_markers.to_bytes(
                (hashed_env_markers.bit_length() + 7) // 8, byteorder="big"
            )
        )
        return int.from_bytes(environment_hash.digest(), byteorder="big")
