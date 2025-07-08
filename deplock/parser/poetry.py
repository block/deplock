import logging
from pathlib import Path
from poetry.utils.wheel import Wheel
from typing import List, Union, Dict, Optional
import warnings

from deplock.configs.poetry_lock import PoetryLockConfig
from deplock.exceptions import (
    MissingPythonEnvironmentError,
    MissingLockMetadataError,
    NoPoetryLockFileFoundError,
    IncompatibleDistributionError,
    InvalidLockVersionError,
    InvalidLockFileError,
)
from deplock.types.environment import PythonEnvironment
from deplock.types.requirement import PythonRequirement
from deplock.utils.markers import validate_python_version, check_markers

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PoetryLock:
    def __init__(self, base_path: Union[str, Path, None] = None
                     , end_dir: Union[str, Path, None] = None
                     , poetry_lock_filename: str = "poetry.lock"):
        """Initialize a PoetryLock object to parse and validate Poetry lock files.
        
        Args:
            base_path: The starting path to search for a poetry.lock file. Defaults to current directory.
            end_dir: The top-most directory to search up to. Defaults to base_path's parent.
            poetry_lock_filename: The name of the Poetry lock file. Defaults to "poetry.lock".
        """
        match base_path:
            case None:
                self.base_path = Path(".")
            case str():
                self.base_path = Path(base_path)
            case Path():
                self.base_path = base_path
            case _:  # Default case for any other value
                logger.debug(f"Value of base_path must be None, str, or pathlib.Path")

        match end_dir:
            case None:
                self.end_dir = self.base_path.parent
            case str():
                self.end_dir = Path(end_dir)
            case Path():
                self.end_dir = end_dir
            case _:  # Default case for any other value
                logger.debug(f"Value of end_dir must be None, str, or pathlib.Path")

        self.poetry_lock_path = self._search_tree_for_lock_file(poetry_lock_filename)
        self.data = self._parse_poetry_lock()
        self.python_target_env_spec = None
        self.poetry_lock_is_validated = False
        self.valid_package_list = None
        self.package_requirements = None
        
    def _search_tree_for_lock_file(self, poetry_lock_filename: str) -> Path:
        """Search for a poetry.lock file starting from base_path and working up to end_dir.
        
        Args:
            poetry_lock_filename: The name of the Poetry lock file to search for.
            
        Returns:
            Path: The path to the found poetry.lock file.
            
        Raises:
            NoPoetryLockFileFoundError: If no poetry.lock file is found in the directory tree.
        """
        current = Path(self.base_path).resolve()

        while True:
            poetry_lock_file_paths = list(current.glob(poetry_lock_filename))
            if poetry_lock_file_paths:
                assert len(poetry_lock_file_paths) == 1
                poetry_lock_file_path = poetry_lock_file_paths[0]
                return poetry_lock_file_path

            if current == current.parent:  # We've reached the root
                break

            if self.end_dir is not None and self.end_dir == current:
                break

            current = current.parent
        raise NoPoetryLockFileFoundError(f"No `{poetry_lock_filename}` file found in directory tree.")
    
    def _parse_poetry_lock(self):
        """Parse the poetry.lock file into a PoetryLockConfig object.
        
        Returns:
            PoetryLockConfig: A configuration object representing the parsed poetry.lock file.
        """
        # Use the Poetry API to parse the lock file
        from poetry.factory import Factory
        
        factory = Factory()
        poetry = factory.create_poetry(Path(self.poetry_lock_path.parent))
        
        if not poetry.locker.is_locked():
            raise NoPoetryLockFileFoundError("Poetry lock file does not exist.")
            
        # Convert to our internal format
        poetry_lock_config = PoetryLockConfig.model_validate({
            "metadata": {
                "lock_version": "2.0",  # Poetry standard lock version
                "python_versions": poetry.locker.lock_data.get("metadata", {}).get("python-versions", "")
            },
            "packages": [
                {
                    "name": package.name,
                    "version": str(package.version),
                    "category": package.category,
                    "optional": package.optional,
                    "python_versions": str(package.python_constraint) if package.python_constraint else None,
                    "files": [
                        {
                            "file": file["file"],
                            "hash": file["hash"]
                        } for file in package.files
                    ],
                    "source": {
                        "type": package.source_type,
                        "url": package.source_url,
                        "reference": package.source_reference
                    } if package.source_type else None,
                    "dependencies": [
                        {
                            "name": dep.name,
                            "constraint": str(dep.constraint) if dep.constraint else None,
                            "optional": dep.is_optional(),
                            "python_versions": str(dep.python_constraint) if dep.python_constraint else None,
                            "marker": str(dep.marker) if dep.marker else None
                        } for dep in package.requires
                    ]
                } for package in poetry.locker.locked_repository().packages
            ]
        })
        
        return poetry_lock_config
        
    def add_target_environment_specification(self,
                                             python_environment: PythonEnvironment):
        """Add a PythonEnvironment which will be used to check the compatibility
        of the lock file and the packages in the lock file.
        
        Args:
            python_environment: The target Python environment to validate against.
        """
        if self.python_target_env_spec is not None:
            warnings.warn("Environment specification has already been set and will "
                          "be overwritten.")
        self.python_target_env_spec = python_environment
    
    def validate_poetry_lock(self):
        """Validate that the poetry.lock is compatible with the target Python environment.
        If the lock file does not have a requires-python or environment tag, it will
        be assumed to be compatible with the target Python environment.
        
        Raises:
            MissingPythonEnvironmentError: If no target Python environment has been specified.
            InvalidLockVersionError: If the lock file version is not supported.
            InvalidLockFileError: If the lock file is not compatible with the target environment.
        """
        if self.python_target_env_spec is None:
            raise MissingPythonEnvironmentError("No Python environment specified")
        
        # Check lock file version
        if not self.data.metadata.lock_version.startswith("2."):
            raise InvalidLockVersionError
            
        # Check Python version compatibility
        if self.data.metadata.python_versions:
            valid_py_version = validate_python_version(
                specifier=self.data.metadata.python_versions,
                current_version=self.python_target_env_spec.python_version
            )
        else:
            valid_py_version = True
            
        if not valid_py_version:
            raise InvalidLockFileError("Poetry lock file not compatible with target Python version")
            
        self.poetry_lock_is_validated = True
        
    def get_valid_packages_from_lock(self) -> List:
        """Get a list of packages from the lock file that are compatible with the target environment.
        
        Returns:
            List: A list of valid packages compatible with the target environment.
            
        Raises:
            MissingPythonEnvironmentError: If no target Python environment has been specified.
        """
        if self.python_target_env_spec is None:
            raise MissingPythonEnvironmentError("No Python environment specified")
            
        self.valid_package_list = []
        
        for package in self.data.packages:
            if package.python_versions:
                valid_py_version = validate_python_version(
                    specifier=package.python_versions,
                    current_version=self.python_target_env_spec.python_version
                )
            else:
                valid_py_version = True
                
            # Check for any marker conditions (platform, os, etc.)
            if not valid_py_version:
                logger.debug(f"Package {package.name} is not compatible with "
                             f"the target Python version "
                             f"{self.python_target_env_spec.python_version}.")
                continue
                
            self.valid_package_list.append(package)
            
        return self.valid_package_list
        
    def get_preferred_distributions(self) -> List[PythonRequirement]:
        """For each package, return the preferred distribution according
        to the following logic:
            * if there is a compatible .whl:
                * use the minimum matching version
                * fall back to a built distribution (.tar.gz) if no
                match is found and a non platform specific distribution exists
                
        Returns:
            List[PythonRequirement]: A list of Python requirements with preferred distributions.
            
        Raises:
            MissingLockMetadataError: If packages have not been validated against the target environment.
            IncompatibleDistributionError: If a compatible distribution cannot be found for a package.
        """
        if not self.valid_package_list:
            raise MissingLockMetadataError("Packages have not been validated against "
                                           "the current Python environment. Specify a "
                                           "target environment and validate lock file "
                                           "against this environment "
                                           "before continuing.")
        
        self.package_requirements = []
        supported_tags = self.python_target_env_spec.supported_tags()
        
        for package in self.valid_package_list:
            distributions = [
                file for file in package.files
            ]
            
            best_dist, min_tag_index = None, None
            
            binary_distributions = [
                dist for dist in distributions if dist.file.endswith(".whl")
            ]
            is_platform_specific = any(
                [
                    dist
                    for dist in binary_distributions
                    if not dist.file.endswith("none-any.whl")
                ]
            )
            
            for dist in distributions:
                filename = dist.file
                if filename.endswith(".whl"):
                    wheel = Wheel(filename)
                    matched_index = wheel.get_minimum_supported_index(supported_tags)
                    if matched_index is not None and (
                        min_tag_index is None or matched_index < min_tag_index
                    ):
                        min_tag_index = matched_index
                        best_dist = dist
                
                # For standard distribution (.tar.gz)
                elif (
                    not is_platform_specific
                    and filename.endswith(".tar.gz")
                    and not best_dist
                ):
                    best_dist = dist
            
            if not best_dist:
                raise IncompatibleDistributionError(
                    f"Could not find a distribution for "
                    f"{package.name}=={package.version} that is compatible with "
                    "target environment."
                )
                
            logger.debug(
                "Found compatible distribution for target "
                f"environment: {best_dist.file}"
            )
            
            # Get the source URL from the package
            source_url = None
            if package.source and package.source.url:
                source_url = package.source.url
            
            self.package_requirements.append(
                PythonRequirement(
                    package.name,
                    str(package.version),
                    fingerprint=best_dist.hash,
                    index_url=source_url
                )
            )
            
        return self.package_requirements