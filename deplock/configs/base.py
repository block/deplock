from pydantic import AfterValidator, Field, BaseModel
from typing import Annotated, List

from deplock.configs._validators import is_float_string
from deplock.configs.packages import Package

class PylockConfig(BaseModel):
    lock_version: Annotated[str, AfterValidator(is_float_string)] = Field(
        alias="lock-version",
        description="Record the file format version that the file adheres to.",
    )
    environments: List[str] | None = Field(
        default=None,
        description="A list of Environment Markers for which the lock file is considered compatible with.",
    )
    requires_python: str | None = Field(
        alias="requires-python",
        default=None,
        description="Specifies the Requires-Python for the minimum Python version "
                    "compatible for any environment supported by the lock file "
                    "(i.e. the minimum viable Python version for the lock file).",
    )
    extras: List[str] | None = Field(
        default=[],
        description="The list of extras supported by this lock file."
                    " Lockers MAY choose to not support writing lock files that support extras and dependency groups (i.e. tools may only support exporting a single-use lock file)."
                    "Tools supporting extras MUST also support dependency groups."
                    "Tools should explicitly set this key to an empty array to signal that the inputs used to generate the lock file had no extras (e.g. a pyproject.toml file had no [project.optional-dependencies] table), signalling that the lock file is, in effect, multi-use even if it only looks to be single-use."
    )

    dependency_groups: List[str] | None = Field(
        alias="dependency-groups",
        default=[],
        description="The list of Dependency Groups publicly supported by this lock file (i.e. dependency groups users are expected to be able to specify via a tool’s UI)."
                    "Lockers MAY choose to not support writing lock files that support extras and dependency groups (i.e. tools may only support exporting a single-use lock file)."
                    "Tools supporting dependency groups MUST also support extras."
                    "Tools SHOULD explicitly set this key to an empty array to signal that the inputs used to generate the lock file had no dependency groups (e.g. a pyproject.toml file had no [dependency-groups] table), signalling that the lock file is, in effect, multi-use even if it only looks to be single-use.",
    )
    default_groups: List[str] | None = Field(
        alias="default-groups",
        default=[],
        description="The name of synthetic dependency groups to represent what should be installed by default (e.g. what project.dependencies implicitly represents)."
                    "Meant to be used in situations where packages.marker necessitates such a group to exist."
                    "The groups listed by this key SHOULD NOT be listed in dependency-groups as the groups are not meant to be directly exposed to users by name but instead via an installer’s UI.")

    created_by: str = Field(
        alias="created-by",
        description = "Records the name of the tool used to create the lock file."
                      "Tools MAY use the [tool] table to record enough details that it can be inferred what inputs were used to create the lock file."
                      "Tools SHOULD record the normalized name of the tool if it is available as a Python package to facilitate finding the tool.",
    )
    packages: List[Package] = Field(
        description = "The packages included in the lock file.",
    )