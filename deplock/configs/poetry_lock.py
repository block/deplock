from pydantic import BaseModel, Field, computed_field
from typing import Dict, List, Optional

class PoetryFile(BaseModel):
    file: str
    hash: str

class PoetrySource(BaseModel):
    type: Optional[str] = None
    url: Optional[str] = None
    reference: Optional[str] = None

class PoetryDependency(BaseModel):
    name: str
    constraint: Optional[str] = None
    optional: Optional[bool] = False
    python_versions: Optional[str] = None
    marker: Optional[str] = None

class PoetryPackage(BaseModel):
    name: str
    version: str
    category: str = "main"
    optional: bool = False
    python_versions: Optional[str] = None
    files: List[PoetryFile] = []
    source: Optional[PoetrySource] = None
    dependencies: List[PoetryDependency] = []

class PoetryLockMetadata(BaseModel):
    lock_version: str
    python_versions: Optional[str] = None
    content_hash: Optional[str] = Field(None, alias="content-hash")

class PoetryLockConfig(BaseModel):
    metadata: PoetryLockMetadata
    packages: List[PoetryPackage]