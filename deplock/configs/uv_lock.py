from pydantic import BaseModel, Field, computed_field
from typing import Dict, List

class UVDistInfo(BaseModel):
    url: str
    hash: str
    size: int | None = None

    @computed_field
    def dist_name(self) -> str:
        return self.url.split("/")[-1]

class UVMetadata(BaseModel):
    requires_dist: List[Dict[str, str | List[str]]] | None =  Field(
        alias="requires-dist",
        default=None,)
    requires_dev: Dict[str, List] | None =  Field(
        alias="requires-dev",
        default=None,)

class UVPackage(BaseModel):
    name: str
    version: str
    source: Dict[str, str]
    resolution_markers: List[str] | None = Field(
        alias="resolution-markers",
        default=None,
        description="Package level resolution marker")
    dependencies: List[Dict[str, str | Dict | List[str]]] | None = None
    sdist: UVDistInfo | None = None
    wheels: List[UVDistInfo] | None = None
    optional_dependencies: List[Dict[str, str]] | None = None
    dev_dependencies: List[Dict[str, str | List]] | Dict | None =  Field(
        alias="dev-dependencies",
        default=None,)
    metadata: UVMetadata | None = None

    def _get_source_url_parts(self) -> Dict[str, str]:
        if self.source is None:
            source_url_type = "UNKNOWN"
            source_url = "UNKNOWN"
        elif "editable" in self.source:
            source_url_type = "editable"
            source_url = self.source["editable"]
        elif "registry" in self.source:
            source_url_type = "registry"
            source_url = self.source["registry"]
        # if "source" in the package metadata, but its not "editable" or "registry"
        # use whatever source and value is there
        else:
            source_url_type = list(self.source.keys())[0]
            source_url = self.source[source_url_type]
        return {"source_url": source_url, "source_url_type": source_url_type}

    @computed_field
    def source_url(self) -> str:
        url_dict = self._get_source_url_parts()
        return url_dict["source_url"]

    @computed_field
    def source_url_type(self) -> str:
        url_dict = self._get_source_url_parts()
        return url_dict["source_url_type"]


class UVLockConfig(BaseModel):
    version: int | None = None
    requires_python: str | None = Field(
        alias="requires-python",
        default=None,)
    resolution_markers: List[str] | None = Field(
        alias="resolution-markers",
        default=None,)
    manifest: Dict[str, List[str]] | None = None
    package: List[UVPackage]