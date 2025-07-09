import logging
from pathlib import Path
from poetry.utils.wheel import Wheel
import tomlkit
from typing import List, Set, Tuple, Union
import warnings

from deplock.configs.uv_lock import UVLockConfig, UVPackage
from deplock.exceptions import (
    MissingPythonEnvironmentError,
    MissingLockMetadataError,
    NoUVLockFileFoundError,
    IncompatibleDistributionError,
    InvalidLockVersionError,
    InvalidLockFileError,
)
from deplock.types.environment import PythonEnvironment
from deplock.types.requirement import PythonRequirement
from deplock.utils.markers import validate_python_version, check_markers

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class UVLock:
    def __init__(self, base_path: Union[str, Path, None] = None
                     , end_dir: Union[str, Path, None] = None
                     , uv_lock_filename: str = "uv.lock"):

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

        self.uv_lock_path = self._search_tree_for_lock_file(uv_lock_filename)
        self.data = self._parse_uv_lock()
        self.python_target_env_spec = None
        self.uv_lock_is_validated = False
        self.valid_package_list = None
        self.package_requirements = None

    def _search_tree_for_lock_file(self, uv_lock_filename: str) -> Path:
        current = Path(self.base_path).resolve()

        while True:
            uv_lock_file_paths = list(current.glob(uv_lock_filename))
            if uv_lock_file_paths:
                assert len(uv_lock_file_paths) == 1
                uv_lock_file_path = uv_lock_file_paths[0]
                return uv_lock_file_path

            if current == current.parent:  # We've reached the root
                break

            if self.end_dir is not None and self.end_dir == current:
                break

            current = current.parent
        raise NoUVLockFileFoundError("No `uv.lock` file found in directory tree.")


    def _parse_uv_lock(self):
        with self.uv_lock_path.open("r") as uv_lock_file:
            toml_content = uv_lock_file.read()
            parsed_toml = tomlkit.parse(toml_content)
        uv_lock_config = UVLockConfig.model_validate(parsed_toml)
        return uv_lock_config

    def add_target_environment_specification(self,
                                             python_environment: PythonEnvironment):
        """Add a PythonEnvironment which will be used to check the compatibility
        of the lock file and the packages in the lock file."""
        if self.python_target_env_spec is not None:
            warnings.warn("Environment specification has already been set and will"
                          "be overwritten.")
        self.python_target_env_spec = python_environment

    def validate_uv_lock(self):
        """Validate that the uv.lock is compatible with the current Python version.
            If the lock file does not have a requires-python or environment tag, it will
            be assumed to be compatible with the current Python version.
        """
        if self.python_target_env_spec is None:
            raise MissingPythonEnvironmentError("No Python environment specified")

        # sequentially check the validity of the lock file vs. the current env
        if self.data.lock_version != "1.0":
            raise InvalidLockVersionError
        if self.data.environments:
            valid_environment = check_markers(markers=self.data.environments, environment=self.python_target_env_spec)
        else:
            valid_environment = True
        if self.data.requires_python:
            valid_py_version = validate_python_version(specifier=self.data.requires_python,
                                    current_version=self.python_target_env_spec.python_version)
        else:
            valid_py_version = True

        if not valid_environment and not valid_py_version:
            raise InvalidLockFileError

        self.uv_lock_is_validated = True

    def get_valid_packages_from_lock(self):
        base_package_list = []
        base_required_dependency_set = set()
        base_skipped_dependency_set = set()
        for package in self.data.package:
            (base_package,
                required_dependency_set,
                skipped_dependency_set,
            ) = self._check_single_package(package)
            if base_package is None:
                continue
            base_package_list.append(base_package)
            base_required_dependency_set.update(required_dependency_set)
            base_skipped_dependency_set.update(skipped_dependency_set)

        # if the package is in both sets, it is required
        package_intersection = base_required_dependency_set.intersection(base_skipped_dependency_set)
        # add back any packages only in the `required_dependency_set`
        package_intersection.update(base_required_dependency_set)

        self.valid_package_list = []
        for package in base_package_list:
            if package.name in package_intersection:
                self.valid_package_list.append(package)
        return self.valid_package_list


    def _check_single_package(self, package: UVPackage) -> (
            Tuple[UVPackage, Set[str], Set[str]] | Tuple[None, None, None]):
        """
                # keep all directly specified packages if they are not removed
        # due to non-valid resolution markers
        """
        if self.python_target_env_spec is None:
            raise MissingPythonEnvironmentError("No Python environment specified")

        if package.resolution_markers:
            if not check_markers(markers=package.resolution_markers,
                                 environment=self.python_target_env_spec):
                return None, None, None

        required_dependencies = set()
        skipped_dependencies = set()
        if package.dependencies:
            for dep in package.dependencies:
                dep_name = dep['name']
                if "marker" in dep:
                    if check_markers(markers=dep["marker"],
                                     environment=self.python_target_env_spec):
                        required_dependencies.add(dep_name)
                    else:
                        skipped_dependencies.add(dep_name)
                else:
                    required_dependencies.add(dep_name)

        return package, required_dependencies, skipped_dependencies

    def get_preferred_distributions(self) -> List[PythonRequirement]:
        """For each package, return the preferred distribution according
        to the following logic:
            * if there is a compatible .whl:
                * use the minimum matching version
                * fall back to a built distribution (.tar.gz) if no
                match is found and a non platform specific distribution exists
        By default, the list of valid packages will be used, but all packages
        will be used in valid packages is not set."""
        if not self.valid_package_list:
            raise MissingLockMetadataError("Packages have not been validated against "
                                           "the current Python environment. Specify a "
                                           "target environment and validate lock file "
                                           "against this environment "
                                           "before continuing.")

        self.package_requirements = []
        supported_tags = self.python_target_env_spec.supported_tags()

        for package in self.valid_package_list:
            distributions = [*(package.wheels or [])]
            if package.sdist:
                distributions.append(package.sdist)

            best_dist, min_tag_index = None, None

            binary_distributions = [
                dist for dist in distributions if dist.dist_name.endswith(".whl")
            ]
            is_platform_specific = any(
                [
                    dist
                    for dist in binary_distributions
                    if not dist.dist_name.endswith("none-any.whl")
                ]
            )
            for dist in distributions:
                filename = dist.dist_name
                if filename.endswith(".whl"):
                    # Wheel is from the Poetry API, but is not Poetry specific and can
                    # generically parse .whl file names
                    wheel = Wheel(filename)
                    matched_index = wheel.get_minimum_supported_index(supported_tags)
                    if matched_index is not None and (
                        min_tag_index is None or matched_index < min_tag_index
                    ):
                        min_tag_index = matched_index
                        best_dist = dist

                # a `*.tar.gz` standard distribution can be used as the best_dist if:
                #     * the package has a not platform specific option (at least one
                #        `*none-any.whl` wheel)
                #     * there is a standard distribution with extension `.tar.gz`
                #     * no better option exists (best_dist is None)
                # if any of these are False, the `*.tar.gz` cannot be used
                # as the `best_dist`
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
                f"environment: {best_dist.dist_name}"
            )

            self.package_requirements.append(
                PythonRequirement(
                    package.name,
                    str(package.version),
                    fingerprint=best_dist.hash,
                    index_url=package.source_url,
                )
            )
        return self.package_requirements