import warnings
from pathlib import Path
from poetry.utils.wheel import Wheel
import tomlkit
from typing import List, Union, Dict
import logging

from deplock.configs.base import  PylockConfig
from deplock.configs.packages import Package
from deplock.exceptions import (
    MissingPythonEnvironmentError,
    MissingLockMetadataError,
    InvalidLockVersionError,
    InvalidLockFileError,
    IncompatibleDistributionError,
)
from deplock.types.environment import PythonEnvironment
from deplock.types.requirement import PythonRequirement
from deplock.utils.markers import validate_python_version, check_markers


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PyLock:
    def __init__(self, base_path: Union[str, Path, None] = None
                     , end_dir: Union[str, Path, None] = None
                     , package_name: Union[str, None] = None ):
        """
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

        self.package_name = package_name
        self.python_target_env_spec = None
        self.lock_data = []
        self.data = None
        # find all pylock*.toml files in path
        self.pylock_file_paths = self._search_tree_for_lock_file()
        # sort the pylock files giving preference to any pylock that contains
        # the service name
        self.sorted_pylock_file_paths = self._sort_pylock_list()
        # parse the lock files into Pydantic models
        self._parse_pylock_list()
        self.pylock_toml_is_validated = False
        self.valid_package_list = None
        self.package_requirements = None

    def _search_tree_for_lock_file(self) -> List[Path]:
        current = Path(self.base_path).resolve()
        pylock_file_paths = []

        while True:
            pylock_matches = current.glob("pylock.*toml")
            if pylock_matches:
                pylock_file_paths.extend([i for i in pylock_matches if i != []])

            if current == current.parent:  # We've reached the root
                break

            if self.end_dir is not None and self.end_dir == current:
                break

            current = current.parent

        return pylock_file_paths

    def _sort_pylock_list(self):
        """From PEP 751, detailing the preference on lock files.
        The expectation is that services that automatically install from lock files will search for:
                * The lock file with the service’s name and doing the default install
                * A multi-use pylock.toml with a dependency group with the name of the service
                * The default install of pylock.toml"""
        sorted_pylock_file_list = []
        for lock_file_path in self.pylock_file_paths:
            lock_file_name = lock_file_path.name
            if (
                len(lock_file_name) > 11
                and lock_file_name.startswith("pylock.")
                and lock_file_name.endswith(".toml")
            ):
                name = lock_file_name.removeprefix("pylock.").removesuffix(".toml")
                if name == self.package_name:
                    sorted_pylock_file_list.insert(0, lock_file_path)
                    return sorted_pylock_file_list[0]
            else:
                sorted_pylock_file_list.append(lock_file_path)
        return sorted_pylock_file_list


    def add_target_environment_specification(self,
                                             python_environment: PythonEnvironment):
        """Add a PythonEnvironment which will be used to check the compatibility
        of the lock file and the packages in the lock file."""
        if self.python_target_env_spec is not None:
            warnings.warn("Environment specification has already been set and will"
                          "be overwritten.")
        self.python_target_env_spec = python_environment

    def _parse_pylock_list(self):
        for pylock_file_path in self.sorted_pylock_file_paths:
            parsed_toml = self._parse_pylock_toml(pylock_file_path)
            pylock_config = PylockConfig.model_validate(parsed_toml)
            self.lock_data.append(pylock_config)
        # use the data from the lock file at position 0
        self.data = self.lock_data[0]

    @staticmethod
    def _parse_pylock_toml(pylock_toml_path: Path) -> Dict[str, str]:
        with pylock_toml_path.open("r") as toml_file:
            toml_content = toml_file.read()
            toml_doc = tomlkit.parse(toml_content)
        return toml_doc

    def validate_pylock_toml(self):
        """Validate that the pylock toml is compatible with the current Python version.
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

        self.pylock_toml_is_validated = True

    def get_valid_packages_from_lock(self) -> List[Package]:
        # reset self.valid_package_list to clear out anything currently included
        self.valid_package_list = []
        if self.python_target_env_spec is None:
            raise MissingPythonEnvironmentError("Cannot apply environment filters "
                                                "without environment marker specified")

        for package in self.data.packages:
            if package.marker:
                valid_environment = check_markers(
                    markers=package.markers,
                    environment=self.python_target_env_spec,
                )
            else:
                valid_environment = True
            if package.requires_python:
                valid_py_version = validate_python_version(
                    specifier=package.requires_python,
                    current_version=self.python_target_env_spec.python_version,
                )
            else:
                valid_py_version = True

            if not valid_environment and not valid_py_version:
                logger.debug(f"Package {package.name} is not compatible with"
                             f" the current Python version "
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
            distributions = [
                *(package.wheels_info or []),
                *(package.sdist_info or []),
                *(package.vcs_info or []),
                *(package.directory_info or []),
                *(package.archive_info or []),
            ]
            best_dist, min_tag_index = None, None

            binary_distributions = [
                dist for dist in distributions if dist.name.endswith(".whl")
            ]
            is_platform_specific = any(
                [
                    dist
                    for dist in binary_distributions
                    if not dist.name.endswith("none-any.whl")
                ]
            )
            for dist in distributions:
                filename = dist.name
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
                f"environment: {best_dist.name}"
            )

            self.package_requirements.append(
                PythonRequirement(
                    package.name,
                    str(package.version),
                    fingerprint=best_dist.hashes,
                    index_url=package.url,
                )
            )
        return self.package_requirements