import datetime
from pydantic import Field, model_validator, BaseModel
from typing import Any, Dict, List, Literal
from typing_extensions import Self

from deplock.exceptions import PackageDistributionValidationError, MissingRequiredPackageFieldError

# wheels and sdists
# sdist: mutually-exclusive with packages.vcs, packages.directory, and packages.archive
# whls: mutually-exclusive with packages.vcs, packages.directory, and packages.archive
class Wheels(BaseModel):
    class_type: Literal["Wheels"] = "Wheels"
    name: str | None = Field(default=None,
                             description="The file name of the Binary distribution format file." )
    upload_time: datetime.datetime | None = Field(default=None,
                                                  alias="upload-time",
                                                  description="The time the file was uploaded."
                                                              "The date and time MUST be recorded in UTC.")
    url: str = Field(description="The URL to the source tree.")
    path: str | None = Field(default=None,
                             description="The path to the local directory of the source tree."
                                         "If a relative path is used it MUST be relative to the location of this file."
                                         "If the path is relative it MAY use POSIX-style path separators explicitly for portability.")
    size: int | None = Field(default=None,
                             description="The size of the archive file."
                                         "Tools SHOULD provide the file size when reasonably possible (e.g. the file size is available via the Content-Length header from a HEAD HTTP request).")
    hashes: Dict[str, str] | None = Field(default=None,
                                          description="A table listing known hash values of the file where the key is the hash algorithm and the value is the hash value."
                                                      "The table MUST contain at least one entry."
                                                      "Hash algorithm keys SHOULD be lowercase."
                                                      "At least one secure algorithm from hashlib.algorithms_guaranteed SHOULD always be included (at time of writing, sha256 specifically is recommended.")
    @model_validator(mode="after")
    def check_url_or_path(self) -> Self:
        if not self.url and not self.path:
            raise MissingRequiredPackageFieldError("Wheels Package type must have a `url` or `path` field.")
        return self

class SDist(BaseModel):
    class_type: Literal["SDist"] = "SDist"
    name: str | None = Field(default=None,
                             description="The file name of the Binary distribution format file.")
    upload_time: datetime.datetime | None = Field(default=None,
                                                  alias="upload-time",
                                                  description="The time the file was uploaded."
                                                              "The date and time MUST be recorded in UTC.")
    url: str = Field(description="The URL to the source tree.")
    path: str | None = Field(default=None,
                             description="The path to the local directory of the source tree."
                                  "If a relative path is used it MUST be relative to the location of this file."
                                  "If the path is relative it MAY use POSIX-style path separators explicitly for portability.")
    size: int | None = Field(default=None,
                             description="The size of the archive file."
                                         "Tools SHOULD provide the file size when reasonably possible (e.g. the file size is available via the Content-Length header from a HEAD HTTP request).")
    hashes: Dict[str, str] | None = Field(default=None,
                                          description="A table listing known hash values of the file where the key is the hash algorithm and the value is the hash value."
                                                      "The table MUST contain at least one entry."
                                                      "Hash algorithm keys SHOULD be lowercase."
                                                      "At least one secure algorithm from hashlib.algorithms_guaranteed SHOULD always be included (at time of writing, sha256 specifically is recommended.")
    @model_validator(mode="after")
    def check_url_or_path(self) -> Self:
        if not self.url and not self.path:
            raise MissingRequiredPackageFieldError("SDist Package type must have a `url` or `path` field.")
        return self

class VCS(BaseModel):
    # mutually-exclusive with packages.directory, packages.archive, packages.sdist, and packages.wheels
    class_type: Literal["VCS"] = "VCS"
    type: str = Field(description="The type of version control system used.packages")

    url: str | None = Field(default=None,
                            description="The URL to the source tree.")

    path: str | None = Field(default=None,
                             description="The path to the local directory of the source tree."
                                  "If a relative path is used it MUST be relative to the location of this file."
                                  "If the path is relative it MAY use POSIX-style path separators explicitly for portability.")

    requested_revision: str | None = Field(alias="requested-revision",
                                           default=None,
                                           description="The branch/tag/ref/commit/revision/etc. that the user requested."
                                                       "This is purely informational and to facilitate writing the Direct "
                                                       "URL Data Structure; it MUST NOT be used to checkout the repository")

    commit_id: str = Field(alias="commit-id",
                           description="The exact commit/revision number that is to be installed."
                                       "If the VCS supports commit-hash based revision identifiers, such a commit-hash MUST be used as the commit ID in order to reference an immutable version of the source code.")
    subdirectory: str | None = Field(default=None,
                                     description="The subdirectory within the source tree where the project root of the project is (e.g. the location of the pyproject.toml file)."
                                                 "The path MUST be relative to the root of the source tree structure.")
    @model_validator(mode="after")
    def check_url_or_path(self) -> Self:
        if not self.url and not self.path:
            raise MissingRequiredPackageFieldError("VCS Package type must have a `url` or `path` field.")
        return self

class Directory(BaseModel):
    # mutually-exclusive with packages.vcs, packages.archive, packages.sdist, and packages.wheels
    class_type: Literal["Directory"] = "Directory"
    path: str = Field(description="The local directory where the source tree is."
                                  "If the path is relative it MUST be relative to the location of the lock file."
                                  "If the path is relative it MAY use POSIX-style path separators for portability.")
    editable: bool | None = Field(default=False,
                                  description="A flag representing whether the source tree was an editable install at lock time."
                                              "Installer MAY choose to ignore this flag if user actions or context would make an "
                                              "editable install unnecessary or undesirable (e.g. a container image that will not be mounted for "
                                              "development purposes but instead deployed to production where it would be treated at read-only).")
    subdirectory: str | None = Field(default=None,
                                     description="The subdirectory within the source tree where the project root of the project is (e.g. the location of the pyproject.toml file)."
                                                 "The path MUST be relative to the root of the source tree structure.")



class Archive(BaseModel):
    class_type: Literal["Archive"] = "Archive"
    url: str | None = Field(default=None,
                            description="The URL to the source tree.")

    path: str | None = Field(default=None,
                             description="The path to the local directory of the source tree."
                                  "If a relative path is used it MUST be relative to the location of this file."
                                  "If the path is relative it MAY use POSIX-style path separators explicitly for portability.")

    size: int | None = Field(default=None,
                             description="The size of the archive file."
                                         "Tools SHOULD provide the file size when reasonably possible (e.g. the file size is available via the Content-Length header from a HEAD HTTP request).")
    upload_time: datetime.datetime | None = Field(alias="upload-time",
                                                  default=None,
                                                  description="The time the file was uploaded."
                                                              "The date and time MUST be recorded in UTC.")

    hashes: Dict[str, str] = Field(description="A table listing known hash values of the file where the key is the hash algorithm and the value is the hash value."
                                                      "The table MUST contain at least one entry."
                                                      "Hash algorithm keys SHOULD be lowercase."
                                                      "At least one secure algorithm from hashlib.algorithms_guaranteed SHOULD always be included (at time of writing, sha256 specifically is recommended.")

    subdirectory: str | None = Field(default=None,
                                     description="The subdirectory within the source tree where the project root of the project is (e.g. the location of the pyproject.toml file)."
                                                 "The path MUST be relative to the root of the source tree structure.")
    @model_validator(mode="after")
    def check_url_or_path(self) -> Self:
        if not self.url and not self.path:
            raise MissingRequiredPackageFieldError("Archive Package type must have a `url` or `path` field.")
        return self


class Package(BaseModel):
    name: str = Field(description="The name of the package normalized.",)
    version: str | None = Field(
        default=None,
        description="The version of the package."
                    "The version SHOULD be specified when the version is known to be stable (i.e. when an sdist or wheels are specified)."
                    "The version MUST NOT be included when it cannot be guaranteed to be consistent with the code used (i.e. when a source tree is used)..",
    )
    marker: str | None = Field(
        default=None,
        description="The environment marker which specify when the package should be installed.",)
    requires_python: str | None = Field(
        alias="requires-python",
        default=None,
        description="Holds the Version specifiers for Python version compatibility for the package.",
    )
    dependencies: List[Dict[str, Any]] | None = Field(
        default=None,
        description="Records the other entries in [[packages]] which are direct dependencies of this package."
                    "Each entry is a table which contains the minimum information required to tell which other "
                    "package entry it corresponds to where doing a key-by-key comparison would find the appropriate "
                    "package with no ambiguity (e.g. if there are two entries for the spam package, then you can "
                    "include the version number like {name = 'spam', version = '1.0.0('}, or by source like "
                    "{name =')spam', vcs = { url = '...('})."
                    "Tools MUST NOT use this information when doing installation; it is purely informational for auditing purposes.")
    index: str | None = Field(
        default=None,
        description="The base URL for the package index from Simple repository API where the sdist and/or wheels were found (e.g. https://pypi.org/simple/)."
                    "When possible, this SHOULD be specified to assist with generating software bill of materials – aka SBOMs – and to assist in finding a file if a URL ceases to be valid.)"
                    "Tools MAY support installing from an index if the URL recorded for a specific file is no longer valid (e.g. returns a 404 HTTP error code).")

    sdist_info: List[SDist] | None = Field(alias="sdist", default=None)
    wheels_info: List[Wheels] | None = Field(alias="wheels", default=None)
    vcs_info: List[VCS] | None = Field(alias="vcs", default=None)
    archive_info: List[Archive] | None = Field(alias="archive", default=None)
    directory_info: List[Directory] | None = Field(alias="directory", default=None)

    @model_validator(mode="after")
    def check_dists_types(self) -> Self:
        # TODO: more details on exactly which package source types are clashing

        _vcs = "VCS" if self.vcs_info else None
        _directory = "Directory" if self.directory_info else None
        _archive = "Archive" if self.archive_info else None
        _sdist = "SDist" if self.sdist_info else None
        _wheels = "Wheels" if self.wheels_info else None

        dist_sources = ", ".join([i for i in [_vcs, _directory, _archive, _sdist, _wheels] if i is not None])

        if self.vcs_info and any(
            [
                self.directory_info is not None,
                self.archive_info is not None,
                self.sdist_info is not None,
                self.wheels_info is not None,
            ]
        ):
            raise PackageDistributionValidationError(
                "Cannot have mix of package source types."
                f"Found the following package source types: {dist_sources}"
            )

        if self.directory_info and any(
            [
                self.vcs_info is not None,
                self.archive_info is not None,
                self.sdist_info is not None,
                self.wheels_info is not None,
            ]
        ):
            raise PackageDistributionValidationError(
                "Cannot have mix of package source types."
                f"Found the following package source types: {dist_sources}"
            )

        if self.sdist_info and any(
            [
                self.vcs_info is not None,
                self.archive_info is not None,
                self.directory_info is not None,
            ]
        ):
            raise PackageDistributionValidationError(
                "Cannot have mix of package source types."
                f"Found the following package source types: {dist_sources}"
            )

        if self.wheels_info and any(
            [
                self.vcs_info is not None,
                self.archive_info is not None,
                self.directory_info is not None,
            ]
        ):
            raise PackageDistributionValidationError(
                "Cannot have mix of package source types."
                f"Found the following package source types: {dist_sources}"
            )

        return self

    attestation_identities: Any | None = Field(alias="attestation-identities",
                                               default=None,
                                               description="")
    tool: Dict[str, str] | None = Field(
        default=None,
        description="Similar usage as that of the [tool] table from the pyproject.toml specification, "
                    "but at the package version level instead of at the lock file level (which is also available via [tool])."
                    "Data recorded in the table MUST be disposable (i.e. it MUST NOT affect installation).")
