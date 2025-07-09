import dataclasses
import functools
import itertools
import logging
from pathlib import Path
from poetry.core.constraints.version import Version
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.package import Package
from poetry.utils.wheel import Wheel
from typing import Iterable, List, Optional, Set, Union, Dict
import warnings

from deplock.exceptions import (
    MissingPythonEnvironmentError,
    MissingLockMetadataError,
    MissingPoetryLockFileError,
    StalePoetryLockFileError,
    IncompatibleDistributionError,
    PoetryPyprojectMissingPythonSpecError,
    InvalidLockFileError,
)
from deplock.types.environment import PythonEnvironment
from deplock.types.requirement import LocalPythonRequirement, PythonRequirement
from deplock.utils.markers import validate_python_version

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PoetryLock:
    def __init__(self, base_path: Union[str, Path, None] = None
                     , end_dir: Union[str, Path, None] = None
                     , dependency_groups: Optional[List[str]] = None
                     , extras: Optional[Iterable[str]] = None
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
                logger.debug("Value of base_path must be None, str, or pathlib.Path")

        match end_dir:
            case None:
                self.end_dir = self.base_path.parent
            case str():
                self.end_dir = Path(end_dir)
            case Path():
                self.end_dir = end_dir
            case _:  # Default case for any other value
                logger.debug("Value of end_dir must be None, str, or pathlib.Path")

        self._dependency_groups = list(set(["main"] + (dependency_groups or [])))
        self._extras = extras or []
        self.poetry_lock_path = self._search_tree_for_lock_file(poetry_lock_filename)
        self.data = self._parse_poetry_lock()
        self.python_target_env_spec = None
        self.poetry_lock_is_validated = False
        self.valid_package_dict = None
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
        raise MissingPoetryLockFileError(f"No `{poetry_lock_filename}` file found in directory tree.")
    
    def _parse_poetry_lock(self):
        """Parse the poetry.lock file.
        """
        # Use the Poetry API to parse the lock file
        from poetry.factory import Factory

        self.poetry = Factory().create_poetry(disable_plugins=True,
                                              cwd=self.poetry_lock_path)

        if not self.poetry.locker.is_locked():
            raise MissingPoetryLockFileError("Lock file does not exist. Run `poetry lock`.")
        if not self.poetry.locker.is_fresh():
            raise StalePoetryLockFileError("Lock file is not up to date. Run `poetry lock`.")

        self._packages = {
            PythonRequirement(
                package.name,
                str(package.version),
                fingerprint=None,
                index_url=package.source_url,
            ): package
            for package in self.poetry.locker.locked_repository().packages
        }
        return self._packages

        
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

        try:
            project_python_reqs = str(self.poetry.package.python_constraint)
        except AttributeError:
            raise PoetryPyprojectMissingPythonSpecError("The pyproject.toml in this "
                                                        "Poetry project does not "
                                                        "include a "
                                                        "'[tool.poetry.dependencies]"
                                                        "['python']' key.")

        # Check Python version compatibility
        valid_py_version = validate_python_version(
            specifier=project_python_reqs,
            current_version=self.python_target_env_spec.python_version
        )

        if not valid_py_version:
            raise InvalidLockFileError("Poetry lock file not compatible with target Python version")

        self.poetry_lock_is_validated = True
        return

    @functools.lru_cache(maxsize=1)
    def get_valid_packages_from_lock(self) -> Dict[str, Package]:
        """Get a list of packages from the lock file that are compatible with the target environment.
        
        Returns:
            List: A list of valid packages compatible with the target environment.

        Raises:
            MissingPythonEnvironmentError: If no target Python environment has been specified.
        """
        if self.python_target_env_spec is None:
            raise MissingPythonEnvironmentError("No Python environment specified")

        deps_for_extras = (
            deps
            for name, deps in self.poetry.package.extras.items()
            if name in self._extras
        )
        extra_dependencies = set(itertools.chain.from_iterable(deps_for_extras))

        root_package = self.poetry.package.with_dependency_groups(
            self._dependency_groups, only=True
        )
        dependencies = root_package.all_requires

        locked_repository = self.poetry.locker.locked_repository()

        incompatible_packages: Set[str] = set()
        installable_packages: Dict[str, Package] = {}
        seen: Dict[str, Dependency] = {}

        while dependencies:
            dependency = dependencies.pop()
            seen[dependency.name] = dependency

            # The same dependency, but with different constraints, could
            # have been added to the queue twice. We need to skip it
            # if it's already been chosen to be installed.
            if dependency.name in installable_packages:
                continue

            if not dependency.python_constraint.allows(
                Version.from_parts(
                    major=self.python_target_env_spec.major_python, minor=self.python_target_env_spec.minor_python
                )
            ):
                incompatible_packages.add(dependency.name)
                continue

            if not dependency.marker.validate(
                dataclasses.asdict(self.python_target_env_spec.environment_markers)
            ):
                incompatible_packages.add(dependency.name)
                continue

            """
            The locked repository will only contain one package per dependency
            since Poetry requires resolutions work out to a single version
            across all groups.
            """
            package = locked_repository.find_packages(dependency)[0]
            # It has been observed for conditional dependency specs:
            # torch = [
            #   {platform = "linux", version = "2.2.2+cu118", source = "pytorch-cu118"},
            #   {platform = "darwin", version = ">2.0", source = "artifactory"},
            # ]
            # A package is included in the locked repository with 0 files.
            # Avoid inferring such packages as installable in order to choose
            # the right package for the target
            if not package.files and package.source_type != "directory":
                continue

            if package.optional and dependency not in extra_dependencies:
                continue

            for dep in package.requires:
                if dep.name in installable_packages:
                    continue

                in_queue = any([str(d) == str(dep) for d in dependencies])
                if in_queue:
                    continue

                have_not_visited = str(dep) != seen.get(dep.name)
                if have_not_visited:
                    dependencies.append(dep)

            if package.name in incompatible_packages:
                incompatible_packages.remove(package.name)
            installable_packages[package.name] = package

        for incompatible_package in incompatible_packages:
            logger.warning(
                f"Dependency {incompatible_package} is not compatible with target "
                "environment. Ignoring."
            )
        self.valid_package_dict = installable_packages
        return self.valid_package_dict


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
        if not self.valid_package_dict:
            raise MissingLockMetadataError("Packages have not been validated against "
                                           "the current Python environment. Specify a "
                                           "target environment and validate lock file "
                                           "against this environment "
                                           "before continuing.")

        supported_tags = self.python_target_env_spec.supported_tags()
        self.package_requirements: List[PythonRequirement] = []

        for package_name, package in self.valid_package_dict.items():
            if package.source_type and package.source_type.lower() == "directory":
                if not package.source_url:
                    raise ValueError(
                        f"Package {package.name} has source type directory "
                        "but no source URL"
                    )
                self.package_requirements.append(
                    LocalPythonRequirement(
                        package_name,
                        str(package.version),
                        fingerprint=None,
                        index_url=None,
                        directory=Path(package.source_url),
                    )
                )
                continue

            distributions = package.files
            best_dist, min_tag_index = None, None

            binary_distributions = [
                dist for dist in distributions if dist["file"].endswith(".whl")
            ]
            is_platform_specific = any(
                [
                    dist
                    for dist in binary_distributions
                    if not dist["file"].endswith("none-any.whl")
                ]
            )
            for dist in distributions:
                filename = dist["file"]
                if filename.endswith(".whl"):
                    wheel = Wheel(filename)
                    matched_index = wheel.get_minimum_supported_index(
                        supported_tags
                    )
                    if matched_index is not None and (
                        not min_tag_index or matched_index < min_tag_index
                    ):
                        min_tag_index = matched_index
                        best_dist = dist
                elif (
                    not is_platform_specific
                    and filename.endswith(".tar.gz")
                    and not best_dist
                ):
                    best_dist = dist

            if not best_dist:
                raise IncompatibleDistributionError(
                    f"Could not find a distribution for "
                    f"{package_name}=={package.version} that is compatible with "
                    "target environment."
                )

            logger.debug(
                "Found compatible distribution for target "
                f"environment: {best_dist['file']}"
            )
            self.package_requirements.append(
                PythonRequirement(
                    package_name,
                    str(package.version),
                    fingerprint=best_dist["hash"],
                    index_url=package.source_url,
                )
            )
        return self.package_requirements